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
# *********************************************************
# CodeToRest.py - a module to translate source code to reST
# *********************************************************
# This module provides two basic functions: code_to_rest_ (and related helper
# functions) to convert a source files to reST, and the FencedCodeBlock
# directive to remove temporary markers (fences) required for correct
# code_to_rest_ operation. A simple wrapper to convert source code to reST,
# then to HTML, then to cleaned HTML is given in code_to_html_.
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
# For code_to_rest parsing.
import re
# For calling code_to_rest with a string. While using cStringIO would be
# great, it doesn't support Unicode, so we can't.
from StringIO import StringIO
# To find a file's extension and locate data files.
import os.path
#
# Third-party imports
# -------------------
# Used to open files with unknown encodings and to run docutils itself.
from docutils import io, core
# Import CodeBlock as a base class for FencedCodeBlock.
from docutils.parsers.rst.directives.body import CodeBlock
# Import directives to register the new FencedCodeBlock directive.
from docutils.parsers.rst import directives
# For the docutils default stylesheet and template
import docutils.writers.html4css1
from docutils.writers.html4css1 import Writer
#
# Local application imports
# -------------------------
from .LanguageSpecificOptions import LanguageSpecificOptions

# code_to_rest
# ============
# This routine transforms source code to reST, preserving all indentations of
# both source code and comments. To do so, the comment characters are stripped
# from comments and all code is placed inside code blocks. In addition to
# this processing, several other difficulies arise: preserving the indentation
# of both source code and comments; preserving empty lines of code at the
# beginning or end of a block of code. In the following examples, examine both
# the source code and the resulting HTML to get the full picture, since the text
# below is (after all) in reST, and will be therefore be transformed to HTML.
#
# Preserving empty lines of code
# ------------------------------
# First, consider a method to preserve empty lines of code. Consider, for
# example, the following:
#
# +--------------------------+-------------------------+-----------------------------------+
# + Python source            + Translated to reST      + Translated to (simplified) HTML   |
# +==========================+=========================+===================================+
# | ::                       | Do something ::         | .. code-block:: html              |
# |                          |                         |                                   |
# |  # Do something          |  foo = 1                |  <p>Do something:</p>             |
# |  foo = 1                 |                         |  <pre>foo = 1                     |
# |                          | Do something else ::    |  </pre>                           |
# |  # Do something else     |                         |  <p>Do something else:</p>        |
# |  bar = 2                 |  bar = 2                |  <pre>bar = 2                     |
# |                          |                         |  </pre>                           |
# +--------------------------+-------------------------+-----------------------------------+
#
# In this example, the blank line is lost, since reST allows the literal bock
# containing ``foo = 1`` to end with multiple blank lines; the resulting HTML
# contains only one newline between each of these lines. To solve this, some CSS
# hackery helps tighten up spacing between lines. In addition, this routine adds
# a one-line fence, removed during processing, at the beginning and end of each
# code block to preserve blank lines. The new translation becomes:
#
# +--------------------------+-------------------------+-----------------------------------+
# + Python source            + Translated to reST      + Translated to (simplified) HTML   |
# +==========================+=========================+===================================+
# | ::                       | Do something            | .. code-block:: html              |
# |                          |                         |                                   |
# |  # Do something          | .. fenced-code::        |  <p>Do something:</p>             |
# |  foo = 1                 |                         |  <pre>foo = 1                     |
# |                          |    Beginning fence      |                                   |
# |  # Do something else     |    foo = 1              |  </pre>                           |
# |  bar = 2                 |                         |  <p>Do something else:</p>        |
# |                          |    Ending fence         |  <pre>bar = 2                     |
# |                          |                         |  </pre>                           |
# |                          | Do something else       |                                   |
# |                          |                         |                                   |
# |                          | .. fenced-code::        |                                   |
# |                          |                         |                                   |
# |                          |    Beginning fence      |                                   |
# |                          |    bar = 2              |                                   |
# |                          |    Ending fence         |                                   |
# |                          |                         |                                   |
# |                          |                         |                                   |
# +--------------------------+-------------------------+-----------------------------------+
#
# Preserving indentation
# ----------------------
# The same fence approach also preserves indentation. Without the fences,
# indendentation is consumed by the reST parser:
#
# +--------------------------+-------------------------+-----------------------------------+
# + Python source            + Translated to reST      + Translated to (simplified) HTML   |
# +==========================+=========================+===================================+
# | ::                       | One space indent ::     | .. code-block:: html              |
# |                          |                         |                                   |
# |  # One space indent      |   foo = 1               |  <p>One space indent</p>          |
# |   foo = 1                |                         |  <pre>foo = 1                     |
# |  # No indent             | No indent ::            |  </pre>                           |
# |  bar = 2                 |                         |  <p>No indent</p>                 |
# |                          |  bar = 2                |  <pre>bar = 1                     |
# |                          |                         |  </pre>                           |
# +--------------------------+-------------------------+-----------------------------------+
#
# With fences added:
#
# +--------------------------+-------------------------+-----------------------------------+
# + Python source            + Translated to reST      + Translated to (simplified) HTML   |
# +==========================+=========================+===================================+
# | ::                       | One space indent        | .. code-block:: html              |
# |                          |                         |                                   |
# |  # One space indent      | .. fenced-code::        |  <p>One space indent</p>          |
# |   foo = 1                |                         |  <pre> foo = 1                    |
# |  # No indent             |    Beginning fence      |  </pre>                           |
# |  bar = 2                 |     foo = 1             |  <p>No indent</p>                 |
# |                          |    Ending fence         |  <pre>bar = 1                     |
# |                          |                         |  </pre>                           |
# |                          | No indent               |                                   |
# |                          |                         |                                   |
# |                          | .. fenced-code::        |                                   |
# |                          |                         |                                   |
# |                          |    Beginning fence      |                                   |
# |                          |    bar = 1              |                                   |
# |                          |    Ending fence         |                                   |
# +--------------------------+-------------------------+-----------------------------------+
#
# Preserving indentation for comments is more difficult. Blockquotes in reST are
# defined by common indentation, so that any number of (common) spaces define a
# blockquote. In addition, nested quotes lose the line break assocatied with a
# paragraph (no space between ``Two space indent`` and ``Four space indent``.
#
# +--------------------------+-------------------------+-----------------------------------+
# + Python source            + Translated to reST      + Translated to (simplified) HTML   |
# +==========================+=========================+===================================+
# | ::                       | No indent               | .. code-block:: html              |
# |                          |                         |                                   |
# |  # No indent             |   Two space indent      |  <p>No indent</p>                 |
# |    # Two space indent    |                         |  <blockquote><div>Two space indent|
# |      # Four space indent |     Four space indent   |   <blockquote><div>Four space     |
# |                          |                         |     indent                        |
# |                          |                         |   </div></blockquote>             |
# |                          |                         |  </div></blockquote>              |
# +--------------------------+-------------------------+-----------------------------------+
#
# To reproduce this, the blockquote indent is defined in CSS to be one character.
# In addition, empty comments (one per space of indent) define a series of
# nested blockquotes. As the indent increases, additional empty comments must be
# inserted:
#
# +--------------------------+-------------------------+-----------------------------------+
# + Python source            + Translated to reST      | Translated to (simplified) HTML   |
# +==========================+=========================+===================================+
# | ::                       | No indent               | .. code-block:: html              |
# |                          |                         |                                   |
# |    # Two space indent    | ..                      |  <p>No indent</p>                 |
# |      # Four space indent |                         |  <blockquote><div>                |
# |                          |  ..                     |   <blockquote><div>Two space      |
# |                          |                         |    indent                         |
# |                          |   Two space indent      |   </div></blockquote>             |
# |                          |                         |  </div></blockquote>              |
# |                          | ..                      |  <blockquote><div>                |
# |                          |                         |   <blockquote><div>               |
# |                          |  ..                     |    <blockquote><div>              |
# |                          |                         |     <blockquote><div>Four space   |
# |                          |   ..                    |      indent                       |
# |                          |                         |     </div></blockquote>           |
# |                          |    ..                   |    </div></blockquote>            |
# |                          |                         |   </div></blockquote>             |
# |                          |     Four space indent   |  </div></blockquote>              |
# +--------------------------+-------------------------+-----------------------------------+
#
# Summary and implementation
# --------------------------
# This boils down to two basic rules:
#
# #. Code blocks must be preceeded and followed by a removed marker.
#
# #. Comments must be preeceded by a series of empty comments, one per space of
#    indentation.
#
# Therefore, the implemtation consists of a state machine. State transitions,
# such as code to comment or small comment indent to larger comment indent,
# provide an opportunity to apply the two rules above. Specifically, the state
# machine first reads a line, classifies it as code or comment with indent *n*,
# and updates the state. It then takes a state transition action as defined by
# the labels on the arrows below, prepending the resulting string and
# transforming the line. Finally, it outputs the prepended string and the line.
#
# .. digraph:: code_to_rest
#
#     "code" -> "comment"
#       [ label = "closing code marker\l<newline>\lempty comment indent(s)\lstrip comment string\l" ];
#     "comment" -> "code"
#       [ label = "<newline>\l.. fenced-code::\l<newline>\lopening code marker\l<one space>\l" ];
#     "comment" -> "comment"
#       [ label = "<newline>\lempty comment indent(s)\lstrip comment string\l" ];
#     "code" -> "code" [ label = "<one space>" ];
#     "comment" [ label = "comment,\nindent = n" ]
def code_to_rest(
  # An input file-like object, containing source code to be converted to reST.
  in_file,
  # An output file-like object, where the resulting reST will be written.
  out_file,
  # |lso|
  #
  # .. |lso| replace:: An instance of :doc:`LanguageSpecificOptions
  #    <LanguageSpecificOptions>` which specifies the language to use in
  #    translating the source code to reST.
  language_specific_options):

    unique_remove_comment = (language_specific_options.comment_string + u' ' +
      language_specific_options.unique_remove_str)

    # Keep track of the type of the last line.
    last_is_code = False
    # Keep track of the indentation of comment
    comment_indent = u''
    # A regular expression to recognize a comment, storing the whitespace before
    # the comment in group 1. There are two recognized forms of comments:
    # <optional whitespace> [ <comment string> <end of line> OR <comment string>
    # <one char of whitespace> <anything to end of line> ].
    comment_re = re.compile(ur'(^\s*)((' + language_specific_options.comment_string
      + u'$)|(' + language_specific_options.comment_string + u'\s))')

    # Iterate through all lines in the input file
    for line in in_file:
        # Determine the line type by looking for a comment. If this is a
        # comment, save the number of spaces in this comment
        comment_match = re.search(comment_re, line)
        # Now, process this line. Strip off the trailing newline.
        line = line.rstrip(u'\n')
        current_line_list = [line]
        if not comment_match:
            # Each line of code needs a space at the beginning, to indent it
            # inside a literal block.
            current_line_list.insert(0, u' ')
            if not last_is_code:
                # When transitioning from comment to code, prepend a ``\n\n.. fenced-code::``
                # after the last line. Put a marker at the beginning of the line
                # so reST will preserve all indentation of the block.
                current_line_list.insert(0, u'\n\n.. fenced-code::\n\n ' + unique_remove_comment + u'\n')
            else:
                # Otherwise, just prepend a newline
                current_line_list.insert(0, u'\n')
        else:
            new_comment_indent = comment_match.group(1)
            # If indent changes or we were just in code, re-do it.
            redo_indent = ((new_comment_indent != comment_indent) or last_is_code)
            comment_indent = new_comment_indent
            # Remove the comment character (and one space, if it's there)
            current_line_list = [re.sub(comment_re, ur'\1', line)]
            # Prepend a newline
            current_line_list.insert(0, u'\n')
            # Add in left margin adjustments for a code to comment transition
            if redo_indent:
                # Get left margin correct by inserting a series of blockquotes
                blockquote_indent = []
                for i in range(len(comment_indent)):
                    blockquote_indent.append(u'\n\n' + u' '*i + u'..')
                blockquote_indent.append(u'\n')
                current_line_list.insert(0, u''.join(blockquote_indent))
            if last_is_code:
                # Finish code off with a newline-preserving marker
                current_line_list.insert(0, u'\n ' + unique_remove_comment)

        # Convert to a string
        line_str = u''.join(current_line_list)
        current_line_list = []
        # For debug:
        # line_str += str(line_type) + str(last_is_code)
        # We're done!
        out_file.write(line_str)
        last_is_code = not comment_match

    # Provide a closing fence if we ended with code.
    if last_is_code:
        out_file.write(u'\n ' + unique_remove_comment)

    # At the end of the file, include a final newline.
    out_file.write(u'\n')

