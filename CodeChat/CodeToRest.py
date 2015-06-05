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
# The API_ lists four function which convert source code into either reST or
# HTML. For a discussion on how this is accomplished, the lexer_to_rest_
# function forms the core of the alogorithm; Step_5_ gives a detailed
# explanation of how the code is translated to reST.
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
from pygments import lex
from pygments.lexers import get_lexer_for_filename, get_lexer_by_name, \
    get_lexer_for_mimetype
from pygments.token import Token
#
# Local application imports
# -------------------------
from .CommentDelimiterInfo import COMMENT_DELIMITER_INFO
#
# API
# ===
# The following routines provide easy access to the core functionality of this
# module: code_to_rest_string_, code_to_rest_file_, code_to_html_string_, and
# code_to_html_file_.
#
# .. _code_to_rest_string:
#
# This function converts a string containg code to reST, returning the result
# as a string.
def code_to_rest_string(
  # .. _code_str:
  #
  # The code to translate to reST.
  code_str,
  # .. _options:
  #
  # Specify the lexer (see get_lexer_ arguments), and provide it any other
  # needed options.
  **options):

    # Use a StringIO to capture writes into a string.
    output_rst = StringIO()
    _lexer_to_rest(code_str, get_lexer(**options), output_rst)
    return output_rst.getvalue()

# .. _code_to_rest_file:
#
# Convert a source file to a reST file.
def code_to_rest_file(
  # .. _source_path:
  #
  # Path to a source code file to process.
  source_path,
  # Path to a destination reST file to create. It will be overwritten if it
  # already exists.
  rst_path,
  # .. _input_encoding:
  #
  # Encoding to use for the input file. The default of None detects the encoding
  # of the input file.
  input_encoding=None,
  # .. _output_encoding:
  #
  # Encoding to use for the output file.
  output_encoding='utf-8'):

    # Use docutil's I/O classes to better handle and sniff encodings.
    #
    # Note: both these classes automatically close themselves after a
    # read or write.
    fi = io.FileInput(source_path=source_path, encoding=input_encoding)
    fo = io.FileOutput(destination_path=rst_path, encoding=output_encoding)
    code_str = fi.read()
    lexer = get_lexer(filename=source_path)
    rst = code_to_rest_string(code_str, lexer=lexer)
    fo.write(rst)


# .. _code_to_html_string:
#
# This converts a string containing source code to HTML, which it returns as a
# string.
def code_to_html_string(
  # See code_str_.
  code_str,
  # A file-like object where warnings and errors will be written, or None to
  # send them to stderr.
  warning_stream=None,
  # See options_.
  **options):

    rest = code_to_rest_string(code_str, **options)
    # `docutils
    # <http://docutils.sourceforge.net/docs/user/tools.html#rst2html-py>`_
    # converts reST to HTML.
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


# .. _code_to_html_file:
#
# Convert source code stored in a file to HTML, which is saved in another file.
def code_to_html_file(
  # See source_path_.
  source_path,
  # Destination file name to hold the generated HTML. This file will be
  # overwritten. If not supplied, *source_path*\ ``.html`` will be assumed.
  html_path=None,
  # See input_encoding_.
  input_encoding=None,
  # See output_encoding_.
  output_encoding='utf-8'):

    html_path = html_path or source_path + '.html'
    fi = io.FileInput(source_path=source_path, encoding=input_encoding)
    fo = io.FileOutput(destination_path=html_path, encoding=output_encoding)

    code_str = fi.read()
    lexer = get_lexer(filename=source_path)
    html = code_to_html_string(code_str, lexer=lexer)

    fo.write(html)
#
#
# Supporting routines
# -------------------
#
# .. _get_lexer:
#
# Provide several ways to find a lexer. Provide any of the following arguments,
# and this function will return the appropriate lexer for it.
def get_lexer(
  # The lexer itself, which will simply be returned.
  lexer=None,
  # The `short name <http://pygments.org/docs/lexers/>`_, or alias, of the
  # lexer to use.
  alias=None,
  # The filename of the source file to lex.
  filename=None,
  # The MIME type of the source ile to lex.
  mimetype=None,
  # See options_.
  **options):

    if lexer:
        return lexer
    if alias:
        return get_lexer_by_name(alias, **options)
    if filename:
        return get_lexer_for_filename(filename, **options)
    if mimetype:
        return get_lexer_for_mimetype(mimetype, **options)


