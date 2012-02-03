# -*- coding: utf-8 -*-
#
# ==============================================================================
# CodeToRest
# ==============================================================================

import re
import codecs

# This class converts from source to to reST. As the <a>overview</a>
# states, this uses Pygments to do most of the work, adding only a formatter
# to that library. Therefore, to use this class, simply select this class
# as the formatter for Pygments (see an example 
# <a href="#def_CodeToHtml">below</a>).
def code_to_rest(language_specific_options, in_file, out_file):
    comment_re = language_specific_options.comment_regex
    unique_remove_comment = language_specific_options.comment_string + \
      language_specific_options.unique_remove_str
    
    # Keep track of the type of the last line.
    last_is_code = False
    # Determine the type of the current line
    is_code, is_comment, is_ws = range(3)
    line_type = is_comment
    # Keep track of the indentation of comment
    comment_indent = ''
    # A regular expression for whitespace not containing a newline
    ws_re = re.compile(r'^\s*$')
    # A regular expression to remove comment chars
    comment_re = re.compile(r'(^\s*)' + comment_re)

    # Iterate through all tokens in the input file        
    for line in in_file:
        # Determine the line type
        # Check for whitespace
        if re.search(ws_re, line):
            # If the line is whitespace, inherit the type of the previous
            # line.
            line_type = is_code if last_is_code else is_comment
        # Check for a comment
        elif re.search(comment_re, line):
            line_type = is_comment
        # On a newline(s), process the line
        else:
            line_type = is_code
            
        # Now, process this line.
        # Convert to a string, stripping off the trailing newline
        line = line[:-1]
        current_line_list = [line]
        if line_type == is_code:
            # Each line of code needs a space at the beginning
            current_line_list.insert(0, ' ')
            if not last_is_code:
                # When transitioning from comment to code, prepend a ::
                # to the last line.
                # Hack: put a . at the beginning of the line so reST
                # will preserve all indentation of the block.
                current_line_list.insert(0, '\n\n::\n\n ' + unique_remove_comment + '\n')
            else:
                # Otherwise, just prepend a newline
                current_line_list.insert(0, '\n')
        else:
            # Save the number of spaces in this comment
            match = re.search(comment_re, line)
            new_comment_indent = match.group(1) if match else ''
            # If indent changes, then re-do indent by treating it as if it were code
            if new_comment_indent != comment_indent:
                last_is_code = True
            comment_indent = new_comment_indent
            # Remove the comment character (and one space, if it's there)
            current_line_list = [re.sub(comment_re, r'\1', line)]
            # Prepend a newline
            current_line_list.insert(0, '\n')
            # Add in left margin adjustments for a code to comment transition
            if last_is_code:
                # Get left margin correct by inserting a series of blockquotes
                blockquote_indent = []
                for i in range(len(comment_indent)):
                    blockquote_indent.append('\n\n' + ' '*i + unique_remove_comment)
                blockquote_indent.append('\n\n')
                current_line_list.insert(0, ''.join(blockquote_indent))
            
        # Convert to a string
        line_str = ''.join(current_line_list)
        current_line_list = []
        # For debug:
        # line_str += str(line_type) + str(last_is_code)
        # We're done!
        out_file.write(line_str)
        last_is_code = line_type == is_code
        line_type = is_ws

# <a name="CodeToHtml"></a>Use Pygments with the CodeToHtmlFormatter to translate a source file to an HTML file.
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
                app.srcdir, source_suffix, exclude_matchers=matchers))
            # Now, translate any old or missing files
            for source_file_noext in docs:
                source_file = source_file_noext + source_suffix
                rest_file = source_file + app.config.source_suffix
                if ( (not os.path.exists(rest_file)) or
                     (os.path.getmtime(source_file) > os.path.getmtime(rest_file)) ):
                    print('Old file: %s' % source_file)
                    CodeToRest(source_file, rest_file, lso)
                else:
                    print('Current file: %s' % source_file)
    

# Sphinx emits this event when the HTML builder has created a context dictionary to render a template with. Do all necessary fix-up after the reST-to-code progress.
def sphinx_html_page_context(app, pagename, templatename, context, doctree):
    if 'body' in context.keys():
        str = context['body']
        # Clean up code from any code to reST goo
        str = re.sub('<span class="c1?">[^<]*' + LanguageSpecificOptions.unique_remove_str + '</span>', '', str)
        str = re.sub('<p>[^<]*' + LanguageSpecificOptions.unique_remove_str + '</p>', '', str)
        str = re.sub('<pre>[^<]*' + LanguageSpecificOptions.unique_remove_str + '\n', '<pre>', str)
        context['body'] = str

# This routine defines the entry point called by Sphinx to initialize this extension, per http://sphinx.pocoo.org/ext/appapi.htm.
def setup(app):
    # See sphinx_source_read() for more info.
    app.connect('html-page-context', sphinx_html_page_context)
    app.connect('builder-inited', sphinx_builder_inited)
    

if __name__ == '__main__':
    from CodeChat import main
    main()