# Choose a LanguageSpecificOptions class based on the given file's extension.
def _lso_from_ext(
  # The path (and name)of a file. This file's extension will be used to create
  # an instance of the LanguageSpecificOptions class.
  file_path):
    lso = LanguageSpecificOptions()
    lso.set_language(os.path.splitext(file_path)[1])
    return lso

# Wrap code_to_rest by processing a string. It returns a string containing the
# resulting reST.
def code_to_rest_string(
  # |source_str|
  #
  # .. |source_str| replace:: String containing source code to process.
  source_str,
  # |lso|
  language_specific_options):
    #
    # We don't use io.StringInput/Output here because it provides only a single
    # read/write operation, while code_to_rest_ expects to do many.
    output_rst = StringIO()
    code_to_rest(StringIO(source_str), output_rst, language_specific_options)
    return output_rst.getvalue()

# Wrap code_to_rest_string by opening in and out files.
def code_to_rest_file(
  # |source_path|
  #
  # .. |source_path| replace:: Path to a source code file to process.
  source_path,
  # Path to a destination reST file to create. It will be overwritten if it
  # already exists.
  rst_path,
  # |lsoNone|
  #
  # .. |lsoNone| replace:: None to determine the language based on the
  #    given source_path's extension.
  language_specific_options=None,
  # |input_encoding|
  #
  # .. |input_encoding| replace:: Encoding to use for the input file. The
  #       default of None detects the encoding of the input file.
  input_encoding=None,
  # |output_encoding|
  #
  # .. |output_encoding| replace:: Encoding to use for the output file.
  output_encoding='utf-8'):

    print('Processing ' + os.path.basename(source_path) + ' to ' +
          os.path.basename(rst_path))
    # Use docutil's I/O classes to better handle and sniff encodings.
    #
    # Note: both these classes automatically close themselves after a
    # read or write.
    fi = io.FileInput(source_path=source_path, encoding=input_encoding)
    fo = io.FileOutput(destination_path=rst_path, encoding=output_encoding)
    lso = language_specific_options or _lso_from_ext(source_path)
    rst = code_to_rest_string(fi.read(), language_specific_options)
    fo.write(rst)


