# .. Copyright (C) 2012-2018 Bryan A. Jones.
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
from os import path
import fnmatch
import codecs
from pathlib import Path

# Third-party imports
# -------------------
from six import iteritems
from sphinx.util import get_matching_files
from sphinx.util.matching import compile_matchers
import sphinx.environment
from sphinx.util.osutil import SEP
# The location of this class varies with the Sphinx version. It's only needed for Sphinx 1.8.0+.
try:
    from sphinx.io import FiletypeNotFoundError
except ImportError:
    FiletypeNotFoundError = None
import pygments.util

# Local application imports
# -------------------------
from .CodeToRest import code_to_rest_string, get_lexer, add_highlight_language
from .CommentDelimiterInfo import SUPPORTED_GLOBS
from . import __version__


# source-read event
# =================
# The source-read_ event occurs when a source file is read. If it's code, this
# routine changes it into reST.
def _source_read(
    # _`app`: The `Sphinx application object <http://sphinx-doc.org/extdev/appapi.html#sphinx.application.Sphinx>`_.
    app,
    # _`docname`: The name of the document that was read. It contains a path
    # relative to the project directory and (typically) no extension.
    docname,
    # A list whose single element is the contents of the source file.
    source):

    if is_source_code(app.env, docname):
        # See if it's an extension we should process.
        try:
            # See if ``source_file`` matches any of the globs.
            lexer = None
            lfg = app.config.CodeChat_lexer_for_glob
            for glob, lexer_alias in lfg.items():
                if Path(docname).match(glob):
                    # On a match, pass the specified lexer alias.
                    lexer = get_lexer(alias=lexer_alias)
                    break
            # Do this after checking the CodeChat_lexer_for_glob list, since
            # this will raise an exception on failure.
            lexer = lexer or get_lexer(filename=docname, code=source[0])

            # Translate code to reST.
            app.info('Converted using the {} lexer.'.format(lexer.name))
            source[0] = code_to_rest_string(source[0], lexer=lexer)
            source[0] = add_highlight_language(source[0], lexer)

        except (KeyError, pygments.util.ClassNotFound) as e:
            # We don't support this language.
            app.warn(e, docname)


# Return True if the supplied docname is source code.
def is_source_code(
    # The `Sphinx build environament <http://www.sphinx-doc.org/en/1.5.1/extdev/envapi.html>`_.
    env,
    # See docname_.
    docname):

    # If the docname's extension doesn't change when asking for its full path,
    # then it's source code. Normally, the docname of ``foo.rst`` is ``foo``;
    # only for source code is the docname of ``foo.c`` also ``foo.c``. Look up
    # the name and extension using `doc2path
    # <http://sphinx-doc.org/extdev/envapi.html#sphinx.environment.BuildEnvironment.doc2path>`_.
    docname_ext = env.doc2path(docname, None)
    return Path(docname_ext) == Path(docname)


# Monkeypatch
# ===========
# Sphinx doesn't naturally look for source files. Simply adding all supported
# source file extensions to ``conf.py``'s `source_suffix <http://sphinx-doc.org/config.html#confval-source_suffix>`_
# doesn't work, since ``foo.c`` and ``foo.h`` will now both been seen as the
# docname ``foo``, making then indistinguishable.
#
# get_matching_docs patch
# -----------------------
# So, do a bit of monkeypatching: for source files, make their docname the same
# as the file name; for reST file, allow Sphinx to strip off the extension as
# before. The first patch accomplishes this. It comes from ``sphinx.util``, line
# 92 and following in Sphinx 1.3.1.
def _get_matching_docs(dirname, suffixes, exclude_matchers=()):
    """Get all file names (without suffixes) matching a suffix in a directory,
    recursively.

    Exclude files and dirs matching a pattern in *exclude_patterns*.
    """
    suffixpatterns = ['*' + s for s in suffixes]
    # The following two lines were added.
    source_suffixpatterns = ( SUPPORTED_GLOBS |
                             set(_config.CodeChat_lexer_for_glob.keys()) )
    exclude_matchers += compile_matchers(_config.CodeChat_excludes)
    for filename in get_matching_files(dirname, exclude_matchers):
        for suffixpattern in suffixpatterns:
            if fnmatch.fnmatch(filename, suffixpattern):
                yield filename[:-len(suffixpattern)+1]
                break
        # The following code was added.
        for source_suffixpattern in source_suffixpatterns:
            if Path(filename).match(source_suffixpattern):
                yield filename
                break


# Note that this is referenced in ``sphinx.environment`` by ``from sphinx.util
# import get_matching_docs``. So, `where to patch <https://docs.python.org/dev/library/unittest.mock.html#where-to-patch>`_
# is in ``sphinx.environment`` instead of ``sphinx.util``.
sphinx.environment.get_matching_docs = _get_matching_docs


# doc2path patch
# --------------
# Next, the way docnames get transformed back to a full path needs to be fixed
# for source files. Specifically, a docname might be the source file, without
# adding an extension. This code comes from ``sphinx.environment`` of Sphinx
# 1.8.1. See also the official `doc2path <http://sphinx-doc.org/extdev/envapi.html#sphinx.environment.BuildEnvironment.doc2path>`_
# Sphinx docs.
def _doc2path(self, docname, base=True, suffix=None):
    """Return the filename for the document name.

    If *base* is True, return absolute path under self.srcdir.
    If *base* is None, return relative path to self.srcdir.
    If *base* is a path string, return absolute path under that.
    If *suffix* is not None, add it instead of config.source_suffix.
    """
    docname = docname.replace(SEP, path.sep)
    if suffix is None:
        # Use first candidate if there is not a file for any suffix
        suffix = next(iter(self.config.source_suffix))
        for candidate_suffix in self.config.source_suffix:
            if path.isfile(path.join(self.srcdir, docname) +
                           candidate_suffix):
                suffix = candidate_suffix
                break
        else:
            # Two lines of code added here -- check for the no-extenion case.
            if path.isfile(path.join(self.srcdir, docname)):
                suffix = ''
    if base is True:
        return path.join(self.srcdir, docname) + suffix
    elif base is None:
        return docname + suffix
    else:
        return path.join(base, docname) + suffix


