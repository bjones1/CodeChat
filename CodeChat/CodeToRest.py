# -*- coding: utf-8 -*-
#
# ==============================================================================
# CodeToRest
# ==============================================================================

# .. module:: CodeChat


import re
import codecs

# Add in junk comments to force indentation to work when trasitioning between code and comments or vice versa.
def code_to_rest(language_specific_options, in_file, out_file):
    unique_remove_comment = language_specific_options.comment_string + \
      language_specific_options.unique_remove_str
    
    # Keep track of the type of the last line.
    last_is_code = False
    # Determine the type of the current line
    is_code, is_comment = range(2)
    line_type = is_comment
    # Keep track of the indentation of comment
    comment_indent = ''
    # A regular expression for whitespace not containing a newline
    ws_re = re.compile(r'^\s*$')
    # A regular expression to remove comment chars
    comment_re = re.compile(r'(^\s*)' + language_specific_options.comment_string)

    # Iterate through all lines in the input file
    for line in in_file:
        # Determine the line type
        # Check for whitespace
        if re.search(ws_re, line):
            # If the line is whitespace, treat it as code.
            line_type = is_code
        # Check for a comment
        elif re.search(comment_re, line):
            line_type = is_comment
        # All other types (including blank lines) are code.
        else:
            line_type = is_code
            
        # Now, process this line. Strip of the trailing newline
        line = line.rstrip('\n')
        current_line_list = [line]
        if line_type == is_code:
            # Each line of code needs a space at the beginning, to indent it inside a literal block.
            current_line_list.insert(0, ' ')
            if not last_is_code:
                # When transitioning from comment to code, prepend a :: to the last line. Put a marker at the beginning of the line so reST will preserve all indentation of the block.
                current_line_list.insert(0, ' ::\n\n ' + unique_remove_comment + '\n')
            else:
                # Otherwise, just prepend a newline
                current_line_list.insert(0, '\n')
        else:
            # This is a comment. Save the number of spaces in this comment
            match = re.search(comment_re, line)
            new_comment_indent = match.group(1) if match else ''
            # If indent changes or we were just in code, re-do it.
            redo_indent = ((new_comment_indent != comment_indent) or last_is_code)
            comment_indent = new_comment_indent
            # Remove the comment character (and one space, if it's there)
            current_line_list = [re.sub(comment_re, r'\1', line)]
            # Prepend a newline
            current_line_list.insert(0, '\n')
            # Add in left margin adjustments for a code to comment transition
            if redo_indent:
                # Get left margin correct by inserting a series of blockquotes
                blockquote_indent = []
                for i in range(len(comment_indent)):
                    blockquote_indent.append('\n\n' + ' '*i + unique_remove_comment)
                blockquote_indent.append('\n\n')
                current_line_list.insert(0, ''.join(blockquote_indent))
            if last_is_code:
                # Finish code off with a newline-preserving marker
                current_line_list.insert(0, '\n ' + unique_remove_comment + '\n')
            
        # Convert to a string
        line_str = ''.join(current_line_list)
        current_line_list = []
        # For debug:
        # line_str += str(line_type) + str(last_is_code)
        # We're done!
        out_file.write(line_str)
        last_is_code = line_type == is_code
        
    # At the end of the file, include a final newline
    out_file.write('\n')

# Wrap code_to_rest by opening in and out files.
def CodeToRest(source_path, rst_path, language_specific_options):
    with codecs.open(source_path, 'r', encoding = 'utf-8') as in_file:
        with codecs.open(rst_path, mode = 'w', encoding = 'utf-8') as out_file:
            code_to_rest(language_specific_options, in_file, out_file)
            


# .. function:: sphinx_builder_inited(app)
#
# This function searches for source code and transforms it to reST before Sphinx searches for reST source.
#
# To do so, we need to search for source files. Sphinx has some utils to help with that.
from sphinx.util.matching import compile_matchers
from sphinx.util import get_matching_docs
import os.path
from LanguageSpecificOptions import LanguageSpecificOptions