# code_to_html
# ============
# To convert source code to HTML:
#
# #. ``code_to_rest`` converts source code to reST.
# #. `docutils
#    <http://docutils.sourceforge.net/docs/user/tools.html#rst2html-py>`_
#    converts reST to HTML.
def code_to_html_string(
  # |source_str|
  source_str,
  # |lso|
  language_specific_options,
  # A file-like object where warnings and errors will be written, or None to
  # send them to stderr.
  warning_stream=None):

    rest = code_to_rest_string(source_str, language_specific_options)
    html = core.publish_string(rest, writer_name='html',
      settings_overrides={
        # Include our custom css file: provide the path to the default css and
        # then to our css. The stylesheet dirs must include docutils defaults.
        # However, Write.default_stylesheet_dirs doesn't work when frozen,
        # because (I think) it relies on a relative path wihch the frozen
        # environment doesn't have. So, rebuild that path manually.
        'stylesheet_path': Writer.default_stylesheet + ',CodeChat.css',
        'stylesheet_dirs': ['.', os.path.dirname(docutils.writers.html4css1.__file__),
                           os.path.join(os.path.dirname(__file__), 'template')],
        # The default template uses a relative path, which doesn't work when frozen ???.
        'template': os.path.join(os.path.dirname(docutils.writers.html4css1.__file__), Writer.default_template),
        # Make sure to use Unicode everywhere.
        'output_encoding': 'unicode',
        'input_encoding' : 'unicode',
        # Don't stop processing, no matter what.
        'halt_level'     : 5,
        # Capture errors to a string and return it.
        'warning_stream' : warning_stream})
    return html

