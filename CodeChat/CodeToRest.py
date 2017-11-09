# .. Copyright (C) 2012-2017 Bryan A. Jones.
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
# The API_ lists four functions which convert source code into either reST or
# HTML. For a discussion on how this is accomplished, the lexer_to_rest_
# function forms the core of the alogorithm; `step 5 <Step_5>`_ gives a detailed
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
from io import StringIO
import os.path
from enum import Enum
# To clean up docstrings.
import inspect

# Third-party imports
# -------------------
# Used to open files with unknown encodings and to run docutils itself.
from docutils import io, core
# Import CodeBlock as a base class for FencedCodeBlock.
from docutils.parsers.rst.directives.body import CodeBlock
# Import directives to register the new FencedCodeBlock and SetLine directives.
from docutils.parsers.rst import directives, Directive
# For the docutils default stylesheet and template
from docutils.writers.html4css1 import Writer
from pygments.lexers import get_lexer_for_filename, get_lexer_by_name, \
    get_lexer_for_mimetype, guess_lexer_for_filename, guess_lexer
from pygments.util import text_type, guess_decode
from pygments.lexer import _encoding_map
from pygments.token import Token
from pygments.filter import apply_filters
import ast

# Local application imports
# -------------------------
from .CommentDelimiterInfo import COMMENT_DELIMITER_INFO

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
    _lexer_to_rest(code_str, get_lexer(code=code_str, **options), output_rst)
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
    # Encoding to use for the input file. The default of None detects the
    # encoding of the input file.
    input_encoding=None,
    # .. _output_encoding:
    #
    # Encoding to use for the output file.
    output_encoding='utf-8',
    # See options_.
    **options):

    # Use docutil's I/O classes to better handle and sniff encodings.
    #
    # Note: both these classes automatically close themselves after a
    # read or write.
    fi = io.FileInput(source_path=source_path, encoding=input_encoding)
    fo = io.FileOutput(destination_path=rst_path, encoding=output_encoding)
    code_str = fi.read()
    lexer = get_lexer(filename=source_path, code=code_str, **options)
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
        'stylesheet_path': ','.join(Writer.default_stylesheets + ['CodeChat.css']),
        'stylesheet_dirs': Writer.default_stylesheet_dirs +
            [os.path.join(os.path.dirname(__file__), 'template')],
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
    lexer = get_lexer(filename=source_path, code=code_str)
    html = code_to_html_string(code_str, lexer=lexer)

    fo.write(html)


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
    # The MIME type of the source file to lex.
    mimetype=None,
    # The code to be highlighted, used to guess a lexer.
    code=None,
    # See options_.
    **options):

    # This sets the default tabsize to 4 spaces in
    # `Pygments' lexer <http://pygments.org/docs/api/#pygments.lexer.Lexer>`_,
    # and this link is a list  of
    # `all available lexers <http://pygments.org/docs/lexers/#available-lexers>`_
    options.setdefault('tabsize', 4)

    if lexer:
        return lexer
    if alias:
        return get_lexer_by_name(alias, **options)
    if filename:
        if code:
            return guess_lexer_for_filename(filename, code, **options)
        else:
            return get_lexer_for_filename(filename, **options)
    if mimetype:
        return get_lexer_for_mimetype(mimetype, **options)
    if code:
        return guess_lexer(code, **options)

# .. _len_cdi:
#
# Transforms the comment delimiter info from strings into the length
# of the string.
def _len_cdi(cdi_string):
    cdi = []
    # Takes each item in the tuple and gets the length of the item
    for i in cdi_string:
        if i is not None:
            a = len(i)
        else:
            a = None
        cdi.append(a)
    # Creates a new tuple from the list of lengths and returns it
    return tuple(cdi)