# Provide the ability to print debug info if needed.
def _debug_print(val):
    # Uncomment for debug prints.
    print(val),
    pass
#
#
# .. _lexer_to_rest:
#
# Implementation
# ==============
# This routine transforms source code to reST, preserving all indentations of
# both source code and comments. To do so, the comment characters are stripped
# from reST-formatted comments and all code is placed inside code blocks.
#
# **This routine is the heart of the algorithm.**
def _lexer_to_rest(
  # See code_str_.
  code_str,
  # .. _lexer:
  #
  # The lexer used to analyze the code.
  lexer,
  # See out_file_.
  out_file):

    _debug_print(u'Lexer: {}\n'.format(lexer.name))
    # Gather some additional information, based on the lexer, which is needed
    # to correctly process comments:
    cdi = COMMENT_DELIMITER_INFO[lexer.name]
    # * If there's no multi-line start info, then classify generic comments as
    #   inline. 
    comment_is_inline = not cdi[1]
    # * Likewise, no inline info indicates that generic comments are block 
    #   comments.
    comment_is_block = not cdi[0]
    
    # \1. Invoke a Pygments lexer on the provided source code, obtaining an
    #     iterable of tokens.
    token_iter = lex(code_str, lexer)

    # \2. Combine tokens from the lexer into three groups: whitespace, comment,
    #     or other.
    token_group = _group_lexer_tokens(token_iter, comment_is_inline, comment_is_block)

    # \3. Make a per-line list of [group, string], so that the last string in
    #     each list ends with a newline. Change the group of block comments that
    #     actually span multiple lines.
    gathered_group = _gather_groups_on_newlines(token_group)

    # \4. Classify each line. For reST-formatted comments, remove the leading
    #     whitespace and all comment characters (the // or #, for example).
    #
    # Then classify.
    classified_group = _classify_groups(gathered_group, cdi)

    # \5. Run a state machine to output the corresponding reST.
    _generate_rest(classified_group, out_file)
#
#
# Step 2 of lexer_to_rest_
# ------------------------
# Given tokens, group them.
def _group_lexer_tokens(
  # An interable of (tokentype, string) pairs provided by the lexer, per
  # `get_tokens
  # <http://pygments.org/docs/api/#pygments.lexer.Lexer.get_tokens>`_.
  iter_token,
  # .. _comment_is_inline:
  # 
  # When true, classify generic comments as inline. 
  comment_is_inline,
  # .. _comment_is_block:
  #
  # When true, classify generic comment as block comments.
  comment_is_block):


    # Keep track of the current group and string.
    tokentype, current_string = iter_token.next()
    current_group = _group_for_tokentype(tokentype, comment_is_inline, 
                                         comment_is_block)
    _debug_print(u'tokentype = {}, string = {}\n'.
                format(tokentype, [current_string]))

    # Walk through tokens.
    for tokentype, string in iter_token:
        group = _group_for_tokentype(tokentype, comment_is_inline, 
          comment_is_block)
        _debug_print(u'tokentype = {}, string = {}\n'.
                    format(tokentype, [string]))

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
#
#
# Supporting routines and definitions
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# A simple enumerate I like, taken from one of the snippet on `stackoverflow
# <http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python>`_. 
# What I want: a set of unique identifiers that will be named nicely,
# rather than printed as a number. Really, just a way to create a class whose
# members contain a string representation of their name. Perhaps the best
# solution is `enum34 <https://pypi.python.org/pypi/enum34>`_, based on `PEP
# 0435 <https://www.python.org/dev/peps/pep-0435/>`_, but I don't want an extra
# dependency just for this.
class Enum(frozenset):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError

# Define the groups into which tokens will be placed.
_GROUP = Enum(
  # The basic classification used by group_for_tokentype_.
  ('whitespace inline_comment other ' +
  # A ``/* comment */``-style comment contained in one string.
  'block_comment ' +
  # Grouping is::
  #
  #    /* BLOCK_COMMENT_START
  #       BLOCK_COMMENT_BODY, (repeats for all comment body)
  #       BLOCK_COMMENT_END */
  'block_comment_start block_comment_body block_comment_end ').split())