def code_to_html_file(
  # |source_path|
  source_path,
  # Destination file name to hold the generated HTML. This file will be
  # overwritten. If not supplied, *source_path*\ ``.html`` will be assumed.
  html_path=None,
  # |lsoNone|
  language_specific_options=None,
  # |input_encoding|
  input_encoding=None,
  # |output_encoding|
  output_encoding='utf-8'):

    html_path = html_path or source_path + '.html'
    lso = language_specific_options or _lso_from_ext(source_path)
    fi = io.FileInput(source_path=source_path, encoding=input_encoding)
    fo = io.FileOutput(destination_path=html_path, encoding=output_encoding)

    html = code_to_html_string(fi.read(), lso)

    fo.write(html)


# Create a fenced code block: the first and last lines are presumed to be
# fences, which keep the parser from discarding whitespace. Drop these, then
# treat everything else as code.
#
# See the `directive docs
# <http://docutils.sourceforge.net/docs/howto/rst-directives.html>`_ for more
# information.
class FencedCodeBlock(CodeBlock):
    def run(self):
        # The content must contain at least two lines (the fences).
        if len(self.content) < 2:
            raise self.error('Fenced code block must contain at least two lines.')
        # Remove the fences.
        self.content = self.content[1:-1]
        #
        # By default, the Pygments `stripnl
        # <http://pygments.org/docs/lexers/>`_ option is True, causing Pygments
        # to drop any empty lines. The reST parser converts a line containing
        # only spaces to an empty line, which  will then be stripped by Pygments
        # if these are leading or trailing newlines. So, add a space back in to
        # keep these lines from being dropped.
        #
        # So, first add spaces from the beginning of the lines until we reach
        # the first non-blank line.
        processedAllContent = True
        for i in range(len(self.content)):
            if self.content[i]:
                processedAllContent = False
                break
            self.content[i] = ' '
        # If we've seen all the content, then don't do it again -- we'd be
        # adding unnecessary spaces. Otherwise, walk from the end of the content
        # backwards, adding spaces until the first non-blank line.
        if not processedAllContent:
            for i in range(len(self.content)):
                # Recall Python indexing: while 0 is the first elemment in a
                # list, -1 is the last element, so offset all indices by -1.
                if self.content[-i - 1]:
                    break
                self.content[-i - 1] = ' '

        # Now, process the resulting contents as a code block.
        nodeList = CodeBlock.run(self)

        # Sphinx fix: if the current `highlight
        # <http://sphinx-doc.org/markup/code.html>`_ language is ``python``,
        # "Normal Python code is only highlighted if it is parseable" (quoted
        # from the previous link). This means code snippets, such as
        # ``def foo():`` won't be highlighted: Python wants ``def foo(): pass``,
        # for example. To get around this, setting the ``highlight_args`` option
        # "force"=True skips the parsing. I found this in
        # ``Sphinx.highlighting.highlight_block`` (see the ``force`` argument)
        # and in ``Sphinx.writers.html.HTMLWriter.visit_literal_block``, where
        # the ``code-block`` directive (which supports fragments of code, not
        # just parsable code) has ``highlight_args['force'] = True`` set. This
        # should be ignored by docutils, so it's done for both Sphinx and
        # docutils.
        #
        # Note that the nodeList returned by the CodeBlock directive contains
        # only a single ``literal_block`` node. The setting should be applied to
        # it.
        nodeList[0]['highlight_args'] = {'force' : True}

        return nodeList

