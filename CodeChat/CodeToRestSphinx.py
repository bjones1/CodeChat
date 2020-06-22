# .. Copyright (C) 2012-2020 Bryan A. Jones.
#
#    This file is part of CodeChat.
#
#    CodeChat is free software: you can redistribute it and/or modify it under
#    the terms of the GNU General Public License as published by the Free
#    Software Foundation, either version 3 of the License, or (at your option)
#    any later version.
#
#    CodeChat is distributed in the hope that it will be useful, but WITHOUT ANY
#    WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#    FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#    details.
#
#    You should have received a copy of the GNU General Public License along
#    with CodeChat.  If not, see <http://www.gnu.org/licenses/>.
#
# ***************************************************************
# |docname| - a Sphinx extension to translate source code to reST
# ***************************************************************
# This modules enables Sphinx to read in source files by converting the source
# code to reST before passing the file on to Sphinx. The overall design:
#
# 1. Monkeypatch_ Sphinx to include source files in the build, keeping the
#    source file's extension intact. (Sphinx strips the extension of reST
#    files).
# 2. When Sphinx `reads a source file <source-read event>`_, check to see if the
#    file's extension is intact. If so, it's a source file; translate it to reST
#    then pass it on to Sphinx.
#
# .. contents::
#
# Imports
# =======
# These are listed in the order prescribed by `PEP 8
# <http://www.python.org/dev/peps/pep-0008/#imports>`_.
#
# Standard library
# ----------------
import os
from pathlib import Path
from typing import Dict

# Third-party imports
# -------------------
import sphinx
import sphinx.util
import sphinx.project
from sphinx.util import path_stabilize
from sphinx.util.osutil import SEP, relpath
import sphinx.io

# The exception ``FiletypeNotFoundError`` was `deprecated in Sphinx v2.4.0 <https://www.sphinx-doc.org/en/master/extdev/deprecated.html>`_ by moving it from ``sphinx.io`` to ``sphinx.errors``.
if sphinx.version_info[:3] >= (2, 4, 0):
    from sphinx.errors import FiletypeNotFoundError
else:
    from sphinx.io import FiletypeNotFoundError
import pygments.util

# Local application imports
# -------------------------
from .CodeToRest import code_to_rest_string, get_lexer, add_highlight_language
from .CodeToMarkdown import code_to_markdown_string
from .CommentDelimiterInfo import SUPPORTED_GLOBS
from . import __version__


# source-read event
# =================
# Create a logger for issuing warnings during the build process.
logger = sphinx.util.logging.getLogger(__name__)


# The source-read_ event occurs when a source file is read. If it's code, this
# routine changes it into reST or Markdown.
def _source_read(
    # _`app`: The `Sphinx application object <http://sphinx-doc.org/extdev/appapi.html#sphinx.application.Sphinx>`_.
    app,
    # _`docname`: The name of the document that was read. It contains a path
    # relative to the project directory and (typically) no extension.
    docname,
    # A list whose single element is the contents of the source file.
    source,
):

    if is_source_code(app.env, docname):
        # See if it's an extension we should process.
        try:
            # See if ``source_file`` matches any of the globs.
            lexer = None
            lfg = app.config.CodeChat_lexer_for_glob
            path_docname = Path(docname)
            for glob, lexer_alias in lfg.items():
                if path_docname.match(glob):
                    # On a match, pass the specified lexer alias.
                    lexer = get_lexer(alias=lexer_alias)
                    break
            # Do this after checking the ``CodeChat_lexer_for_glob`` list, since
            # this will raise an exception on failure.
            lexer = lexer or get_lexer(filename=docname, code=source[0])

            # Translate code to reST or Markdown.
            if is_markdown_docname(app.config, docname):
                source[0] = code_to_markdown_string(source[0], lexer=lexer)
                markup = "Markdown"
            else:
                source[0] = code_to_rest_string(source[0], lexer=lexer)
                source[0] = add_highlight_language(source[0], lexer)
                markup = "reST"
            logger.info(
                "Converted as {} using the {} lexer.".format(markup, lexer.name)
            )

        except (KeyError, pygments.util.ClassNotFound) as e:
            # We don't support this language.
            logger.warning(
                "Unsupported source code language: " + str(e), location=docname
            )