# .. _group_for_tokentype:
#
# Given a tokentype, group it.
def _group_for_tokentype(
  # The tokentype to place into a group.
  tokentype,
  # See comment_is_inline_.
  comment_is_inline,
  # See comment_is_block_.
  comment_is_block):

    # The list of Pygments `tokens <http://pygments.org/docs/tokens/>`_ lists
    # ``Token.Text`` (how a newline is classified) and ``Token.Whitespace``.
    # Consider either as whitespace.
    if tokentype in Token.Text or tokentype in Token.Whitespace:
        return _GROUP.whitespace
    # There is a Token.Comment, but this can refer to inline or block comments,
    # or even other things (preprocessors statements). Therefore, restrict
    # classification as follows.
    if (tokentype == Token.Comment.Single or 
      (tokentype == Token.Comment and comment_is_inline) ):
        return _GROUP.inline_comment
    if (tokentype == Token.Comment.Multiline or
      (tokentype == Token.Comment and comment_is_block) ):
        return _GROUP.block_comment
    return _GROUP.other
#
#
# Step #3 of lexer_to_rest_
# -------------------------
# Given an iterable of groups, break them into lists based on newlines.
def _gather_groups_on_newlines(
  # An iterable of (group, string) pairs provided by
  # ``group_lexer_tokens``.
  iter_grouped):

    # Keep a list of (group, string) tuples we're accumulating.
    l = []

    # Accumulate until we find a newline, then yield that.
    for group, string in iter_grouped:
        _debug_print(u'group = {}, string = {}\n'.format(group, [string]))
        # A given group (such as a block string) may extend across multiple
        # newlines. Split these groups apart first.
        splitlines = string.splitlines(True)
        # Look for block comments spread across multiple lines and label
        # them  correctly.
        if len(splitlines) > 1 and group == _GROUP.block_comment:
            group = _GROUP.block_comment_start
        for index, split_str in enumerate(splitlines):
            # Accumulate results.
            l.append( (group, split_str) )

            # For block comments, move from a start to a body group.
            if group == _GROUP.block_comment_start:
                group = _GROUP.block_comment_body
            # If the next line is the last line, update the block
            # group.
            is_next_to_last_line = index == len(splitlines) - 2
            if (is_next_to_last_line and
                group == _GROUP.block_comment_body):
                group = _GROUP.block_comment_end

            # Yield when we find a newline, then clear our accumulator.
            if split_str.endswith('\n'):
                yield l
                l = []

    # Output final group, if one is still accumulating.
    if l:
        yield l
#
#
# Step #4 of lexer_to_rest_
# -------------------------
# Classify the output of ``gather_groups_on_newlines`` into either a code or
# comment with n leading whitespace types. Remove all comment characters.
def _classify_groups(
  # An iterable of [(group1, string1_no_newline), (group2, string2_no_newline),
  # ..., (groupN, stringN_ending_newline)], produced by
  # ``gather_groups_on_newlines``.
  iter_gathered_groups,
  # .. _comment_delim_info:
  #
  # An element of COMMENT_DELIMITER_INFO for the language being classified.
  comment_delim_info):

    # Keep track of block comment state.
    is_block_rest_comment = False

    # Walk through groups.
    for l in iter_gathered_groups:
        _debug_print(u'list[(group, string), ... = {}\n'.format(l))

        if _is_rest_comment(l, is_block_rest_comment, comment_delim_info):

            first_group, first_string = l[0]
            # The type = # of leading whitespace characters, or 0 if none.
            if first_group == _GROUP.whitespace:
                # Encode this whitespace in the type, then drop it.
                type_ = len(first_string)
                l.pop(0)
            else:
                type_ = 0

            # Update the block reST state.
            if l[0][0] == _GROUP.block_comment_start:
                is_block_rest_comment = True

            # Strip all comment characters off the strings and combine them.
            string = ''.join([_remove_comment_delim(group, string, 
              comment_delim_info) for group, string in l])
            # Remove the inital space character from the first comment,
            # but not from body or end comments.
            if ( len(string) and string[0] == ' ' and
                first_group not in (_GROUP.block_comment_body,
                                    _GROUP.block_comment_end) ):
                string = string[1:]

        # Everything else is considered code.
        else:
            type_ = -1
            string = ''.join([string for group, string in l])
            is_block_rest_comment = False

        yield type_, string