# Register the new fenced code block directive with docutils.
directives.register_directive('fenced-code', FencedCodeBlock)
# .. _rewrite:
#
# Idea for code_to_rest rewrite
# =============================
# #. Create a Pygments lexer for the language in use: ``code_file_to_lexer``,
#    ``code_str_to_lexer``.
# #. Combine tokens from the lexer into three groups: whitespace, comment, or
#    other.
# #. Make a per-line list of [group, string], so that the last string in each
#    list ends with a newline. Change the group of multi-line comments that
#    actually span multiple lines.
# #. Classify each line. If a line contains OTHER_GROUP, or the first
#    non-comment character of the first comment isn't a space or newline,
#    it's code. Otherwise, it's a comment.
#
#    For comments, remove the leading whitespace and all comment characters
#    (the // or #, for example).
#
#    Note that mixed code and comments is hard: reST will still apply some of
#    its parsing rules to an inline code block or inline literal, meaning
#    that leading or trailing spaces and backticks will not be preserved,
#    instead parsing incorrectly. For example ::
#
#       :code:` Testing `
#
#    renders incorrectly.
#
# #. Run a state machine to output the corresponding reST.
#
from pygments import lex
from pygments.lexers import get_lexer_for_filename, get_lexer_by_name
from pygments.token import Token
import string

