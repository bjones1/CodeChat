# .. -*- coding: utf-8 -*-
#
#    Copyright (C) 2012-2013 Bryan A. Jones.
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
import re
import os.path

# Third-party imports
# -------------------
# Sphinx routines help to search for source files.
from sphinx.util.matching import compile_matchers
from sphinx.util import get_matching_docs

# Local application imports
# -------------------------
from .LanguageSpecificOptions import LanguageSpecificOptions
from .CodeToRest import code_to_rest_file, code_to_rest_html_clean

# CodeToRest extension
# ====================
# This extension provides the CodeToRest Sphinx extension. The overall process:
#
# #. Translate all source files to reST before Sphinx looks for reST source
#    (``sphinx_builder_inited``).
# #. When Sphinx has HTML ready to output, strip out gunk inserted by
#    ``code_to_rest`` to format source files correctly
#    (``sphinx_html_page_context``).
#
# This function searches for source code and transforms it to reST before Sphinx
# searches for reST source.
def sphinx_builder_inited(app):
    # Look for every extension of every supported langauge.
    lso = LanguageSpecificOptions()
    for source_suffix in lso.extension_to_options.keys():
        # Choose the current language to process any file in.
        lso.set_language(source_suffix)
        
        # This part of the code has turned into a giant hack, trying to deal
        # with various versions of Sphinx. For now, leave it and gradually 
        # remove portions as support for older Sphinx versions fades.
        #
        # Find all source files with the given extension. This was copied almost
        # verabtim from ``sphinx.environment.BuildEnvironment.find_files``.
        #
        # `html_extra_path <http://sphinx-doc.org/config.html#build-config>`_
        # was added in Sphinx 1.2. Support earlier versions as well.
        try:
            ep = app.config.html_extra_path
        except:
            ep = []

        # The deprecated config values ``exclude_trees``, ``exclude_dirnames``
        # and ``unused_docs`` were removed in `Sphinx 1.3b1
        # <http://sphinx-doc.org/changes.html#release-1-3b1-released-oct-10-2014>`_.
        # Keep going if these aren't available.
        try:
            et = app.config.exclude_trees
            tp = []
            ed = ['**/' + d for d in app.config.exclude_dirnames]
            ud = [d + app.config.source_suffix for d in app.config.unused_docs]
            more_excludes = ''
            gmd_source_suffix = source_suffix
        except:
            et = []
            # Per the documentation on `templates_path 
            # <http://sphinx-doc.org/config.html#confval-templates_path>`_, this
            # value is added to the list of excludes starting in v 1.3. Put it
            # here, which isn't executed for pre-1.3 Sphinx.
            tp = app.config.templates_path
            ed = []
            ud = []
            # The v1.3 source adds one more exclude.
            more_excludes = '*.lproj/**'
            # The v1.3 source expects ``source_suffix`` to be a list.
            gmd_source_suffix = [source_suffix]

        # Build a list of file patterns to exclude, then gather docs that should 
        # be processed after applying these excludes.
        matchers = compile_matchers(
            app.config.exclude_patterns[:] +
            ep +
            tp +
            et +
            ud +
            ed +
            ['**/_sources', '.#*', more_excludes]
        )
        docs = set(get_matching_docs(
            app.srcdir, gmd_source_suffix, exclude_matchers=matchers))
        # ``get_matching_docs`` can return an empty filename; remove it.
        docs -= set([''])
        
        # Now, translate any old or missing files.
        for source_file_noext in docs:
            source_file = os.path.join(app.env.srcdir, source_file_noext +
                                       source_suffix)
            # Starting in `Sphinx 1.3
            # <http://sphinx-doc.org/changes.html#release-1-3-released-mar-10-2015>`_,
            # ``source_suffix`` can be a list, not just a string. Handle both
            # cases.
            if isinstance(app.config.source_suffix, str):
                app_source_suffix = app.config.source_suffix
            else:
                app_source_suffix = app.config.source_suffix[0]

            rest_file = os.path.join(app.env.srcdir, source_file + app_source_suffix)
            if ( (not os.path.exists(rest_file)) or
                 (os.path.getmtime(source_file) > os.path.getmtime(rest_file)) ):
                print(source_file, rest_file)
                code_to_rest_file(source_file, rest_file, lso,
                                  app.config.html_output_encoding)

# Sphinx emits this event when the HTML builder has created a context dictionary
# to render a template with. Do all necessary fix-up after the reST-to-code
# progress.
def sphinx_html_page_context(app, pagename, templatename, context, doctree):
    env = app and app.builder.env
    if 'body' in context.keys():
        s = context['body']
        s = code_to_rest_html_clean(s)

        if hasattr(env, "codelinks"):
            for codelink in env.codelinks:
                print(codelink)
                s = re.sub('<span class="n">' + codelink['search'] + '</span>',
                           '<span class="n"><a href="' + codelink['replace'] +
                             '">' +  codelink['search'] + '</a></span>', s)
        context['body'] = s

# Sphinx hooks
# ============
# This routine defines the entry point called by Sphinx to initialize this
# extension, per http://sphinx.pocoo.org/ext/appapi.htm.
def setup(app):
    # See sphinx_source_read() for more info.
    app.connect('html-page-context', sphinx_html_page_context)
    app.connect('builder-inited', sphinx_builder_inited)