#
#
# Supporting routines
# ^^^^^^^^^^^^^^^^^^^
# Given a (group, string) tuple, return the string with comment delimiter
# removed if it is a comment, or just the string if it's not a comment.
def _remove_comment_delim(
  # The group this string was classified into.
  group,
  # The string corresponding to this group.
  string,
  # See comment_delim_info_.
  comment_delim_info):

    # Number of characters in a single-line comment delimiter.
    (len_inline_comment_delim,
    # Number of characters in an opening block comment.
    len_opening_block_comment_delim,
    # Number of characters in an closing block comment.
    len_closing_block_comment_delim) = comment_delim_info

    if group == _GROUP.inline_comment:
        return string[len_inline_comment_delim:]
    if group == _GROUP.block_comment:
        return string[ len_opening_block_comment_delim:
                      -len_closing_block_comment_delim]
    if group == _GROUP.block_comment_start:
        return string[len_opening_block_comment_delim:]
    if group == _GROUP.block_comment_end:
        return string[:-len_closing_block_comment_delim]
    else:
        return string


# Return a string with the given delimiter removed from its beginning.
def _remove_beginning_comment_delim(
  # Either the number of characters in the beginning delimiter, or a tuple of
  # strings which give all valie beginning comment delimiters.
  beginning_comment_delim,
  # The string which start with the delimiter to be removed.
  string):

    # If we already know the number of characters in the delimiter, we're done!
    # Just return the substring.
    if isinstance(beginning_comment_delim, int):
        return string[beginning_comment_delim:]
    # Otherwise, we must search for one of the known delimiters in the  given
    # string.
    else:
        for bcd in beginning_comment_delim:
            # If we find it at the beginning of the string, strip it off.
            if string.find(bcd) == 0:
                return string[len(bcd):]

        # Not found -- panic.
        assert False


# Determine if the given line is a comment to be interpreted by reST.
# Supports ``remove_comment_chars``, ``classify_groups``.
def _is_rest_comment(
  # A sequence of (group, string) representing a single line.
  line_list,
  # True if this line contains the body or end of a block comment
  # that will be interpreted by reST.
  is_block_rest_comment,
  # See lexer_.
  lexer):

    # See if there is any _GROUP.other in this line. If so, it's not a reST
    # comment.
    group_tuple, string_tuple = zip(*line_list)
    if _GROUP.other in group_tuple:
        return False
    # If there's no comments (meaning the entire line is whitespace), it's not a
    # reST comment.
    if group_tuple == (_GROUP.whitespace, ):
        return False

    # Find the first comment. There may be whitespace preceeding it, so select
    # the correct index.
    first_comment_index = 1 if group_tuple[0] == _GROUP.whitespace else 0
    first_group = group_tuple[first_comment_index]
    first_string = string_tuple[first_comment_index]
    first_comment_text = _remove_comment_delim(first_group, first_string, lexer)
    # The cases are:
    #
    # #. ``// comment, //\n, #`` -> reST comment. Note that in some languages
    #    (Python is one example), the newline isn't included in the comment.
    # #. ``//comment`` -> not a reST comment.
    # #. ``/* comment, /*\n``, or any block comment body or end for which its
    #    block start was a reST comment.
    # #. ``/**/`` -> a reST comment. (I could see this either as reST or not;
    #    because it was simpler, I picked reST.)
    first_char_is_rest = ( (len(first_comment_text) > 0 and
                          first_comment_text[0] in (' ', '\n')) or
                          len(first_comment_text) == 0 )
    is_block_body_or_end = first_group in (_GROUP.block_comment_body,
                                               _GROUP.block_comment_end)
    if ( (first_char_is_rest and not is_block_body_or_end) or
         (is_block_rest_comment and is_block_body_or_end) ):
        return True
    return False