# Step #1 of the rewrite_
# -----------------------
# Given a file containing source code, invoke the lexer on it.
def code_file_to_lexer(
  # |source_path|
  source_path,
  # |input_encoding|
  input_encoding=None,
  # Lexer `options <http://pygments.org/docs/lexers/>`_.
  **lexer_options):

    # Use docutil's I/O classes to better handle and sniff encodings.
    #
    # Note: This classe automatically close itself after a read.
    fi = io.FileInput(source_path=source_path, encoding=input_encoding)

    # `Request
    # <http://pygments.org/docs/api/#pygments.lexers.get_lexer_for_filename>`_
    # a Pygments lexer for this file.
    lexer = get_lexer_for_filename(source_path, **lexer_options)

    # Invoke the lexer.
    return lex(fi.read(), lexer)

# Given a string containing source code, invoke the lexer on it.
def code_str_to_lexer(
  # |source_str|
  source_str,
  # One of the short names from the `available lexers
  # <http://pygments.org/docs/lexers/>`_.
  lexer_name,
  # See the same parameter in code_file_to_lexer.
  **lexer_options):

    # `Request
    # <http://pygments.org/docs/api/#pygments.lexers.get_lexer_by_name>`__
    # a Pygments lexer given its short name (alias).
    lexer = get_lexer_by_name(lexer_name, **lexer_options)

    # Invoke the lexer.
    return lex(source_str, lexer)

# Step #2 of the rewrite_
# -----------------------
# Given tokens, group them.
def group_lexer_tokens(
  # An interable of (tokentype, value) pairs provided by the lexer, per
  # `get_tokens
  # <http://pygments.org/docs/api/#pygments.lexer.Lexer.get_tokens>`_.
  iter_token):

    # Keep track of the current group and string.
    tokentype, current_string = iter_token.next()
    current_group = group_for_tokentype(tokentype)

    # Walk through tokens.
    for tokentype, string in iter_token:
        group = group_for_tokentype(tokentype)

        # If there's a change in group, yield what we've accumulated so far,
        # then initialize the state to the newly-found group and string.
        if current_group != group:
            yield current_group, current_string
            current_group = group
            current_string = string
        # Otherwise, keep accumulating.
        else:
            current_string += string

    # Output final pair, if we have it.
    if current_string:
        yield current_group, current_string

# Supporting routines and definitions
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# Define the groups into which tokens will be placed.
(WHITESPACE_GROUP, SINGLE_LINE_COMMENT_GROUP, OTHER_GROUP,
 # A ``/* comment */``-style comment contained in one string.
 MULTI_LINE_COMMENT_GROUP,
 # Grouping is::
 #
 #    /* MULTI_LINE_COMMENT_START_GROUP,
 #       MULTI_LINE_COMMENT_BODY_GROUP, (repeats for all comment body)
 #       MULTI_LINE_COMMENT_END_GROUP */
 MULTI_LINE_COMMENT_START_GROUP, MULTI_LINE_COMMENT_BODY_GROUP,
 MULTI_LINE_COMMENT_END_GROUP) = range(7)

# Given a tokentype, group it.
def group_for_tokentype(
  # The tokentype to place into a group.
  tokentype):

    # The list of Pygments `tokens <http://pygments.org/docs/tokens/>`_ lists
    # ``Token.Text`` (how a newline is classified) and ``Token.Whitespace``.
    # Consider either as whitespace. However, note that preprocessor directives
    # are considered as a type of comment by Pygments; for our grouping,
    # consider them code.
    if tokentype in Token.Text or tokentype in Token.Whitespace:
        return WHITESPACE_GROUP
    if tokentype in Token.Comment and tokentype not in Token.Comment.Preproc:
        if tokentype not in Token.Comment.Multiline:
            return SINGLE_LINE_COMMENT_GROUP
        else:
            return MULTI_LINE_COMMENT_GROUP
    return OTHER_GROUP


