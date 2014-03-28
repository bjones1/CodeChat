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
# *******************************************************************
# CodeToRest.py - a Sphinx extension to translate source code to reST
# *******************************************************************
# This module provides two basic functions: code_to_rest_ (and related helper
# functions) to convert a source files to reST, and code_to_rest_html_clean_ to
# remove temporary markers required for correct code_to_rest_ operation. The
# typical flow would be:
#
# .. digraph:: overall_block_diagram
#
#    "Source code" -> "code_to_rest" [ label = ".py, .c, etc." ];
#    "code_to_rest" -> "reST to HTML" [ label = "reST" ];
#    "reST to HTML" -> "code_to_rest_html_clean"
#      [ label = "HTML with temp. markers" ];
#    "code_to_rest_html_clean" -> "Web browser" [ label = "final HTML" ];
#
# The reST to HTML conversion will typically be performed by
# `docutils <http://docutils.sourceforge.net/docs/user/tools.html#rst2html-py>`_.
#
# Imports
# =======
# These are listed in the order prescribed by `PEP 8
# <http://www.python.org/dev/peps/pep-0008/#imports>`_.
#
# Standard library
# ----------------
# We need this to open and save text files in Unicode.
import codecs
# For code_to_rest_html_clean replacements.
import re
# For calling code_to_rest with a string
from cStringIO import StringIO

# Local application imports
# -------------------------
from LanguageSpecificOptions import LanguageSpecificOptions

# code_to_rest
# ============
# This routine transforms source code to reST, preserving all indentations of
# both source code and comments. To do so, the comment characters are stripped
# from comments and all code is placed inside literal blocks. In addition to
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
# | ::                       | Do something ::         | ::                                |
# |                          |                         |                                   |
# |  # Do something          |  foo = 1                |  <p>Do something:</p>             |
# |  foo = 1                 |                         |  <pre>foo = 1                     |
# |                          |                         |  </pre>                           |
# |  # Do something else     | Do something else ::    |  <p>Do something else:</p>        |
# |  bar = 2                 |                         |  <pre>bar = 2                     |
# |                          |  bar = 2                |  </pre>                           |
# +--------------------------+-------------------------+-----------------------------------+
#
# In this example, the blank line is lost, since reST allows the literal bock
# containing ``foo = 1`` to end with multiple blank lines; the resulting HTML
# contains only one newline between each of these lines. To solve this, some CSS
# hackery helps tighten up spacing between lines. In addition, this routine adds
# a marker, removed during post-processing, at the end of each code block to
# preserve blank lines. The new translation becomes:
#
# +--------------------------+-------------------------+-----------------------------------+
# + Python source            + Translated to reST      + Translated to (simplified) HTML   |
# +==========================+=========================+===================================+
# | ::                       | Do something ::         | ::                                |
# |                          |                         |                                   |
# |  # Do something          |  foo = 1                |  <p>Do something:</p>             |
# |  foo = 1                 |                         |  <pre>foo = 1                     |
# |                          |  # wokifvzohtdlm        |                                   |
# |  # Do something else     |                         |  </pre>                           |
# |  bar = 2                 | Do something else ::    |  <p>Do something else:</p>        |
# |                          |                         |  <pre>bar = 2                     |
# |                          |  bar = 2                |  </pre>                           |
# +--------------------------+-------------------------+-----------------------------------+
#
# Preserving indentation
# ----------------------
# Preserving indentation in code blocks is relatively straightforward. reST eats
# all whitespace common to a literal block, using that to set the indent. For
# example:
#
# +--------------------------+-------------------------+-----------------------------------+
# + Python source            + Translated to reST      + Translated to (simplified) HTML   |
# +==========================+=========================+===================================+
# | ::                       | One space indent ::     | ::                                |
# |                          |                         |                                   |
# |  # One space indent      |   foo = 1               |  <p>One space indent</p>          |
# |   foo = 1                |                         |  <pre>foo = 1                     |
# |                          |                         |  </pre>                           |
# |  # No indent             | No indent ::            |  <p>No indent</p>                 |
# |  bar = 2                 |                         |  <pre>bar = 1                     |
# |                          |  bar = 2                |  </pre>                           |
# +--------------------------+-------------------------+-----------------------------------+
#
# To fix this, code_to_rest adds an unindented marker (also removed during
# post-processing) at the beginning of each code block to preserve indents:
#
# +--------------------------+-------------------------+-----------------------------------+
# + Python source            + Translated to reST      + Translated to (simplified) HTML   |
# +==========================+=========================+===================================+
# | ::                       | One space indent ::     | ::                                |
# |                          |                         |                                   |
# |  # One space indent      |  # wokifvzohtdlm        |  <p>One space indent</p>          |
# |   foo = 1                |   foo = 1               |  <pre> foo = 1                    |
# |                          |                         |  </pre>                           |
# |  # No indent             |                         |  <p>No indent</p>                 |
# |  bar = 2                 | No indent ::            |  <pre>bar = 1                     |
# |                          |                         |  </pre>                           |
# |                          |  # wokifvzohtdlm        |                                   |
# |                          |  bar = 2                |                                   |
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
# | ::                       | No indent               | ::                                |
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
# | ::                       | No indent               | ::                                |
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
# machine first reads a line, classifies it as code or comment with indent n,
# and updates the state. It then takes a state transition action as defined by
# the labels on the arrows below, prepending the resulting string and
# transforming the line. Finally, it outputs the prepended string and the line.
#
# .. digraph:: code_to_rest
#
#     "code" -> "comment"
#       [ label = "closing code marker\l<newline>\lempty comment indent(s)\lstrip comment string\l" ];
#     "comment" -> "code"
#       [ label = "<newline>\l::\l<newline>\lopening code marker\l<one space>\l" ];
#     "comment" -> "comment"
#       [ label = "<newline>\lempty comment indent(s)\lstrip comment string\l" ];
#     "code" -> "code" [ label = "<one space>" ];
#     "comment" [ label = "comment,\nindent = n" ]
def code_to_rest(
  language_specific_options,
  # |lso|
  #
  # .. |lso| replace:: An instance of :doc:`LanguageSpecificOptions
  #    <LanguageSpecificOptions.py>` which specifies the language to use in
  #    translating the source code to reST.
  in_file,
  # An input file-like object, containing source code to be converted to reST.
  out_file):
  # An output file-like object, where the resulting reST will be written.
    unique_remove_comment = (language_specific_options.comment_string + ' ' +
      language_specific_options.unique_remove_str)

    # Keep track of the type of the last line.
    last_is_code = False
    # Keep track of the indentation of comment
    comment_indent = ''
    # A regular expression to recognize a comment, storing the whitespace before
    # the comment in group 1. There are two recognized forms of comments:
    # <optional whitespace> [ <comment string> <end of line> OR <comment string>
    # <one char of whitespace> <anything to end of line> ].
    comment_re = re.compile(r'(^\s*)((' + language_specific_options.comment_string
      + '$)|(' + language_specific_options.comment_string + '\s))')

    # Iterate through all lines in the input file
    for line in in_file:
        # Determine the line type by looking for a comment. If this is a
        # comment, save the number of spaces in this comment
        comment_match = re.search(comment_re, line)
        # Now, process this line. Strip off the trailing newline.
        line = line.rstrip('\n')
        current_line_list = [line]
        if not comment_match:
            # Each line of code needs a space at the beginning, to indent it
            # inside a literal block.
            current_line_list.insert(0, ' ')
            if not last_is_code:
                # When transitioning from comment to code, prepend a \n\n::
                # after the last line. Put a marker at the beginning of the line
                # so reST will preserve all indentation of the block. (Can't
                # just prepend a <space>::, since this boogers up title
                # underlines, which become ------ ::)
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
                    blockquote_indent.append('\n\n' + ' '*i + '..')
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
def CodeToRestFile(
  source_path,
  # Path to a source code file to process.
  rst_path,
  # Path to a destination reST file to create. It will be overwritten if it
  # already exists.
  language_specific_options):
  # |lso|
    print('Processing ' + source_path + ' to ' + rst_path)
    with codecs.open(source_path, 'r', encoding = 'utf-8') as in_file:
        with codecs.open(rst_path, mode = 'w', encoding = 'utf-8') as out_file:
            code_to_rest(language_specific_options, in_file, out_file)