sphinx.environment.BuildEnvironment.doc2path = _doc2path


# get_filetype patch
# ------------------
# The ``get_filetype`` function raises an exception if it can't determine the type of a file. Patch it to also recognize source code as restructuredtext. This was taken from ``sphinx.io``, version 1.8.1. This patch only matters for Sphinx 1.8.0+; previous versions work without it.
def _get_filetype(source_suffix, filename):
    # type: (Dict[unicode, unicode], unicode) -> unicode
    for suffix, filetype in iteritems(source_suffix):
        if filename.endswith(suffix):
            # If default filetype (None), considered as restructuredtext.
            return filetype or 'restructuredtext'
    else:
        # The following code was added.
        # Ideally, verify that the provided ``filename`` matches a CodeChat suffix, using code like that in `get_matching_docs`. However, the ``filename`` presented is a full path, not a path relative to the source directory. Therefore, some patterns, such as ``.gitignore``, won't work.
        source_suffixpatterns = ( SUPPORTED_GLOBS |
                                 set(_config.CodeChat_lexer_for_glob.keys()) )
        for source_suffixpattern in source_suffixpatterns:
            if Path(filename).match(source_suffixpattern):
                return 'restructuredtext'
        # This was the existing code.
        print(filename)
        raise FiletypeNotFoundError


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
    doctree):

    sourcename = context.get('sourcename')
    ext = Path(pagename).suffix
    # The extension Sphinx uses optionally includes the `html_sourcelink_suffix <http://www.sphinx-doc.org/en/stable/config.html#confval-html_sourcelink_suffix>`_.
    sphinx_ext = ext + ('' if ext == app.config.html_sourcelink_suffix else app.config.html_sourcelink_suffix)
    double_ext = ext + sphinx_ext
    # Only provide the rename if necessary.
    if sourcename and ext and sourcename.endswith(double_ext):
        # Take off the second of the double extensions.
        context['sourcename'] = sourcename[:-len(double_ext)] + sphinx_ext


# Enki_ support
# =============
# `Enki <http://enki-editor.org/>`_, which hosts CodeChat, needs to know the
# HTML file extension. So, save it to a file for Enki_ to read. Note that this
# can't be done in `Extension setup`_, since the values in ``conf.py`` aren't
# loaded yet. See also global_config_. Instead, wait for the builder-inited_
# event, when the config_ settings are available.
def _builder_inited(
    # See app_.
    app):

    try:
        with codecs.open('sphinx-enki-info.txt', 'wb', 'utf-8') as f:
            f.write(app.config.html_file_suffix)
    except TypeError:
        # If ``html_file_suffix`` is None (TypeError), Enki will assume
        # ``.html``.
        pass


# Extension setup
# ===============
# This routine defines the `entry point
# <http://sphinx-doc.org/extdev/appapi.html>`_ called by Sphinx to initialize
# this extension.
def setup(
    # See app_.
    app):

    # Ensure we're using a new enough Sphinx using `require_sphinx
    # <http://sphinx-doc.org/extdev/appapi.html#sphinx.application.Sphinx.require_sphinx>`_.
    app.require_sphinx('1.5')

    # Use the `source-read <http://sphinx-doc.org/extdev/appapi.html#event-source-read>`_
    # event hook to transform source code to reST before Sphinx processes it.
    app.connect('source-read', _source_read)

    # Add the CodeChat.css style sheet using `add_stylesheet
    # <http://sphinx-doc.org/extdev/appapi.html#sphinx.application.Sphinx.add_stylesheet>`_.
    app.add_stylesheet('CodeChat.css')

    # Add the `CodeChat_lexer_for_glob <CodeChat_lexer_for_glob>` config value. See `add_config_value
    # <http://sphinx-doc.org/extdev/appapi.html#sphinx.application.Sphinx.add_config_value>`_.
    app.add_config_value('CodeChat_lexer_for_glob', {}, 'html')
    # Add the `CodeChat_excludes <CodeChat_excludes>` config value.
    app.add_config_value('CodeChat_excludes', [], 'html')

    # Use the `builder-inited <http://sphinx-doc.org/extdev/appapi.html#event-builder-inited>`_
    # event to write out settings specified in ``conf.py``.
    app.connect('builder-inited', _builder_inited)
    # Use the `html-page-context <http://www.sphinx-doc.org/en/stable/extdev/appapi.html#event-html-page-context>`_
    # event to correct the extension of source files.
    app.connect('html-page-context', _html_page_context)

    # .. _global_config:
    #
    # An ugly hack: we need to get to the `Config <http://sphinx-doc.org/extdev/appapi.html#sphinx.config.Config>`_
    # object after ``conf.py``'s values have been loaded. They aren't loaded
    # yet, so we store the ``config`` object to access it later when it is
    # loaded.
    global _config
    _config = app.config

    # Return `extension metadata <http://sphinx-doc.org/extdev/index.html>`_.
    return {
        'version': __version__,
        'parallel_read_safe': True
    }