# Return True if the supplied ``docname`` is source code.
def is_source_code(
    # The `Sphinx build environment <http://www.sphinx-doc.org/en/1.5.1/extdev/envapi.html>`_.
    env,
    # See docname_.
    docname,
):

    # If the docname's extension doesn't change when asking for its full path,
    # then it's source code. Normally, the docname of ``foo.rst`` is ``foo``;
    # only for source code is the docname of ``foo.c`` also ``foo.c``. Look up
    # the name and extension using `doc2path
    # <http://sphinx-doc.org/extdev/envapi.html#sphinx.environment.BuildEnvironment.doc2path>`_.
    docname_ext = env.doc2path(docname, None)
    return Path(docname_ext) == Path(docname)


# Return True if the supplied ``docname`` is Markdown; False means reST.
def is_markdown_docname(
    # The Sphinx config object.
    config,
    # See docname_.
    docname,
):
    # Get the second extension: given a file named ``a.foo.bar``, produce ``[".foo"]``; given ``a.bar``, produce ``[]``.
    docname_suffixes = Path(docname).suffixes
    # See if this is a recognized Markdown extension.
    return (
        len(docname_suffixes) > 1
        and config.source_suffix.get(docname_suffixes[-2]) == "markdown"
    )


# Monkeypatch
# ===========
# Sphinx doesn't naturally look for source files. Simply adding all supported
# source file extensions to ``conf.py``'s `source_suffix <http://sphinx-doc.org/config.html#confval-source_suffix>`_
# doesn't work, since ``foo.c`` and ``foo.h`` will now both been seen as the
# docname ``foo``, making then indistinguishable. See also my `post on
# sphinx-users <https://groups.google.com/d/msg/sphinx-users/CH8FW-tK1T0/_IHuAUW5GQAJ>`_.
#
# path2doc patch
# --------------
# For source files, make their docname the same as the file name; for reST
# files, allow Sphinx to strip off the extension as before. This patch
# accomplishes this. It comes from ``sphinx.project.Project``, line 46 and
# following in Sphinx 2.0.1.
def _path2doc(self, filename):
    # type: (str) -> str
    """Return the docname for the filename if the file is document.

    *filename* should be absolute or relative to the source directory.
    """
    if filename.startswith(self.srcdir):
        filename = relpath(filename, self.srcdir)
    for suffix in self.source_suffix:
        if filename.endswith(suffix):
            if sphinx.version_info[:3] >= (2, 3, 0):
                # This line was added in https://github.com/sphinx-doc/sphinx/commit/155f4b0d00e72d16eed47581f2fee75e41c452cf, starting in v2.3.0. It's a patch to fix https://github.com/sphinx-doc/sphinx/issues/6813.
                filename = path_stabilize(filename)
            return filename[: -len(suffix)]

    # The following code was added.
    if is_supported_language(filename):
        return filename

    # This was the existing code.
    # the file does not have docname
    return None


sphinx.project.Project.path2doc = _path2doc


# Return True if the provided filename is a source code language CodeChat supports.
def is_supported_language(filename):
    # type: (str) -> bool
    source_suffixpatterns = SUPPORTED_GLOBS | set(
        _config.CodeChat_lexer_for_glob.keys()
    )
    path_filename = Path(filename)
    for source_suffixpattern in source_suffixpatterns:
        if path_filename.match(source_suffixpattern):
            return True
    return False


# doc2path patch
# --------------
# Next, the way docnames get transformed back to a full path needs to be fixed
# for source files. Specifically, a docname might be the source file, without
# adding an extension. This code comes from ``sphinx.project.Project`` of Sphinx
# 2.0.1.
def _doc2path(self, docname, basedir=True):
    # type: (str, bool) -> str
    """Return the filename for the document name.

    If *basedir* is True, return as an absolute path.
    Else, return as a relative path to the source directory.
    """
    docname = docname.replace(SEP, os.path.sep)
    basename = os.path.join(self.srcdir, docname)
    for suffix in self.source_suffix:
        if os.path.isfile(basename + suffix):
            break
    else:
        # Three lines of code added here -- check for the no-extension case.
        if os.path.isfile(os.path.join(self.srcdir, docname)):
            suffix = ""
        else:
            # document does not exist
            suffix = list(self.source_suffix)[0]

    if basedir:
        return basename + suffix
    else:
        return docname + suffix


sphinx.project.Project.doc2path = _doc2path


# get_filetype patch
# ------------------
# The ``get_filetype`` function raises an exception if it can't determine the type of a file. Patch it to also recognize source code as reST. This was taken from ``sphinx.util``, version 2.4.0.
def _get_filetype(source_suffix: Dict[str, str], filename: str) -> str:
    for suffix, filetype in source_suffix.items():
        if filename.endswith(suffix):
            # If default filetype (None), considered as restructuredtext.
            return filetype or "restructuredtext"
    else:
        # The following code was added.
        if is_supported_language(filename):
            return (
                "markdown"
                if is_markdown_docname(_config, filename)
                else "restructuredtext"
            )
        # This was the existing code.
        raise FiletypeNotFoundError


