# .. -*- coding: utf-8 -*-
#
#    Copyright (C) 2012-2015 Bryan A. Jones.
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
# *************************************************************************
# CodeToRestSphinx.py - a Sphinx extension to translate source code to reST
# *************************************************************************
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
import os.path
from os import path
# For glob_to_lexer matching.
import fnmatch
# For saving Enki info.
import codecs
#
# Third-party imports
# -------------------
from sphinx.util import get_matching_files
import sphinx.environment
from sphinx.util.osutil import SEP
import pygments.util
#
# Local application imports
# -------------------------
from .CodeToRest import code_to_rest_string, get_lexer
from .CommentDelimiterInfo import SUPPORTED_GLOBS
from . import __version__
#
# source-read event
# =================
# The source-read_ event occurs when a source file is read. If it's code, this
# routine changes it into reST.
def _source_read(
  # .. _app:
  #
  # The `Sphinx application object <http://sphinx-doc.org/extdev/appapi.html#sphinx.application.Sphinx>`_.
  app,
  # The name of the document that was read. It contains a path relative to the
  # project directory and (typically) no extension.
  docname,
  # A list whose single element is the contents of the source file.
  source):

    # If the docname's extension doesn't change when asking for its full path,
    # then it's source code. Normally, the docname of ``foo.rst`` is ``foo``;
    # only for source code is the docname of ``foo.c`` also ``foo.c``. Look up
    # the full name and extension using `doc2path
    # <http://sphinx-doc.org/extdev/envapi.html#sphinx.environment.BuildEnvironment.doc2path>`_.
    # Then, use the basename for comparison. Use normcase to ensure a string
    # comparison will be valid.
    base_full_path = os.path.basename(os.path.normcase(app.env.doc2path(docname)))
    # The docname can include a relative path, such as ``src/foo.c``. Remove the
    # path, and again use basename for valid string comparison.
    base_docname = os.path.basename(docname)
    if base_full_path == os.path.normcase(base_docname):
        # See if it's an extension we should process.
        try:
            # Pass the non-normcase version, per _source_file.
            lexer = _lexer_for_filename(app, base_docname, source[0])
            app.info('Converted using the {} lexer.'.format(lexer.name))
            source[0] = code_to_rest_string(source[0], lexer=lexer)
        except (KeyError, pygments.util.ClassNotFound):
            # We Don't support this language.
            pass

# Find a lexer for the given filename. Return a dict to be passed as arguments
# to :ref:`get_lexer <get_lexer>`.
def _lexer_for_filename(
  # See app_.
  app,
  # .. _source_file:
  #
  # The base name of the file under consideration. This must **NOT** be
  # processed by normcase, since ``get_lexer`` doesn't use normcase in its
  # comparsions.
  source_file,
  # The code in source_file,
  code_str):

    # Sphinx likes to capitalize the extension of the file it's processing
    # (observed using Sphinx 1.3.1 on Windows). So, normalize the path
    # before doing the comparison.
    norm_source_file = os.path.normcase(source_file)
    # See if ``source_file`` matches any of the globs.
    for glob, lexer_alias in app.config.CodeChat_lexer_for_glob.iteritems():
        if fnmatch.fnmatch(norm_source_file, glob):
            # On a match, pass the specified lexer alias.
            return get_lexer(alias=lexer_alias)
    # If none of the globs match, fall back to choosing a lexer based only on
    # the filename.
    return get_lexer(filename=source_file, code=code_str)
#
# Monkeypatch
# ===========
# Sphinx doesn't naturally look for source files. Simply adding all supported
# source file extensions to ``conf.py``'s `source_suffix <http://sphinx-doc.org/config.html#confval-source_suffix>`_
# doesn't work, since ``foo.c`` and ``foo.h`` will now both been seen as the
# docname ``foo``, making then indistinguishable.
#
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
    # The following line was added. While SUPPORTED_EXTENSIONS gives a list of
    # extensions, the CodeChat_lexer_for_glob is a glob, so it doesn't need a
    # prepended ``*``.
    source_suffixpatterns = ( SUPPORTED_GLOBS |
                             set(_config.CodeChat_lexer_for_glob.keys()) )
    for filename in get_matching_files(dirname, exclude_matchers):
        for suffixpattern in suffixpatterns:
            if fnmatch.fnmatch(filename, suffixpattern):
                yield filename[:-len(suffixpattern)+1]
                break
        # The following code was added.
        for source_suffixpattern in source_suffixpatterns:
            if fnmatch.fnmatch(filename, source_suffixpattern):
                yield filename
                break

