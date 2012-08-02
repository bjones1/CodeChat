# -*- coding: utf-8 -*-
#
# ==============================================================================
# CodeToRest
# ==============================================================================

# .. module:: CodeChat

import re
import codecs

# code_to_rest
# ============
# This routine transforms source code to reST, preserving all indentations of both source code and comments. To do so, the comment characters are stripped from comments and all code is placed inside literal blocks. In addition to this processing, several other difficulies arise: preserving the indentation of both source code and comments; preserving empty lines of code at the beginning or end of a block of code. In the following examples, examine both the source code and the resulting HTML to get the full picture, since the text below is (after all) in reST, and will be therefore be transformed to HTML.
#
# Preserving empty lines of code
# ------------------------------
# First, consider a method to preserve empty lines of code. Consider, for example, the following:
#
# +--------------------------+-------------------------+-----------------------------------+
# + Python source            + Translated to reST      + Translated to (simplified) HTML   |
# +==========================+=========================+===================================+
# | ::                       | Do something::          | ::                                |
# |                          |                         |                                   |
# |  # Do something          |  foo = 1                |  <p>Do something:</p>             |
# |  foo = 1                 |                         |  <pre>foo = 1                     |
# |                          |                         |  </pre>                           |
# |  # Do something else     | Do something else::     |  <p>Do something else:</p>        |
# |  bar = 2                 |                         |  <pre>bar = 2                     |
# |                          |  bar = 2                |  </pre>                           |
# +--------------------------+-------------------------+-----------------------------------+
#
# In this example, the blank line is lost, since reST allows the literal bock containing ``foo = 1`` to end with multiple blank lines; the resulting HTML contains only one newline between each of these lines. To solve this, some CSS hackery helps tighten up spacing between lines. In addition, this routine adds a marker, removed during post-processing, at the end of each code block to preserve blank lines. The new translation becomes:
#
# +--------------------------+-------------------------+-----------------------------------+
# + Python source            + Translated to reST      + Translated to (simplified) HTML   |
# +==========================+=========================+===================================+
# | ::                       | Do something::          | ::                                |
# |                          |                         |                                   |
# |  # Do something          |  foo = 1                |  <p>Do something:</p>             |
# |  foo = 1                 |                         |  <pre>foo = 1                     |
# |                          |  # wokifvzohtdlm        |                                   |
# |  # Do something else     |                         |  </pre>                           |
# |  bar = 2                 | Do something else::     |  <p>Do something else:</p>        |
# |                          |                         |  <pre>bar = 2                     |
# |                          |  bar = 2                |  </pre>                           |
# +--------------------------+-------------------------+-----------------------------------+
#
# Preserving indentation
# ----------------------
# Preserving indentation in code blocks is relatively straightforward. reST eats all whitespace common to a literal block, using that to set the indent. For example:
#
# +--------------------------+-------------------------+
# + Python source            + Translated to reST      +
# +==========================+=========================+
# | ::                       | One space indent::      |
# |                          |                         |
# |  # One space indent      |   foo = 1               |
# |   foo = 1                |                         |
# |                          |                         |
# |  # No indent             | No indent::             |
# |  bar = 2                 |                         |
# |                          |  bar = 2                |
# +--------------------------+-------------------------+
#
# To fix this, code_to_rest adds an unindented marker (also removed during post-processing) at the beginning of each code block to preserve indents:
#
# +--------------------------+-------------------------+
# + Python source            + Translated to reST      +
# +==========================+=========================+
# | ::                       | One space indent::      |
# |                          |                         |
# |  # One space indent      |  # wokifvzohtdlm        |
# |   foo = 1                |   foo = 1               |
# |                          |                         |
# |  # No indent             |                         |
# |  bar = 2                 | No indent::             |
# |                          |                         |
# |                          |  bar = 2                |
# +--------------------------+-------------------------+
#
# Preserving indentation for comments is more difficult. Blockquotes in reST are definted by common indentation, so that any number of (common) spaces define a blockquote:
#
# +--------------------------+-------------------------+
# + Python source            + Translated to reST      +
# +==========================+=========================+
# | ::                       |   Two space indent      |
# |                          |                         |
# |    # Two space indent    |     Four space indent   |
# |      # Four space indent |                         |
# +--------------------------+-------------------------+
#
# To reproduce this, the blockquote indent is defined in CSS to be one character. In addition, removed markers (one per space of indent) define a series of nested blockquotes. As the indent increases, additional markers must be inserted:
#
# +--------------------------+-------------------------+
# + Python source            + Translated to reST      +
# +==========================+=========================+
# | ::                       |  # wokifvzohtdlm        |
# |                          |                         |
# |  # wokifvzohtdlm         |   # wokifvzohtdlm       |
# |                          |                         |
# |   # wokifvzohtdlm        |    Two space indent     |
# |                          |                         |
# |    # Two space indent    |     # wokifvzohtdlm     |
# |                          |                         |
# |                          |      Four space indent  |
# +--------------------------+-------------------------+
#
# Summary and implementation
# --------------------------
# This boils down to two basic rules:
#
# #. Code blocks must be preceeded and followed by a removed marker.
#
# #. Comments must be preeceded by a series of indented markers, one per space of indentation.
#
# Therefore, the (future -- need to rewrite this mess) implemtation consists of a state machine. State transitions, such as code to comment or small comment indent to larger comment indent, provide an opportunity to apply the two rules above. Specifically, the state machine first reads a line, classifies it as code or comment with indent n, and updates the state. It then takes a state transition action as defined below, prepending the resulting string and transforming the line. Finally, it outputs the prepended string and the line.
#
# .. digraph:: code_to_rest
#
#     "code" -> "comment" [ label = "closing code marker\l<newline>\lcomment indent marker(s)\lstrip comment string\l" ];
#     "comment" -> "code" [ label = "<newline>\l::\l<newline>\lopening code marker\l<one space>\l" ];
#     "comment" -> "comment" [ label = "<newline>\lif indent increases:\l  comment indent marker(s)\lstrip comment string\l" ];
#     "code" -> "code" [ label = "<one space>" ];
#     "comment" [ label = "comment,\nindent = n" ]
def code_to_rest(language_specific_options, in_file, out_file):
    unique_remove_comment = (language_specific_options.comment_string + ' ' +
      language_specific_options.unique_remove_str)
    
    # Keep track of the type of the last line.
    last_is_code = False
    # Keep track of the indentation of comment
    comment_indent = ''
    # A regular expression to recognize a comment, storing the whitespace before the comment in group 1. There are two recognized forms of comments: <optional whitespace> [ <comment string> <end of line> OR <comment string> <one char of whitespace> <anything to end of line> ].
    comment_re = re.compile(r'(^\s*)((' + language_specific_options.comment_string + '$)|(' + language_specific_options.comment_string + '\s))')

    # Iterate through all lines in the input file
    for line in in_file:
        # Determine the line type by looking for a comment. If this is a comment, save the number of spaces in this comment
        comment_match = re.search(comment_re, line)
        # Now, process this line. Strip off the trailing newline.
        line = line.rstrip('\n')
        current_line_list = [line]
        if not comment_match:
            # Each line of code needs a space at the beginning, to indent it inside a literal block.
            current_line_list.insert(0, ' ')
            if not last_is_code:
                # When transitioning from comment to code, prepend a \n\n:: after the last line. Put a marker at the beginning of the line so reST will preserve all indentation of the block. (Can't just prepend a <space>::, since this boogers up title underlines, which become ------ ::)
                current_line_list.insert(0, '\n\n::\n\n ' + unique_remove_comment + '\n')
            else:
                # Otherwise, just prepend a newline
                current_line_list.insert(0, '\n')
        else:
            new_comment_indent = comment_match.group(1)
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
                blockquote_indent.append('\n')
                current_line_list.insert(0, ''.join(blockquote_indent))
            if last_is_code:
                # Finish code off with a newline-preserving marker
                current_line_list.insert(0, '\n ' + unique_remove_comment)
            
        # Convert to a string
        line_str = ''.join(current_line_list)
        current_line_list = []
        # For debug:
        # line_str += str(line_type) + str(last_is_code)
        # We're done!
        out_file.write(line_str)
        last_is_code = not comment_match
        
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