# Step #3 of the rewrite_
# -----------------------
# Given an iterable of groups, break them into lists based on newlines.
def gather_groups_on_newlines(
  # An iterable of (group, string) pairs provided by
  # ``group_lexer_tokens``.
  iter_grouped):

    # Keep a list of (group, string) tuples we're accumulating.
    l = []

    # Accumulate until we find a newline, then yield that.
    for (group, string) in iter_grouped:
        # A given group (such as a multiline string) may extend across multiple
        # newlines. Split these groups apart first.
        splitlines = string.splitlines(True)
        # Look for multi-line comments spread across multiple lines and label
        # them  correctly.
        if len(splitlines) > 1 and group == MULTI_LINE_COMMENT_GROUP:
            group = MULTI_LINE_COMMENT_START_GROUP
        for split_str_index in range(len(splitlines)):
            # Accumulate results.
            split_str = splitlines[split_str_index]
            l.append( (group, split_str) )

            # For multi-line comments, move from a start to a body group.
            if group == MULTI_LINE_COMMENT_START_GROUP:
                group = MULTI_LINE_COMMENT_BODY_GROUP
            # If the next line is the last line, update the multi-line
            # group.
            is_next_to_last_line = split_str_index == len(splitlines) - 2
            if (is_next_to_last_line and
                group == MULTI_LINE_COMMENT_BODY_GROUP):
                group = MULTI_LINE_COMMENT_END_GROUP

            # Yield when we find a newline, then clear our accumulator.
            if split_str.endswith('\n'):
                yield l
                l = []

    # Output final group, if one is still accumulating.
    if l:
        yield l

# Step #4 of the rewrite_
# -----------------------
# Classify the output of ``gather_groups_on_newlines`` into either a code or
# comment with n leading whitespace types. Remove all comment characters.
def classify_groups(
  # An iterable of [(group1, string1_no_newline), (group2, string2_no_newline),
  # ..., (groupN, stringN_ending_newline)], produced by
  # ``gather_groups_on_newlines``.
  iter_gathered_groups,
  # See the same parameter in remove_comment_chars above.
  len_single_line_comment,
  # See the same parameter in remove_comment_chars above.
  len_multi_line_comment):

    # Keep track of multi-line comment state.
    is_multiline_rest_comment = False

    # Walk through groups.
    for l in iter_gathered_groups:

        if is_rest_comment(l, is_multiline_rest_comment,
                           len_single_line_comment, len_multi_line_comment):

            first_group, first_string = l[0]
            # The type = # of leading whitespace characters, or 0 if none.
            if first_group == WHITESPACE_GROUP:
                # Encode this whitespace in the type, then drop it.
                type_ = len(first_string)
                l.pop(0)
            else:
                type_ = 0

            # Update the multiline reST state.
            if l[0][0] == MULTI_LINE_COMMENT_START_GROUP:
                is_multiline_rest_comment = True

            # Strip all comment characters off the strings and combine them.
            string = ''.join([remove_comment_chars(group, string,
              len_single_line_comment, len_multi_line_comment)
              for group, string in l])
            # Remove the inital whitespace character from the first comment,
            # but not from body or end comments.
            if ( len(string) and
                first_group not in (MULTI_LINE_COMMENT_BODY_GROUP,
                                    MULTI_LINE_COMMENT_END_GROUP) ):
                string = string[1:]

        # Everything else is considered code.
        else:
            type_ = -1
            string = ''.join([string for group, string in l])
            is_multiline_rest_comment = False

        yield type_, string