# Provide the ability to print debug info if needed.
def _debug_print(val):
    # Uncomment for debug prints.
    #print(val),
    pass


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

    _debug_print('Lexer: {}\n'.format(lexer.name))
    # Gather some additional information, based on the lexer, which is needed
    # to correctly process comments:
    cdi = _len_cdi(COMMENT_DELIMITER_INFO[lexer.name])
    # * If there's no multi-line start info, then classify generic comments as
    #   inline.
    comment_is_inline = not cdi[1]
    # * Likewise, no inline info indicates that generic comments are block
    #   comments.
    comment_is_block = not cdi[0]

    # Include a header containing some `CodeChat style`_. Don't put this in a separate ``.js`` file, since docutils doesn't have an easy way to include it.
    out_file.write(codechat_style)

    # 1.    Invoke a Pygments lexer on the provided source code, obtaining an
    #       iterable of tokens. Also analyze Python code for docstrings.
    #
    token_iter, ast_docstring, ast_syntax_error = _pygments_lexer(code_str, lexer)
    # Prepend any syntax error found to the output.
    if ast_syntax_error:
        out_file.write('.. error:: {}\n\n'.format(ast_syntax_error))

    # 2.    Combine tokens from the lexer into three groups: whitespace, comment,
    #       or other.
    token_group = _group_lexer_tokens(token_iter, comment_is_inline,
                                      comment_is_block, ast_docstring)

    # 3.    Make a per-line list of [group, ws_len, string], so that the last
    #       string in each list ends with a newline. Change the group of block
    #       comments that actually span multiple lines.
    gathered_group = _gather_groups_on_newlines(token_group, cdi)

    # 4.    Classify each line. For reST-formatted comments, remove the leading
    #       whitespace and all comment characters (the // or #, for example).
    classified_group = _classify_groups(gathered_group, cdi)

    # 5.    Run a state machine to output the corresponding reST.
    _generate_rest(classified_group, out_file)

# .. _CodeChat style:
#
# CodeChat style
# --------------
# `../CodeChat.css` provides some of the CSS needed to properly format CodeChat documents. However, not all the necessary styling can be accomplished using CSS. This script sets the styles that can't be set in CSS. Specifically, it removes the bottom margin for cases where code follows a paragraph. The expected structure:
#
# .. code-block:: HTML
#   :linenos:
#
#   <div class="CodeChat-indent">    An indent from CodeChat -- not present with no indent.
#       <p>Text.</p>                 DO NOT change this element's bottom margin.
#       <p>Some text here</p>        This could be any element.
#   </div>
#   <div class="highlight-xxx">      Where xxx is the language name, such as c, python, etc.
#       ...Some code here...
#   </div>
codechat_style = (
    '.. raw:: html\n'
    '\n'
    ' <script type="text/javascript">'
    # Only style after the `DOM is ready <https://stackoverflow.com/questions/799981/document-ready-equivalent-without-jquery>`_.
    'document.addEventListener("DOMContentLoaded", function(event) {'
        # Walk the tree in the given direction.
        'let walk_tree = function('
            # The jQuery elements to walk.
            'elements,'
            # The walker function: ``x => x.next/prevElementSibling``.
            'func_walk,'
            # Which child to select, ``x => first/lastElementChild``.
            'func_child) {'

            # Create an array to hold the children found.
            'let walk_children = [];'
            # For each element in the list of elements, find all its next/previous children.
            'for (let index = 0; index < elements.length; ++index) {'
                # If the current element (``that``) doesn't have a next/previous sibling, ascend the tree until we find one or reach the top.
                'let that = elements[index];'
                'while (that && !func_walk(that)) {'
                    'that = that.parentElement;'
                '}'
                'if (that) {'
                    # We found a next/previous sibling. Go there.
                    'that = func_walk(that);'

                    # Include the next/previous sibling in the output.
                    'walk_children.push(that);'
                    # Add all first/last children of this node to the output.
                    'while (that && func_child(that)) {'
                        'that = func_child(that);'
                        'walk_children.push(that);'
                    '}'
                '}'
            '}'
            'return walk_children;'
        '};'

        # All CodeChat-produced code is marked by the ``fenced-code`` class.
        'let code = document.getElementsByClassName("fenced-code");'
        # Go to the next node from code, then set the margin-top of all first children to 0 so that there will be no extra space between the code and the following comment.
        'walk_tree(code, x => x.nextElementSibling, x => x.firstElementChild).map(x => {'
            'x.style.marginTop = 0;'
            'x.style.paddingTop = 0;'
        '});'
        # Same, but remove space between a comment and the following code.
        'walk_tree(code, x => x.previousElementSibling, x => x.lastElementChild).map(x => {'
            'x.style.marginBottom = 0;'
            'x.style.paddingBottom = 0;'
        '});'
    '});'
    '</script>'
)