# Wrap code_to_rest by processing a string. It returns a string containing the
# resulting reST.
def CodeToRestString(
  source_str,
  # String containing source code to process.
  language_specific_options):
  # |lso|
  output_rst = StringIO()
  code_to_rest(language_specific_options, StringIO(source_str),
    output_rst)
  return output_rst.getvalue()


# code_to_rest_html_clean
# =======================
# Clean up markers injected by code_to_rest. It returns a string containing
# cleaned HTML.
def code_to_rest_html_clean(
  str):
  # A string produced by translating the output of code_to_rest_ to HTML.
    #
    # Note that a <pre> tag on a line by itself does NOT produce a newline in the html, hence <pre>\n in the replacement text.
    str = re.sub('<pre>[^\n]*' + LanguageSpecificOptions.unique_remove_str + '[^\n]*\n', '<pre>\n', str)

    # TODO: Add examples of where these are seen.
    str = re.sub('<span class="\w+">[^<]*' + LanguageSpecificOptions.unique_remove_str + '</span>\n', '', str)
    str = re.sub('<p>[^<]*' + LanguageSpecificOptions.unique_remove_str + '</p>', '', str)
    str = re.sub('\n[^\n]*' + LanguageSpecificOptions.unique_remove_str + '</pre>', '\n</pre>', str)

    # When an empty comment indented by at least two spaces preceeds a heading, like this:
    ##   #
    ## Foo
    ## ---
    # then the HTML produced is repeated <blockquote><div> then <div># wokifvzohtdlm</div>.
    str = re.sub('<div>[^<]*' + LanguageSpecificOptions.unique_remove_str + '</div>', '', str)

    # The BatchLexer doesn't always recognize comments, treating then an un-hilighed code: just a blank line which says
    ## : wokifvz-ohtdlm (dash added to keep this from disappearing)
    str = re.sub('\n[^\n]*' + LanguageSpecificOptions.unique_remove_str + '\n', '\n', str)

    return str