# Supporting routines
# ^^^^^^^^^^^^^^^^^^^
# Given a (group, string) tuple, return the string with comment characters
# removed if it is a comment, or just the string if it's not a comment.
def remove_comment_chars(
  # The group this string was classified into.
  group,
  # The string corresponding to this group.
  string,
  # Number of characters in a single-line comment
  len_single_line_comment,
  # Number of characters in a multi-line comment. I assume the start and end
  # characters are the same length: ``/*`` and ``*/``, etc.
  len_multi_line_comment):

    if group == SINGLE_LINE_COMMENT_GROUP:
        return string[len_single_line_comment:]
    if group == MULTI_LINE_COMMENT_GROUP:
        return string[len_multi_line_comment:-len_multi_line_comment]
    if group == MULTI_LINE_COMMENT_START_GROUP:
        return string[len_multi_line_comment:]
    if group == MULTI_LINE_COMMENT_END_GROUP:
        return string[:-len_multi_line_comment]
    else:
        return string

# Determine if the given line is a comment to be interpreted by reST.
# Supports ``remove_comment_chars``, ``classify_groups``.
def is_rest_comment(
  # A list of (group, string) representing a single line.
  line_list,
  # True if this line contains the body or end of a multi-line comment
  # that will be interpreted by reST.
  is_multiline_rest_comment,
  # See the same parameter in remove_comment_chars above.
  len_single_line_comment,
  # See the same parameter in remove_comment_chars above.
  len_multi_line_comment):

    # See if there is any OTHER_GROUP in this line. If so, it's not a reST
    # comment.
    group_tuple, string_tuple = zip(*line_list)
    if OTHER_GROUP in group_tuple:
        return False
    # If there's no comments (meaning the entire line is whitespace), it's not a
    # reST comment.
    if group_tuple == (WHITESPACE_GROUP, ):
        return False

    # Find the first comment. There may be whitespace preceeding it, so select
    # the correct index.
    first_comment_index = 1 if group_tuple[0] == WHITESPACE_GROUP else 0
    first_group = group_tuple[first_comment_index]
    first_string = string_tuple[first_comment_index]
    first_comment_text = remove_comment_chars(first_group, first_string,
      len_single_line_comment, len_multi_line_comment)
    # The cases are::
    #
    #  #. // comment, //\n -> reST comment
    #  #. //comment -> not a reST comment.
    #  #. /* comment, /*\n, or any multi-line body or end for which its
    #     multi-line start was a reST comment.
    first_char_is_rest = (len(first_comment_text) > 0 and
                          first_comment_text[0] in (' ', '\n'))
    is_multiline_body_or_end = first_group in (MULTI_LINE_COMMENT_BODY_GROUP,
                                               MULTI_LINE_COMMENT_END_GROUP)
    if ( (first_char_is_rest and not is_multiline_body_or_end) or
         (is_multiline_rest_comment and is_multiline_body_or_end) ):
        return True
    return False

# Step #5 of the rewrite_
# -----------------------
# Generate reST from the classified code.
def generate_rest(
  # An iterable of (type, string) pairs, one per line.
  classified_lines,
  # .. _out_file:
  #
  # A file-like output to which the reST text is written.
  out_file):

    # Keep track of the current type. Begin with a 0-indent comment.
    current_type = -2

    for type_, string in classified_lines:
        # See if there's a change in state.
        if current_type != type_:
            # Exit the current state.
            exit_state(current_type, out_file)

            # Enter the new state.
            #
            # Code state: emit the beginning of a fenced block.
            if type_ == -1:
                out_file.write('.. fenced-code::\n\n Beginning fence\n')
            # Comment state: emit an opening indent for non-zero indents.
            elif type_ > 0:
                out_file.write('.. raw:: html\n\n <div style="margin-left:' +
                               str(0.5*type_) + 'em;">\n\n')

        # Output string based on state. All code needs an inital space to
        # place it inside the fenced-code block.
        if type_ == -1:
            out_file.write(' ')
        out_file.write(string)

        # Update the state.
        current_type = type_

    # When done, exit the last state.
    exit_state(current_type, out_file)

# Supporting routines
# ^^^^^^^^^^^^^^^^^^^
# Output text produce when exiting a state. Supports ``generate_rest`` above.
def exit_state(
  # The type (classification) of the last line.
  type_,
  # See out_file_.
  out_file):

    # Code state: emit an ending fence.
    if type_ == -1:
        out_file.write(' Ending fence\n\n')
    # Comment state: emit a closing indent.
    elif type_ > 0:
        out_file.write('\n.. raw:: html\n\n </div>\n\n')
    # Initial state. Nothing needed.
    else:
        pass