# Step 1 of lexer_to_rest_
# ------------------------
def _pygments_lexer(
    # See code_str_.
    code_str,
    # See lexer_.
    lexer):

    # Pygments does some cleanup on the code given to it before lexing it. If
    # this is Python code, we want to run AST on that cleaned-up version, so
    # that AST results can be correlated with Pygments results. However,
    # Pygments doesn't offer a way to do this; so, add that ability in to the
    # detected lexer.
    preprocessed_code_str = _pygments_get_tokens_preprocess(lexer, code_str)
    # Note: though Pygments does support a `String.Doc token type <http://pygments.org/docs/tokens/#literals>`_,
    # it doesn't truly identify docstring; from Pygments 2.1.3,
    # ``pygments.lexers.python.PythonLexer``:
    #
    # .. code-block:: Python3
    #    :linenos:
    #    :lineno-start: 55
    #
    #    (r'^(\s*)([rRuU]{,2}"""(?:.|\n)*?""")', bygroups(Text, String.Doc)),
    #    (r"^(\s*)([rRuU]{,2}'''(?:.|\n)*?''')", bygroups(Text, String.Doc)),
    #
    # which means that ``String.Doc`` is simply *ANY* triple-quoted string.
    # Looking at other lexers, ``String.Doc`` often refers to a
    # specially-formatted comment, not a docstring. From
    # ``pygments.lexers.javascript``:
    #
    # .. code-block:: Javascript
    #    :linenos:
    #    :lineno-start: 591
    #
    #    (r'//.*?\n', Comment.Single),
    #    (r'/\*\*!.*?\*/', String.Doc),
    #    (r'/\*.*?\*/', Comment.Multiline),
    #
    # So, the ``String.Doc`` token can't be used in any meaningful way by
    # CodeToRest to identify docstrings. Per Wikipedia's `docstrings article
    # <https://en.wikipedia.org/wiki/Docstring>`_, only three languages support
    # this feature. So, we'll need a language-specific approach. For Python,
    # `PEP 0257 <https://www.python.org/dev/peps/pep-0257>`_ provides the
    # syntax and even some code to correctly remove docstring indentation. The
    # `ast <https://docs.python.org/3.4/library/ast.html>`_ module provides
    # routines which parse a given Python string without executing it, which
    # is better than evaluating arbitrary Python then looking at its
    # ``__doc__`` attributes.
    #
    # Perhaps the approach would be to scan with ast, then see if the line
    # number matches the ending line number of a string, and if so convert the
    # string into a comment. Trickiness: Python will merge strings; consider
    # the following:
    #
    # .. code-block:: pycon
    #    :linenos:
    #
    #    >>> def foo():
    #    ...     ("""A comment.""" \
    #    ...      ' More.'
    #    ...      " And more.")
    #    ...     pass
    #    ...
    #    >>> print(foo.__doc__)
    #    A comment. More. And more.
    #
    # It's probabaly best not to support this case. Unfortunately, AST reports
    # this as a single string, rather than as a list of several elements.
    # The approach: make sure the docstring found by ast is in the text of a
    # Pygments string token. If so, replace the string token by a block
    # comment, whose contents come from ``inspect.cleandoc`` of the docstring.
    #
    # So, process this with AST if this is Python or Python3 code to find docstrings.
    # If found, store line number and docstring into ``ast_docstring``.
    ast_docstring = {}
    # Provide a place to store syntax errors resutling from parsing the Python code.
    ast_syntax_error = ''
    # Determine if code is Python or Python3. Note that AST processing cannot
    # support Python 2 specific syntax (e.g. the ``<>`` operator).
    if lexer.name == 'Python' or lexer.name == 'Python 3':
        # Syntax errors cause ``ast.parse`` to fail. Catch and report them.
        try:
            # If so, walk through the preprocessed code to analyze each token.
            for _ in ast.walk(ast.parse(preprocessed_code_str)):
                try:
                    # Check if current token is a docstring.
                    d = ast.get_docstring(_, False)
                    if d is not None:
                        # If so, store current line number and token value. Note
                        # that ``lineno`` gives the last line of the string,
                        # per http://bugs.python.org/issue16806.
                        ast_docstring[_.body[0].lineno] = d
                except (AttributeError, TypeError):
                    pass
        except SyntaxError as err:
            # Take the file name (which shows up as ``<unknown>`` out of the error message returned.
            ast_syntax_error = 'SyntaxError: {}. Docstrings cannot be processed.\n'.format(err).replace('<unknown>, ', '')

    # Now, run the lexer.
    return (_pygments_get_tokens_postprocess(lexer, preprocessed_code_str),
            ast_docstring, ast_syntax_error)

