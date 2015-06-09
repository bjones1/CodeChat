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
# This modules supplies CodeToRest-related Sphinx extensions.
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
# For code_to_rest_html_clean replacements.
import os.path
# For glob_to_lexer matching.
import re, fnmatch

# Third-party imports
# -------------------
# Sphinx routines help to search for source files.
from sphinx.util.matching import compile_matchers
from sphinx.util import get_matching_docs
from pygments.lexers import get_all_lexers
import pygments.util

# Local application imports
# -------------------------
from .CodeToRest import code_to_rest_string, code_to_rest_file, get_lexer
from .CommentDelimiterInfo import COMMENT_DELIMITER_INFO
from . import __version__

# Supported extensions
# --------------------
# Compute a list of supported filename extensions: supported by the lexer and
# by CodeChat (inline / block comment info in COMMENT_DELIMITER_INFO).
SUPPORTED_EXTENSIONS = set()
# Per `get_all_lexers
# <http://pygments.org/docs/api/#pygments.lexers.get_all_lexers>`_, we get a
# tuple. Pick out only the filename and examine it.
for longname, aliases, filename_patterns, mimetypes in get_all_lexers():
    # Pick only filenames we have comment info for.
    if longname in COMMENT_DELIMITER_INFO:
        for fnp in filename_patterns:
            # Take just the extension, which is what Sphinx expects.
            ext = os.path.splitext(fnp)[1]
            # Wrap ext in a list so set won't treat it each character in the
            # string as a separate element.
            SUPPORTED_EXTENSIONS = SUPPORTED_EXTENSIONS.union([ext])

# Now, do some fixup on this list:
#
# * ``Makefile.*`` turns into ``.*`` as an extension. Remove this.
#   Likewise, ``Sconscript`` turns into an empty string, which confuses
#   Sphinx. Remove this also.
SUPPORTED_EXTENSIONS -= set(['.*', ''])
# * Expand ``.php[345]``.
SUPPORTED_EXTENSIONS -= set(['.php[345]'])
SUPPORTED_EXTENSIONS |= set(['.php', '.php3', '.php4', '.php5'])

# CodeToRest extension
# ====================
# This extension provides the CodeToRest Sphinx extension. There are two
# implementations:
#
# * Pre 1.3 Sphinx: translate all source files to reST before Sphinx looks for
#   reST source (``sphinx_builder_inited``). This leaves a lot of gunky ``.rst``
#   files around in the source directory.
# * 1.3 and newer Sphinx: translate a source file in place to reST
#   (``source_read``). Much cleaner.
#
# This function searches for source code and transforms it to reST before Sphinx
# searches for reST source.
def builder_inited(app):
    # Look for every extension of every supported langauge. Add it if we support
    # that language.

    for source_suffix in SUPPORTED_EXTENSIONS:
        # Find all source files with the given extension. This was copied almost
        # verabtim from ``sphinx.environment.BuildEnvironment.find_files``.
        #
        # `html_extra_path <http://sphinx-doc.org/config.html#build-config>`_
        # was added in Sphinx 1.2. Support earlier versions as well.
        try:
            ep = app.config.html_extra_path
        except:
            ep = []
        matchers = compile_matchers(
            app.config.exclude_patterns[:] +
            ep +
            app.config.exclude_trees +
            [d + app.config.source_suffix for d in app.config.unused_docs] +
            ['**/' + d for d in app.config.exclude_dirnames] +
            ['**/_sources', '.#*']
        )
        docs = set(get_matching_docs(
            app.srcdir, source_suffix, exclude_matchers = matchers))

        # ``get_matching_docs`` can return an empty filename; remove it.
        docs -= set([''])
        # Now, translate any old or missing files.
        for source_file_noext in docs:
            source_file = os.path.join(app.env.srcdir, source_file_noext + source_suffix)
            rest_file = os.path.join(app.env.srcdir, source_file + app.config.source_suffix)
            if ( (not os.path.exists(rest_file)) or
                 (os.path.getmtime(source_file) > os.path.getmtime(rest_file)) ):
                options = _lexer_for_filename(app, source_file)
                code_to_rest_file(source_file, rest_file,
                                  app.config.html_output_encoding, **options)
            else:
                pass

# Find a lexer for the given filename. Return a dict to be passed as arguments
# to :ref:`get_lexer`.
def _lexer_for_filename(
  # A Sphinx app instance.
  app,
  # The path of the file under consideration
  source_file):

    # See if ``source_file`` matches any of the globs.
    for glob, lexer_alias in app.config.CodeChat_lexer_for_glob.iteritems():
        # Sphinx likes to capitalize the extension of the file it's processing
        # (observed using Sphinx 1.3.1 on Windows). So, normalize the path
        # before doing the comparison.
        if re.match(fnmatch.translate(glob), os.path.normpath(
          os.path.normcase(source_file))):
            # On a match, pass the specified lexer alias.
            return {'alias': lexer_alias}
    # If none of the globs match, fall back to choosing a lexer based only on
    # the filename.
    return {'filename': source_file}

# The source-read_ event occurs when a source file is read. If it's code, this
# routine changes it into reST.
def source_read(app, docname, source):
    # The docname doesn't provide an extension. Look up the full name and
    # extension using `doc2path
    # <http://sphinx-doc.org/extdev/envapi.html#sphinx.environment.BuildEnvironment.doc2path>`_.
    full_path = app.env.doc2path(docname)
    # See if it's an extension we should process.
    try:
        options = _lexer_for_filename(app, full_path)
        source[0] = code_to_rest_string(source[0], **options)
    except KeyError, pygments.util.ClassNotFound:
        # We Don't support this language.
        pass

# Sphinx hooks
# ============
# This routine defines the `entry point
# <http://sphinx-doc.org/extdev/appapi.html>`_ called by Sphinx to initialize
# this extension.
def setup(app):
    try:
        # See if we're using at least Sphinx v1.3 using `require_sphinx
        # <http://sphinx-doc.org/extdev/appapi.html#sphinx.application.Sphinx.require_sphinx>`_.
        app.require_sphinx('1.3')
        # If so, then we can use the `source-read
        # <http://sphinx-doc.org/extdev/appapi.html#sphinx.version_info>`_ event
        # hook instead of uglyness below.
        app.connect('source-read', source_read)
    except:
        # Translate source files to .rst files before Sphinx looks for them
        # after the `builder-inited
        # <http://sphinx-doc.org/extdev/appapi.html#event-builder-inited>`_
        # event is emitted.
        app.connect('builder-inited', builder_inited)
    # Add the CodeChat.css style sheet using `add_stylesheet
    # <http://sphinx-doc.org/extdev/appapi.html#sphinx.application.Sphinx.add_stylesheet>`_.
    app.add_stylesheet('CodeChat.css')
    # Add the CodeChat_lexer_for_glob config value. See `add_config_value
    # <http://sphinx-doc.org/extdev/appapi.html#sphinx.application.Sphinx.add_config_value>`_.
    app.add_config_value('CodeChat_lexer_for_glob', {}, 'html')
    # Return `extension metadata <http://sphinx-doc.org/extdev/index.html>`_.
    return {'version' : __version__,
            'parallel_read_safe' : True }
