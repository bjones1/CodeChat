# -*- coding: utf-8 -*-

from pygments.formatter import Formatter
from pygments.token import Token
from pygments.lexers import get_lexer_for_filename
from pygments import highlight
from CodeChat import comment_string, unique_remove_comment
import re
import codecs

# This class converts from source to to reST. As the <a>overview</a>
# states, this uses Pygments to do most of the work, adding only a formatter
# to that library. Therefore, to use this class, simply select this class
# as the formatter for Pygments (see an example 
# <a href="#def_CodeToHtml">below</a>).
class CodeToRestFormatter(Formatter):
    # Pygments <a href="http://pygments.org/docs/formatters/#formatter-classes">calls this routine</a> (see the HtmlFormatter) to transform tokens to first-pass formatted lines. We need a two-pass process: first, merge comments; second, transform tokens to lines. This wrapper creates that pipeline, yielding its results as a generator must. It also wraps each line in a &lt;pre&gt; tag.<br />
    def format_unencoded(self, token_source, out_file):
        nl_token_source = self._expand_nl(token_source)
        self._format_body(nl_token_source, out_file)

    def _expand_nl(self, token_source):
        # Break any comments ending in a newline into two separate tokens
        for ttype, value in token_source:
            if (ttype == Token.Comment.Single) and value.endswith('\n'):
                yield ttype, value[:-1]
                yield Token.Text, u'\n'
            else:
                yield ttype, value

    def _format_body(self, token_source, out_file):  
        # Store up a series of string which will compose the current line
        current_line_list = []
        # Keep track of the type of the last line.
        last_is_code = False
        # Determine the type of the current line
        is_code, is_comment, is_ws = range(3)
        line_type = is_comment
        # Keep track of the indentation of comment
        comment_indent = ''
        # A regular expression for whitespace not containing a newline
        ws = re.compile(r'^[ \t\r\f\v]+$')
        # A regular expression to remove comment chars
        regexp = re.compile(r'(^[ \t]*)' + comment_string + '?', re.MULTILINE)

        # Iterate through all tokens in the input file        
        for ttype, value in token_source:
            # Check for whitespace
            if re.search(ws, value):
                # If so, add it to the stack of tokens on this line
                current_line_list.append(value)
            # Check for a comment
            elif (ttype is Token.Comment) or (ttype is Token.Comment.Single):
                if line_type != is_code:
                    line_type = is_comment
                # If so, add it to the stack of tokens on this line
                current_line_list.append(value)
            # On a newline, process the line
            elif value == '\n':
                # Convert to a string
                line_str = ''.join(current_line_list)
                current_line_list = [line_str]
                # If the line is whitespace, inherit the type of the previous
                # line.
                if line_type == is_ws:
                    line_type = is_code if last_is_code else is_comment
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
                    match = re.search(regexp, line_str)
                    if match:
                        comment_indent = match.group(1)
                    # Remove the comment character (and one space, if it's there)
                    current_line_list = [re.sub(regexp, r'\1', line_str)]
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
            # Not a newline, whitespace, or comment char: must be code.
            else:
                line_type = is_code
                current_line_list.append(value)


# <a name="CodeToHtml"></a>Use Pygments with the CodeToHtmlFormatter to translate a source file to an HTML file.
def CodeToRest(source_path, rst_path):
    code = codecs.open(source_path, 'r', encoding = 'utf-8').read()
    formatter = CodeToRestFormatter()
    outfile = codecs.open(rst_path, mode = 'w', encoding = 'utf-8')
    lexer = get_lexer_for_filename(source_path)
    hi_code = highlight(code, lexer, formatter)
    outfile.write(hi_code)