# Pygments monkeypatching
# ^^^^^^^^^^^^^^^^^^^^^^^
# Provide a way to perform preprocessing on text before lexing it. This code was
# copied from ``pygments.lexer.Lexer.get_token``, v. 2.1.3.
def _pygments_get_tokens_preprocess(self, text, unfiltered=False):
    """
    Return an iterable of (tokentype, value) pairs generated from
    ``text``. If ``unfiltered`` is set to ``True``, the filtering mechanism
    is bypassed even if filters are defined.

    Also preprocess the text, i.e. expand tabs and strip it if
    wanted and applies registered filters.
    """
    if not isinstance(text, text_type):
        if self.encoding == 'guess':
            text, _ = guess_decode(text)
        elif self.encoding == 'chardet':
            try:
                import chardet
            except ImportError:
                raise ImportError('To enable chardet encoding guessing, '
                                  'please install the chardet library '
                                  'from http://chardet.feedparser.org/')
            # check for BOM first
            decoded = None
            for bom, encoding in _encoding_map:
                if text.startswith(bom):
                    decoded = text[len(bom):].decode(encoding, 'replace')
                    break
            # no BOM found, so use chardet
            if decoded is None:
                enc = chardet.detect(text[:1024])  # Guess using first 1KB
                decoded = text.decode(enc.get('encoding') or 'utf-8',
                                      'replace')
            text = decoded
        else:
            text = text.decode(self.encoding)
            if text.startswith(u'\ufeff'):
                text = text[len(u'\ufeff'):]
    else:
        if text.startswith(u'\ufeff'):
            text = text[len(u'\ufeff'):]

    # text now *is* a unicode string
    text = text.replace('\r\n', '\n')
    text = text.replace('\r', '\n')
    if self.stripall:
        text = text.strip()
    elif self.stripnl:
        text = text.strip('\n')
    if self.tabsize > 0:
        text = text.expandtabs(self.tabsize)
    if self.ensurenl and not text.endswith('\n'):
        text += '\n'
    # EDIT: This is not from the original Pygments code. It was added to return
    # the preprocessed text.
    return text

# This code was copied from ``pygments.lexer.Lexer.get_token``, v. 2.1.3 (the last
# few lines).
def _pygments_get_tokens_postprocess(self, text, unfiltered=False):
    def streamer():
        for _, t, v in self.get_tokens_unprocessed(text):
            yield t, v
    stream = streamer()
    if not unfiltered:
        stream = apply_filters(stream, self.filters, self)
    return stream


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
    comment_is_block,
    # Docstring dict found from AST scanning.
    ast_docstring):

    # Keep track of the current group, string, and line no.
    current_string = ''
    current_group = None
    token_lineno = 1
    # Walk through tokens.
    for tokentype, string in iter_token:
        _debug_print('tokentype = {}, string = {}\n'.
                    format(tokentype, [string]))
        # Increase token line no. for every newline found.
        token_lineno += string.count('\n')
        if tokentype == Token.Literal.String.Doc:
            _debug_print('token_lineno = {}, token_docstring = {}\n'.
                  format(token_lineno, string))
            # Compare formatted token containing docstring with AST result.
            if ast_docstring.get(token_lineno) == string[3:-3]:
                tokentype = Token.Comment.Multiline
                string = inspect.cleandoc(string)
                # Insert an extra space after the docstring delimiter, making
                # this look like a reST commment.
                string = string[0:3] + ' ' + string[3:]
        group = _group_for_tokentype(tokentype, comment_is_inline,
          comment_is_block)

        # If there's a change in group, yield what we've accumulated so far,
        # then initialize the state to the newly-found group and string.
        if current_group is None:
            current_group = group
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
class _GROUP(Enum):
    # The basic classification used by group_for_tokentype_.
    whitespace = 1
    inline_comment = 2
    other = 3
    # A ``/* comment */``-style comment contained in one string.
    block_comment = 4
    # Grouping is::
    #
    #    /* BLOCK_COMMENT_START
    #       BLOCK_COMMENT_BODY, (repeats for all comment body)
    #       BLOCK_COMMENT_END */
    block_comment_start = 5
    block_comment_body = 6
    block_comment_end = 7

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
    # There is a Token.Comment, but this can refer to inline or block comments.
    # Therefore, use info from CommentDelimiterInfo as a tiebreaker.
    if (tokentype == Token.Comment.Single or
      # A few goofy lexers use this as of Pygments 2.1.3. See https://bitbucket.org/birkenfeld/pygments-main/issues/1251/use-of-commentsingleline-instead-of.
      tokentype == Token.Comment.Singleline or
      (tokentype == Token.Comment and comment_is_inline) ):
        return _GROUP.inline_comment
    if (tokentype == Token.Comment.Multiline or
      (tokentype == Token.Comment and comment_is_block) ):
        return _GROUP.block_comment
    # If the tiebreaker above doesn't classify a Token.Comment, then assume it
    # to be an inline comment. This occurs in the Matlab lexer using Pygments
    # 2.0.2.
    if tokentype == Token.Comment:
        return _GROUP.inline_comment

    return _GROUP.other