#
#
# .. _Step_5:
#
# Step #5 of lexer_to_rest_
# -------------------------
# When creating reST block containing code or comments, two difficulies
# arise: preserving the indentation
# of both source code and comments; and preserving empty lines of code at the
# beginning or end of a block of code. In the following examples, examine both
# the source code and the resulting HTML to get the full picture, since the text
# below is (after all) in reST, and will be therefore be transformed to HTML.
#
# First, consider a method to preserve empty lines of code. Consider, for
# example, the following:
#
# +--------------------------+-------------------------+-----------------------------------+
# + Python source            + Translated to reST      + Translated to (simplified) HTML   |
# +==========================+=========================+===================================+
# | .. code-block:: Python   | Do something ::         | .. code-block:: html              |
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
# | .. code-block:: Python   | Do something            | .. code-block:: html              |
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
# ^^^^^^^^^^^^^^^^^^^^^^
# The same fence approach also preserves indentation. Without the fences,
# indendentation is consumed by the reST parser:
#
# +--------------------------+-------------------------+-----------------------------------+
# + Python source            + Translated to reST      + Translated to (simplified) HTML   |
# +==========================+=========================+===================================+
# | .. code-block:: Python   | One space indent ::     | .. code-block:: html              |
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
# | .. code-block:: Python   | One space indent        | .. code-block:: html              |
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
# blockquote. So, the distance between a zero and two-space indent is the same
# as the distance between a two-space and a three-space indent; we need the
# second indent to be half the size of the first.
#
# +--------------------------+-------------------------+-----------------------------------+
# + Python source            + Translated to reST      + Translated to (simplified) HTML   |
# +==========================+=========================+===================================+
# | .. code-block:: Python   | No indent               | .. code-block:: html              |
# |                          |                         |                                   |
# |  # No indent             |   Two space indent      |  <p>No indent</p>                 |
# |    # Two space indent    |                         |  <blockquote>Two space indent     |
# |     # Three space indent |    Three space indent   |   <blockquote>Three space         |
# |                          |                         |     indent                        |
# |                          |                         |   </blockquote>                   |
# |                          |                         |  </blockquote>                    |
# +--------------------------+-------------------------+-----------------------------------+
#
# To fix this, the `raw directive
# <http://docutils.sourceforge.net/docs/ref/rst/directives.html#raw-data-pass-through>`_
# is used to insert a pair of ``<div>`` and ``<div>`` HTML elements which set
# the left margin of indented text based on how many spaces (0.5 em = 1 space).
#
# +--------------------------+-------------------------+-----------------------------------+
# + Python source            + Translated to reST      | Translated to (simplified) HTML   |
# +==========================+=========================+===================================+
# | .. code-block:: Python   |  No indent              | .. code-block:: html              |
# |                          |                         |                                   |
# |  # No indent             |  .. raw:: html          |  <p>No indent</p>                 |
# |    # Two space indent    |                         |  <div style="margin-left:1.0em">  |
# |     # Three space indent |   <div style=           |    <p>Two space indent</p>        |
# |                          |   "margin-left:1.0em;"> |  </div>                           |
# |                          |                         |  <div style="margin-left:1.5em;"> |
# |                          |  Two space indent       |    <p>Three space indent</p>      |
# |                          |                         |  </div>                           |
# |                          |  .. raw:: html          |                                   |
# |                          |                         |                                   |
# |                          |   </div><div style=     |                                   |
# |                          |   "margin-left:1.5em;"> |                                   |
# |                          |                         |                                   |
# |                          |  Three space indent     |                                   |
# |                          |                         |                                   |
# |                          |  .. raw:: html          |                                   |
# |                          |                         |                                   |
# |                          |   </div>                |                                   |
# +--------------------------+-------------------------+-----------------------------------+