def sphinx_builder_inited(app):
    # Look for every extension of every supported langauge
    lso = LanguageSpecificOptions()
    for lang in lso.language_specific_options.keys():
        lso.set_language(lang())
        for source_suffix in lso.extensions:
            # Find all source files with the given extension. This was copied almost verabtim from sphinx.environment.BuildEnvironment.find_files.
            matchers = compile_matchers(
                app.config.exclude_patterns[:] +
                app.config.exclude_trees +
                [d + app.config.source_suffix for d in app.config.unused_docs] +
                ['**/' + d for d in app.config.exclude_dirnames] +
                ['**/_sources', '.#*']
            )
            docs = set(get_matching_docs(
                app.srcdir, source_suffix, exclude_matchers = matchers))
            # This can return an empty filename; remove it.
            docs -= set([''])
            # Now, translate any old or missing files
            for source_file_noext in docs:
                source_file = source_file_noext + source_suffix
                rest_file = source_file + app.config.source_suffix
                if ( (not os.path.exists(rest_file)) or
                     (os.path.getmtime(source_file) > os.path.getmtime(rest_file)) ):
                    CodeToRest(source_file, rest_file, lso)
                else:
                    pass
    

# Sphinx emits this event when the HTML builder has created a context dictionary to render a template with. Do all necessary fix-up after the reST-to-code progress.
def sphinx_html_page_context(app, pagename, templatename, context, doctree):
    env = app and app.builder.env
    if 'body' in context.keys():
        str = context['body']
        # Clean markers injected by code_to_rest.
        str = re.sub('<pre>[^\n]*' + LanguageSpecificOptions.unique_remove_str + '[^\n]*\n', '<pre>\n', str)  # Note that a <pre> tag on a line by itself does NOT produce a newline in the html, hence <pre>\n in the replacement text.
        str = re.sub('<span class="\w+">[^<]*' + LanguageSpecificOptions.unique_remove_str + '</span>\n', '', str)
        str = re.sub('<p>[^<]*' + LanguageSpecificOptions.unique_remove_str + '</p>', '', str)
        str = re.sub('\n[^\n]*' + LanguageSpecificOptions.unique_remove_str + '</pre>', '\n</pre>', str)
        if hasattr(env, "codelinks"):
            for codelink in env.codelinks:
                print(codelink)
                str = re.sub('<span class="n">' + codelink['search'] + '</span>', 
                             '<span class="n"><a href="' + codelink['replace'] + '">' +  codelink['search'] + '</a></span>',
                             str)
        context['body'] = str

# Playing with creating a new codelink directive to embed hyperlinks in code.
from sphinx.util.compat import Directive
class CodelinkDirective(Directive):
    # this enables content in the directive
    required_arguments = 1
    optional_arguments = 100000

    # When we encounter a codelink directive, save its args in the environment.
    def run(self):
        env = self.state.document.settings.env
        if not hasattr(env, 'codelinks'):
            env.codelinks = []
        # The codelink directive's arguments give a search and replace string, in the format search=replace.
        for arg in self.arguments:
            search_replace = arg.split('=', 1)
            sr_len = len(search_replace)
#            print(arg, sr_len, search_replace)
            assert sr_len <= 2
            if sr_len == 2:
                env.codelinks.append({'search' : search_replace[0],
                                      'replace' : search_replace[1],
                                     'docname' : env.docname})
        return []

def purge_codelinks(app, env, docname):
    if not hasattr(env, 'codelinks'):
        return
    env.todo_all_todos = [codelink for codelink in env.codelinks
                          if codelink['docname'] != docname]

# This routine defines the entry point called by Sphinx to initialize this extension, per http://sphinx.pocoo.org/ext/appapi.htm.
def setup(app):
    # See sphinx_source_read() for more info.
    app.connect('html-page-context', sphinx_html_page_context)
    app.connect('builder-inited', sphinx_builder_inited)
    
    app.add_directive('codelink', CodelinkDirective)
    app.connect('env-purge-doc', purge_codelinks)

if __name__ == '__main__':
    from CodeChat import main
    main()