# Step #3 of lexer_to_rest_
# -------------------------
# Given an iterable of groups, break them into lists based on newlines. The list
# consists of (group, comment_leading_whitespace_length, string) tuples.
def _gather_groups_on_newlines(
    # An iterable of (group, string) pairs provided by
    # ``group_lexer_tokens``.
    iter_grouped,
    # .. _comment_delim_info:
    #
    # An element of COMMENT_DELIMITER_INFO for the language being classified.
    comment_delim_info):

    # Keep a list of (group, string) tuples we're accumulating.
    l = []

    # Keep track of the length of whitespace at the beginning of the body and
    # end portions of a block comment.
    ws_len = 0

    # Accumulate until we find a newline, then yield that.
    for group, string in iter_grouped:
        _debug_print('group = {}, string = {}\n'.format(group, [string]))
        # A given group (such as a block string) may extend across multiple
        # newlines. Split these groups apart first.
        splitlines = string.splitlines(True)

        # Look for block comments spread across multiple lines and label
        # them correctly.
        if len(splitlines) > 1 and group == _GROUP.block_comment:
            group = _GROUP.block_comment_start
            # Look for an indented multi-line comment block. First, determine
            # what the indent must be: (column in which comment starts) +
            # (length of comment delimiter) + (1 space).
            ws_len = comment_delim_info[1] + 1
            for group_, ws_len_, string_ in l:
                ws_len += len(string_)
            # Determine the indent style (all spaces, or spaces followed by a
            # character, typically ``*``). If it's not spaces only, it must
            # be spaces followed by a delimiter.
            #
            # First, get the last character of the block comment delimiter.
            # This is expressed as a 1-character range, so that '' will be
            # returned if the index is past the end of the string. Perl's PODs
            # consist of ``=whatever text you want\n``, meaning the entire line
            # should be discarded. To make this "easy", I define
            # comment_delim_info[1] as a very large number, so that the entire
            # line will be discarded. Hence, the need for the hack below.
            last_delim_char = string[comment_delim_info[1] - 1:
                                     comment_delim_info[1]]
            if _is_space_indented_line(splitlines[1], ws_len, last_delim_char,
              len(splitlines) == 1, comment_delim_info):
                is_indented_line = _is_space_indented_line
            else:
                is_indented_line = _is_delim_indented_line

            # Look at the second and following lines to see if their indent is
            # consistent.
            for i, line in enumerate(splitlines[1:]):
                if not is_indented_line(line, ws_len, last_delim_char,
                  len(splitlines) - 2 == i, comment_delim_info):
                    # It's inconsistent. Set ws_len to 0 to signal that this
                    # isn't an indented block comment.
                    ws_len = 0
                    break

        for index, split_str in enumerate(splitlines):
            # Accumulate results.
            l.append( (group, ws_len, split_str) )

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

        # We've output a group; reset the ws_len to 0 in case the group just
        # output was a multi-line block comment with ws_len > 0.
        ws_len = 0

    # Output final group, if one is still accumulating.
    if l:
        yield l