# Note that this is referenced in ``sphinx.environment`` by ``from sphinx.util
# import get_matching_docs``. So, `where to patch <https://docs.python.org/dev/library/unittest.mock.html#where-to-patch>`_
# is in ``sphinx.environment`` instead of ``sphinx.util``.
sphinx.environment.get_matching_docs = _get_matching_docs

# Next, the way docnames get transformed back to a full path needs to be fixed
# for source files. Specifically, a docname might be the source file, without
# adding an extension.
def _doc2path(self, docname, base=True, suffix=None):
    """Return the filename for the document name.

    If *base* is True, return absolute path under self.srcdir.
    If *base* is None, return relative path to self.srcdir.
    If *base* is a path string, return absolute path under that.
    If *suffix* is not None, add it instead of config.source_suffix.
    """
    docname = docname.replace(SEP, path.sep)
    if suffix is None:
        for candidate_suffix in self.config.source_suffix:
            if path.isfile(path.join(self.srcdir, docname) +
                           candidate_suffix):
                suffix = candidate_suffix
                break
        else:
            # Three lines of code added here -- check for the no-extenion case.
            if path.isfile(path.join(self.srcdir, docname)):
                suffix = ''
            else:
                # document does not exist
                suffix = self.config.source_suffix[0]
    if base is True:
        return path.join(self.srcdir, docname) + suffix
    elif base is None:
        return docname + suffix
    else:
        return path.join(base, docname) + suffix

sphinx.environment.BuildEnvironment.doc2path = _doc2path
#
# Enki_ support
# =============
def _builder_inited(
  # See app_.
  app):

    # `Enki <http://enki-editor.org/>`_, which hosts CodeChat, needs to know
    # the HTML file extension. So, save it to a file for Enki_ to read. Note
    # that this can't be done in setup_, since the values in ``conf.py`` aren't
    # loaded yet. See also global_config_.
    try:
        with codecs.open('sphinx-enki-info.txt', 'wb', 'utf-8') as f:
            f.write(app.config.html_file_suffix)
    except TypeError:
        # If ``html_file_suffix`` is None (TypeError), Enki will assume
        # ``.html``.
        pass
#
# .. _setup:
#
# Extension setup
# ===============
# This routine defines the `entry point
# <http://sphinx-doc.org/extdev/appapi.html>`_ called by Sphinx to initialize
# this extension.
def setup(
  # See app_.
  app):

    # Ensure we're using at least Sphinx v1.3 using `require_sphinx
    # <http://sphinx-doc.org/extdev/appapi.html#sphinx.application.Sphinx.require_sphinx>`_.
    app.require_sphinx('1.3')

    # Use the `source-read <http://sphinx-doc.org/extdev/appapi.html#event-source-read>`_
    # event hook to transform source code to reST before Sphinx processes it.
    app.connect('source-read', _source_read)

    # Add the CodeChat.css style sheet using `add_stylesheet
    # <http://sphinx-doc.org/extdev/appapi.html#sphinx.application.Sphinx.add_stylesheet>`_.
    app.add_stylesheet('CodeChat.css')

    # Add the CodeChat_lexer_for_glob config value. See `add_config_value
    # <http://sphinx-doc.org/extdev/appapi.html#sphinx.application.Sphinx.add_config_value>`_.
    app.add_config_value('CodeChat_lexer_for_glob', {}, 'html')

    # Use the `builder-inited <http://sphinx-doc.org/extdev/appapi.html#event-builder-inited>`_
    # event to write out settings specified in ``conf.py``.
    app.connect('builder-inited', _builder_inited)

    # .. _global_config:
    #
    # An ugly hack: we need to get to the `Config <http://sphinx-doc.org/extdev/appapi.html#sphinx.config.Config>`_
    # object after ``conf.py``'s values have been loaded. They aren't loaded
    # yet, so we store the ``config`` object to access it later when it is
    # loaded.
    global _config
    _config = app.config

    # Return `extension metadata <http://sphinx-doc.org/extdev/index.html>`_.
    return {'version' : __version__,
            'parallel_read_safe' : True }