# Following either a fenced code block or a raw block, care must be taken to 
# separate these blocks' content from indented comments which follow them. For
# example, the following code:
#
# +--------------------------+-------------------------+-----------------------------------+
# + Python source            + Translated to reST      | Translated to (simplified) HTML   |
# +==========================+=========================+===================================+
# | .. code-block:: Python   |  .. fenced-code::       | .. code-block:: html              |
# |                          |                         |                                   |
# |  def foo():              |     Beginning fence     |  <pre>def foo():                  |
# |  #      Indented comment |     def foo():          |  Ending fence                     |
# |                          |     Ending fence        |                                   |
# |                          |                         |                                   |
# |                          |        Indented comment |                                   |
# +--------------------------+-------------------------+-----------------------------------+
#
# Notice that the ``Ending fence`` ends up in the resulting HTML! To fix this,
# simply add an unindented `reST comment 
# <http://sphinx-doc.org/rest.html#comments>`_ after a block.
#
# +--------------------------+-------------------------+-----------------------------------+
# + Python source            + Translated to reST      | Translated to (simplified) HTML   |
# +==========================+=========================+===================================+
# | .. code-block:: Python   |  .. fenced-code::       | .. code-block:: html              |
# |                          |                         |                                   |
# |  def foo():              |     Beginning fence     |  <pre>def foo():                  |
# |  #      Indented comment |     def foo():          |  </pre>                           |
# |                          |     Ending fence        |  <blockquote>                     |
# |                          |                         |    Indented comment               |
# |                          |  ..                     |  </blockquote>                    |
# |                          |                         |                                   |
# |                          |        Indented comment |                                   |
# +--------------------------+-------------------------+-----------------------------------+
#
# Mixed code and comments
# ^^^^^^^^^^^^^^^^^^^^^^^
# Note that mixing code and comments is hard: reST will still apply some of
# its parsing rules to an inline code block or inline literal, meaning
# that leading or trailing spaces and backticks will not be preserved,
# instead parsing incorrectly. For example ::
#
#    :code:` Testing `
#
# renders incorrectly. So, mixed lines are simply translated as code, meaning
# reST markup can't be applied to the comments.
#
# Summary and implementation
# ^^^^^^^^^^^^^^^^^^^^^^^^^^
# This boils down to the following basic rules:
#
# #. Code blocks must be preceeded and followed by a removed marker (fences).
#
# #. Comments must be preeceded and followed by reST which sets the left
#    margin based on the number of spaces before the comment.
#
# #. Both must be followed by an empty, unindented `reST comment`_.
#
# .. _generate_rest:
#
# Generate reST from the classified code. To do this, create a state machine,
# where current_type defines the state. When the state changes, exit the
# previous state (output a closing fence or closing ``</div>``, then enter the
# new state (output a fenced code block or an opening ``<div style=...>``.
def _generate_rest(
  # An iterable of (type, string) pairs, one per line.
  classified_lines,
  # .. _out_file:
  #
  # A file-like output to which the reST text is written.
  out_file):

    # Keep track of the current type. Begin with a 0-indent comment.
    current_type = -2

    for type_, string in classified_lines:
        _debug_print(u'type_ = {}, string = {}\n'.format(type_, [string]))

        # See if there's a change in state.
        if current_type != type_:
            # Exit the current state.
            _exit_state(current_type, out_file)

            # Enter the new state.
            #
            # Code state: emit the beginning of a fenced block.
            if type_ == -1:
                out_file.write('\n.. fenced-code::\n\n Beginning fence\n')
            # Comment state: emit an opening indent for non-zero indents.
            elif type_ > 0:
                out_file.write('\n.. raw:: html\n\n <div style="margin-left:' +
                               str(0.5*type_) + 'em;">\n\n')

        # Output string based on state. All code needs an inital space to
        # place it inside the fenced-code block.
        if type_ == -1:
            out_file.write(' ')
        out_file.write(string)

        # Update the state.
        current_type = type_

    # When done, exit the last state.
    _exit_state(current_type, out_file)
#
#
# Supporting routines
# ^^^^^^^^^^^^^^^^^^^
# Output text produce when exiting a state. Supports generate_rest_ above.
def _exit_state(
  # The type (classification) of the last line.
  type_,
  # See out_file_.
  out_file):

    # Code state: emit an ending fence.
    if type_ == -1:
        out_file.write(' Ending fence\n\n..\n\n')
    # Comment state: emit a closing indent.
    elif type_ > 0:
        out_file.write('\n.. raw:: html\n\n </div>\n\n..\n\n')
    # Initial state. Nothing needed.
    else:
        pass


# Create a fenced code block: the first and last lines are presumed to be
# fences, which keep the parser from discarding whitespace. Drop these, then
# treat everything else as code.
#
# See the `directive docs
# <http://docutils.sourceforge.net/docs/howto/rst-directives.html>`_ for more
# information.
class _FencedCodeBlock(CodeBlock):
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
        for i, content in enumerate(self.content):
            if content:
                processedAllContent = False
                break
            self.content[i] = ' '
        # If we've seen all the content, then don't do it again -- we'd be
        # adding unnecessary spaces. Otherwise, walk from the end of the content
        # backwards, adding spaces until the first non-blank line.
        if not processedAllContent:
            for i, _ in enumerate(self.content):
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
        # docutils. **Note:** This is based on examining Sphinx 1.3.1 source
        # code.
        #
        # Note that the nodeList returned by the CodeBlock directive contains
        # only a single ``literal_block`` node. The setting should be applied to
        # it.
        nodeList[0]['highlight_args'] = {'force' : True}

        return nodeList

# Register the new fenced code block directive with docutils.
directives.register_directive('fenced-code', _FencedCodeBlock)