# Block comment indentation processing
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# #. A single line: ``/* comment */``. No special handling needed.
# #. Multiple lines, indented with spaces. For example:
#
#    .. code-block:: c
#       :linenos:
#
#       Column:  1
#       1234567890234567
#
#         /* A multi-
#
#            line
#         WRONG INDENTATION
#              string
#          */
#
#    In the code above, the text of the comment begins at column 6 of line 4,
#    with the letter A. Therefore, line 7 lacks the necessary 6-space indent,
#    so that no indententation will be removed from this comment.
#
#    If line 6 was indented properly, the resulting reST would be:
#
#    .. code-block:: rest
#
#       ...rest to indent the left margin of the following text 2 spaces...
#
#       A multi-
#
#       line
#       RIGHT INDENTATION
#         string
#
#       ...rest to end the left margin indent...
#
#    Note that the first 5 characters were stripped off each line, leaving only
#    line 8 indented (preserving its indentation relative to the comment's
#    indentation). Some special cases in doing this processing:
#
#    * Line 5 may contain less than the expected 5 space indent: it could be
#      only a newline. This must be supported with a special case.
#    * The comment closing (line 9) contains just 3 spaces; this is allowed.
#      If there are non-space characters before the closing comment delimiter,
#      they must not occur before column 6. For example,
#
#      .. code-block:: c
#
#         /* A multi-
#            line comment */
#
#      and
#
#      .. code-block:: c
#
#         /* A multi-
#            line comment
#         */
#
#      have consistent indentation. In particular, the last line of a multi-line
#      comment may contain zero or more whitespace chararacters followed by the
#      closing block comment delimiter. However,
#
#      .. code-block:: c
#
#         /* A multi-
#           line comment */
#
#      is not sufficiently indented to qualify for indentation removal.
#
#      So, to recognize:
#
def _is_space_indented_line(
    # A line from a multi-line comment to examine.
    line,
    # The expected indent to check for; a length, in characters.
    indent_len,
    # Placeholder for delimiter expected near the end of an indent (one
    # character). Not used by this function, but this function must take the
    # same parameters as is_delim_indented_line_.
    delim,
    # True if this is the last line of a multi-line comment.
    is_last,
    # See comment_delim_info_.
    comment_delim_info):

    # A line containing only whitespace is always considered valid.
    if line.isspace():
        return True
    # A line beginning with ws_len spaces has the expected indent.
    if len(line) > indent_len and line[:indent_len].isspace():
        return True

    # The closing delimiter will always be followed by a newline, hence the - 1
    # factor.
    line_except_closing_delim = line[:-comment_delim_info[2] - 1]
    # Last line: zero or more whitespaces followed by the closing block comment
    # delimiter is valid. Since ``''.isspace() == False``, check for this case
    # and consider it true.
    if (is_last and (not line_except_closing_delim or
                     line_except_closing_delim.isspace())):
        return True
    # No other correctly indented cases.
    return False


# (continuing from the list above...)
#
# #. Multiple lines, indented with spaces followed by a delimiter. For example:
#
#    .. code-block:: c
#       :linenos:
#
#       Column:  1
#       1234567890123456789
#         /* Multi-
#          *   line
#          *
#          *WRONG INDENTATION
#         *  WRONG INDENTATION
#          */
#
#    The rules are similar to the previous case (indents with space alone).
#    However, there is one special case: line 5 doesn't require a space after
#    the asterisk; a newline is acceptable. If the indentation is corrected, the
#    result is:
#
#    .. code-block:: rest
#
#       ...rest to indent the left margin of the following text 2 spaces...
#
#       Multi-
#         line
#
#       RIGHT INDENTATION
#       RIGHT INDENTATION
#
#       ...rest to end left margin indent...
#
#    So, to recognize:
#
# .. _is_delim_indented_line:
#
def _is_delim_indented_line(
    # A line from a multi-line comment to examine.
    line,
    # The expected indent to check for; a length, in characters.
    indent_len,
    # Delimiter expected near the end of an indent (one character).
    delim,
    # True if this is the last line of a multi-line comment.
    is_last,
    # See comment_delim_info_.
    comment_delim_info):

    # A line the correct number of spaces, followed by a delimiter then either
    # a space or a newline is correctly indented.
    if (len(line) >= indent_len and line[:indent_len - 2].isspace() and
        line[indent_len - 2] == delim and line[indent_len - 1] in '\n '):
        return True
    # Last line possibility: indent_len - 2 spaces followed by the delimiter
    # is a valid indent. For example, an indent of 3 begins with ``/* comment``
    # and can end with ``_*/``, a total of (indent_len == 3) - (2 spaces
    # that are usually a * followed by a space) + (closing delim ``*/`` length
    # of 2 chars) == 3.
    if ( is_last and len(line) == indent_len - 2 +
         comment_delim_info[2] and line[:indent_len - 2].isspace() ):
        return True
    # No other correctly indented cases.
    return False