# The function ``sphinx.io.get_filetype`` was `deprecated in Sphinx v2.4.0`_ by moving it to ``sphinx.util.get_filetype``.
if sphinx.version_info[:3] >= (2, 4, 0):
    # Sphinx uses ``sphinx.deprecation._ModuleWrapper`` to perform deprecation. In ``sphinx.io``, we need to monkeypatch inside it, hence the ``_module`` (a member of the ``_ModuleWrapper``).
    sphinx.io._module.get_filetype = _get_filetype
    sphinx.util.get_filetype = _get_filetype
else:
    sphinx.io.get_filetype = _get_filetype


# Correct naming for the "show source" option
# ===========================================
# The following function corrects the extension of source files in the
# "source" link. By default, Sphinx (in ``sphinx.builders.html.StandaloneHTMLBuilder.get_doc_context``)
# creates a sourcename by appending a file's extension to the value returned by
# ``doc2path``. For non-source files, ``doc2path``'s return value contains no
# extension, so this works fine. However, for source files, ``doc2path``'s
# return value contains an extension, so that appending the extension to source
# files produces a doubled extension -- ``.py.py``, for example.
def _html_page_context(
    # See app_.
    app,
    # The canonical name of the page being rendered, that is, without the
    # ``.html`` suffix and using slashes as path separators.
    pagename,
    # The name of the template to render; this will be 'page.html' for all pages
    # from reST documents.
    templatename,
    # A dictionary of values that are given to the template engine to render the
    # page and can be modified to include custom values. Keys must be strings.
    context,
    # A doctree when the page is created from a reST documents; None when the
    # page is created from an HTML template alone.
    doctree,
):

    sourcename = context.get("sourcename")
    ext = Path(pagename).suffix
    # The extension Sphinx uses optionally includes the `html_sourcelink_suffix <http://www.sphinx-doc.org/en/stable/config.html#confval-html_sourcelink_suffix>`_.
    sphinx_ext = ext + (
        ""
        if ext == app.config.html_sourcelink_suffix
        else app.config.html_sourcelink_suffix
    )
    double_ext = ext + sphinx_ext
    # Only provide the rename if necessary.
    if sourcename and ext and sourcename.endswith(double_ext):
        # Take off the second of the double extensions.
        context["sourcename"] = sourcename[: -len(double_ext)] + sphinx_ext


# Extension setup
# ===============
# This routine defines the `entry point
# <http://sphinx-doc.org/extdev/appapi.html>`_ called by Sphinx to initialize
# this extension.
def setup(
    # See app_.
    app,
):

    # Ensure we're using a new enough Sphinx using `require_sphinx
    # <http://sphinx-doc.org/extdev/appapi.html#sphinx.application.Sphinx.require_sphinx>`_.
    app.require_sphinx("2.0")

    # Use the `source-read <http://sphinx-doc.org/extdev/appapi.html#event-source-read>`_
    # event hook to transform source code to reST before Sphinx processes it.
    app.connect("source-read", _source_read)

    # Add the CodeChat.css style sheet using `add_css_file
    # <http://www.sphinx-doc.org/en/master/extdev/appapi.html#sphinx.application.Sphinx.add_css_file>`_.
    app.add_css_file("CodeChat.css")

    # Add the `CodeChat_lexer_for_glob <CodeChat_lexer_for_glob>` config value. See `add_config_value
    # <http://sphinx-doc.org/extdev/appapi.html#sphinx.application.Sphinx.add_config_value>`_.
    app.add_config_value("CodeChat_lexer_for_glob", {}, "html")

    # Use the `html-page-context <http://www.sphinx-doc.org/en/stable/extdev/appapi.html#event-html-page-context>`_
    # event to correct the extension of source files.
    app.connect("html-page-context", _html_page_context)

    # .. _global_config:
    #
    # An ugly hack: we need to get to the `Config <http://sphinx-doc.org/extdev/appapi.html#sphinx.config.Config>`_
    # object after ``conf.py``'s values have been loaded. They aren't loaded
    # yet, so we store the ``config`` object to access it later when it is
    # loaded.
    global _config
    _config = app.config

    # Return `extension metadata <http://sphinx-doc.org/extdev/index.html>`_.
    return {"version": __version__, "parallel_read_safe": True}