# Step #4 of lexer_to_rest_
# -------------------------
# Classify the output of ``gather_groups_on_newlines`` into either a code or
# comment with n leading whitespace types. Remove all comment characters.
#
# .. Note::
#
#    This is a destructive edit, instead of a classification. To make this
#    invertible, it needs to be non-destructive. The idea:
#
#    * Output s, the entire line as a string, if it's not a reST comment.
#      Currently, it outputs -1, s.
#    * Output whitespace characters or '', opening comment delimiter and
#      space, comment text, closing comment delimiter or '', newline).
#      Currently, it outputs len(leading whitespace characters), comment text +
#      newline.
def _classify_groups(
    # An iterable of [(group1, string1_no_newline), (group2, string2_no_newline),
    # ..., (groupN, stringN_ending_newline)], produced by
    # ``gather_groups_on_newlines``.
    iter_gathered_groups,
    # See comment_delim_info_.
    comment_delim_info):

    # Keep track of block comment state.
    is_block_rest_comment = False

    # Walk through groups.
    for l in iter_gathered_groups:
        _debug_print('[(group, ws_len, string), ...] = {}\n'.format(l))

        if _is_rest_comment(l, is_block_rest_comment, comment_delim_info):

            first_group, first_ws_len, first_string = l[0]
            # The type = # of leading whitespace characters, or 0 if none.
            if first_group == _GROUP.whitespace:
                # Encode this whitespace in the type, then drop it.
                type_ = len(first_string)
                l.pop(0)
                first_group, first_ws_len, first_string = l[0]
            # For body or end block comments, use the indent set by at the
            # beginning of the comment. Otherwise, there is no indent, so
            # set it to 0.
            elif not _is_block_body_or_end(first_group):
                type_ = 0

            # Update the block reST state.
            if first_group == _GROUP.block_comment_start:
                is_block_rest_comment = True

            # Strip all comment characters off the strings and combine them.
            string = ''.join([_remove_comment_delim(group, string,
              comment_delim_info) for group, ws_len, string in l])
            # Remove the inital space character from the first comment,
            # or ws_len chars from body or end comments.
            if _is_block_body_or_end(first_group):
                # Some of the body or end block lines may be just whitespace.
                # Don't strip these: the line may be too short or we might
                # remove a newline. Or, this might be inconsistent indentation
                # in which ws_len == 0, in which case we should also strip
                # nothing.
                if not string.isspace() and first_ws_len > 0:
                    # The first ws_len - 1 characters should be stripped.
                    string = string[first_ws_len - 1:]
                    # The last character, if it's a space, should also be
                    # stripped.
                    if string[0] == ' ':
                        string = string[1:]
            # A comment of ``//\n`` qualifies as a reST comment, but should
            # not have the ``\n`` stripped off. Avoid this case. Otherwise,
            # handle the more typical ``// comment`` case, in which the space
            # after the comment delimiter should be removed.
            elif len(string) > 0 and string[0] == ' ':
                string = string[1:]

        # Everything else is considered code.
        else:
            type_ = -1
            string = ''.join([string for group, ws_len, string in l])
            is_block_rest_comment = False

        yield type_, string


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
#
# .. note::
#
#    This code isn't used yet -- it's for a rewrite which will support multiple
#    delimiters.
def _remove_beginning_comment_delim(
    # Either the number of characters in the beginning delimiter, or a tuple of
    # strings which give all valie beginning comment delimiters.
    beginning_comment_delim_seq,
    # The string which start with the delimiter to be removed.
    string):

    # Loop through all delimiters.
    for bcd in beginning_comment_delim_seq:
        # If we find one at the beginning of the string, strip it off.
        if string.startswith(bcd):
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
    group_tuple, ws_len_tuple, string_tuple = list(zip(*line_list))
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
    # The cases are:
    #
    # 1. ``// comment, //\n, #`` -> reST comment. Note that in some languages
    #    (Python is one example), the newline isn't included in the comment.
    # 2. ``//comment`` -> not a reST comment.
    # 3. ``/* comment, /*\n`` -> reST comment
    # 4. Any block comment body or end for which its block start was a reST
    #    comment -> reST comment.
    # 5. ``/**/`` -> a reST comment. (I could see this either as reST or not;
    #    because it was simpler, I picked reST.)
    #
    # Begin by checking case #4 above.
    if is_block_rest_comment and _is_block_body_or_end(first_group):
        return True
    # To check the other cases, first remove the comment delimiter so we can
    # examine the next character following the delimiter.
    first_comment_text = _remove_comment_delim(first_group, first_string, lexer)
    first_char_is_rest = ( (len(first_comment_text) > 0 and
                          first_comment_text[0] in (' ', '\n')) or
                          len(first_comment_text) == 0 )
    if first_char_is_rest and not _is_block_body_or_end(first_group):
        return True
    return False


# Determine if this group is either a block comment body or a block comment end.
def _is_block_body_or_end(group):
    return group in (_GROUP.block_comment_body, _GROUP.block_comment_end)



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
# | .. code-block:: Python3  | Do something ::         | .. code-block:: html              |
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
# | .. code-block:: Python3  | Do something            | .. code-block:: html              |
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
# | .. code-block:: Python3  | One space indent ::     | .. code-block:: html              |
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
# | .. code-block:: Python3  | One space indent        | .. code-block:: html              |
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
# | .. code-block:: Python3  | No indent               | .. code-block:: html              |
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
# | .. code-block:: Python3  |  No indent              | .. code-block:: html              |
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
# | .. code-block:: Python3  |  .. fenced-code::       | .. code-block:: html              |
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
# | .. code-block:: Python3  |  .. fenced-code::       | .. code-block:: html              |
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
# .. _summary_and_implementation:
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

    # Keep track of the current line number.
    line = 1

    for type_, string in classified_lines:
        _debug_print('type_ = {}, line = {}, string = {}\n'.format(type_, line, [string]))

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
            else:
                # Add an indent if needed.
                if type_ > 0:
                    out_file.write('\n.. raw:: html\n\n'
                      ' <div class="CodeChat-indent" style="margin-left:{}em;">\n\n'.format(0.5*type_))
                # Specify the line number in the source, so that errors will be
                # accurately reported. This isn't necessary in code blocks,
                # since errors can't occur.
                #
                # After this directive, the following text may be indented,
                # which would make it a part of the ``set-line`` directive! So,
                # include an empty comment to terminate the ``set-line``, making
                # any following indents a separate syntatical element. See the
                # end of `reST comment syntax <http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#comments>`_
                # for more discussion.
                out_file.write('\n.. set-line:: {}\n\n..\n\n'.format(line - 4))

        # Output string based on state. All code needs an inital space to
        # place it inside the fenced-code block.
        if type_ == -1:
            out_file.write(' ')
        out_file.write(string)

        # Update the state.
        current_type = type_
        line += 1

    # When done, exit the last state.
    _exit_state(current_type, out_file)


# Supporting routines
# """""""""""""""""""
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


# Supporting reST directives
# """"""""""""""""""""""""""
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

        # Mark all fenced code with a specific class, for styling.
        self.options['classes'] = ['fenced-code']

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

# This directive allows changing the line number at which errors will be
# reported. ``.. set-line:: 10`` makes the current line report as line 10,
# regardless of its actual location in the file.
class _SetLine(Directive):

    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {}
    has_content = False

    def run(self):
        line = int(self.arguments[0])

        # The ``input_lines`` class (see docutils.statemachine.ViewList)
        # maintains two lists, ``data`` and ``items``. ``data`` is a list of
        # strings, one per line, of reST to process. ``items`` is a list of
        # ``(source, offset)`` giving the source of each line and the offset of
        # each line from the beginning of its source. Modifying the offset will
        # change the reported error location.
        il = self.state_machine.input_lines
        # Line renumbering should begin at this offset in ``il.items``, which is
        # the line currently being processed.
        line_offset = self.state_machine.line_offset
        current_source = il.items[line_offset][0]

        # Walk through the current ``input_lines`` up through all its parents.
        while il:
            # Walk from the current line to the end of the current file, rewriting the
            # offset (that is, the effective line number).
            line_ = line
            for index in range(line_offset, len(il.items)):
                source, old_offset = il.items[index]
                # If the source file changes, stop renumbering. The
                # ``current_source`` must have been included; only renumber
                # this, not lines from another source which included
                # ``current_source``.
                if source != current_source:
                    break
                il.items[index] = (source, line_)
                line_ += 1

            # Adjust the offset when moving up to the parent.
            if il.parent:
                line_offset += il.parent_offset
            il = il.parent

        # This directive create no nodes.
        return []

# Register the new fenced code block directive with docutils.
directives.register_directive('fenced-code', _FencedCodeBlock)
directives.register_directive('set-line', _SetLine)
