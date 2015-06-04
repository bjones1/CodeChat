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
# *********************************
# CodeToRest_test.py - Unit testing
# *********************************
# This test bench exercises the CodeToRest module. To run, execute ``py.test``
# from the command line. Note the period in this command -- ``pytest`` does
# **NOT** work (it is a completely different program).
#
# .. highlight:: none
#
# Imports
# =======
# These are listed in the order prescribed by `PEP 8 <http://www.python.org/dev/peps/pep-0008/#imports>`_.
#
# Library imports
# ---------------
import re
#
# Third-party imports
# -------------------
# Used to run docutils.
from docutils import core
from pygments.token import Token
from pygments import lex
from pygments.lexers import get_lexer_by_name
#
# Local application imports
# -------------------------
from .CodeToRest import code_to_rest_string, code_to_html_file
from .CodeToRest import *
from .CodeToRest import _remove_comment_delim, _group_lexer_tokens, \
  _gather_groups_on_newlines, _is_rest_comment, _classify_groups, \
  _generate_rest, _GROUP


# This acutally tests using ``code_to_rest_string``, since that makes
# ``code_to_rest`` easy to call.
class TestCodeToRest(object):
    # Given a string and a language, run it through ``code_to_rest`` and return
    # the resulting string.
    def t(self, in_string, extension = '.c'):
        return code_to_rest_string(in_string, filename='foo' + extension)

    # A single line of code, without an ending ``\n``.
    def test_1(self):
        ret = self.t('testing')
        assert ret ==  '\n.. fenced-code::\n\n Beginning fence\n testing\n Ending fence\n\n'

    # A single line of code, with an ending ``\n``.
    def test_2(self):
        ret = self.t('testing\n')
        assert ret ==  '\n.. fenced-code::\n\n Beginning fence\n testing\n Ending fence\n\n'

    # Several lines of code, with arbitrary indents.
    def test_3(self):
        ret = self.t('testing\n  test 1\n test 2\n   test 3')
        assert ret == '\n.. fenced-code::\n\n Beginning fence\n testing\n   test 1\n  test 2\n    test 3\n Ending fence\n\n'

    # A single line comment, no trailing ``\n``.
    def test_4(self):
        ret = self.t('// testing')
        assert ret == 'testing\n'

    # A single line comment, trailing ``\n``.
    def test_5(self):
        ret = self.t('// testing\n')
        assert ret == 'testing\n'

    # A multi-line comment.
    def test_5a(self):
        ret = self.t('// testing\n// more testing')
        assert ret == 'testing\nmore testing\n'

    # A single line comment with no space after the comment should be treated
    # like code.
    def test_6(self):
        ret = self.t('//testing')
        assert ret == '\n.. fenced-code::\n\n Beginning fence\n //testing\n Ending fence\n\n'

    # A singly indented single-line comment.
    def test_7(self):
        ret = self.t(' // testing')
        assert ret == '\n.. raw:: html\n\n <div style="margin-left:0.5em;">\n\ntesting\n\n.. raw:: html\n\n </div>\n\n'

    # A doubly indented single-line comment.
    def test_8(self):
        ret = self.t('  // testing')
        assert ret == '\n.. raw:: html\n\n <div style="margin-left:1.0em;">\n\ntesting\n\n.. raw:: html\n\n </div>\n\n'

    # A doubly indented multi-line comment.
    def test_9(self):
        ret = self.t('  // testing\n  // more testing')
        assert ret == '\n.. raw:: html\n\n <div style="margin-left:1.0em;">\n\ntesting\nmore testing\n\n.. raw:: html\n\n </div>\n\n'

    # Code to comment transition.
    def test_9a(self):
        ret = self.t('testing\n// test')
        assert ret == '\n.. fenced-code::\n\n Beginning fence\n testing\n Ending fence\n\ntest\n'

    # A line with just the comment char, but no trailing space.
    def test_10(self):
        ret = self.t('//')
        assert ret == '\n'

    # Make sure an empty string works.
    def test_12(self):
        ret = self.t('')
        assert ret == u'\n.. fenced-code::\n\n Beginning fence\n \n Ending fence\n\n'

    # Make sure Unicode works.
    def test_13(self):
        ret = self.t(u'ю')
        assert ret == u'\n.. fenced-code::\n\n Beginning fence\n ю\n Ending fence\n\n'

    # Code to comment transition.
    def test_14(self):
        ret = self.t('testing\n// Comparing')
        assert ret ==  '\n.. fenced-code::\n\n Beginning fence\n testing\n Ending fence\n\nComparing\n'

    # Code to comment transition, with leading blank code lines.
    def test_15(self):
        ret = self.t(' \ntesting\n// Comparing')
        assert ret ==  '\n.. fenced-code::\n\n Beginning fence\n  \n testing\n Ending fence\n\nComparing\n'

    # Code to comment transition, with trailing blank code lines.
    def test_16(self):
        ret = self.t('testing\n\n// Comparing')
        assert ret ==  '\n.. fenced-code::\n\n Beginning fence\n testing\n \n Ending fence\n\nComparing\n'

    # Comment to code transition.
    def test_17(self):
        ret = self.t('// testing\nComparing')
        assert ret ==  'testing\n\n.. fenced-code::\n\n Beginning fence\n Comparing\n Ending fence\n\n'

    # Comment to code transition, with leading blank code lines.
    def test_18(self):
        ret = self.t('// testing\n\nComparing')
        assert ret ==  'testing\n\n.. fenced-code::\n\n Beginning fence\n \n Comparing\n Ending fence\n\n'

    # Comment to code transition, with trailing blank code lines.
    def test_19(self):
        ret = self.t('// testing\nComparing\n\n')
        assert ret ==  'testing\n\n.. fenced-code::\n\n Beginning fence\n Comparing\n Ending fence\n\n'

    #
    def test_20(self):
        ret = self.t('# testing\n#\n# Trying\n', '.py')
        assert ret ==  'testing\n\nTrying\n'

    def test_21(self):
        ret = self.t('#\n', '.py')
        assert ret ==  '\n'


# Fenced code block testing
# =========================
# Use docutils to test converting a fenced code block to HTML.
class TestRestToHtml(object):
    # Use docutils to convert reST to HTML, then look at the resulting string.
    def t(self, rest):
        html = core.publish_string(rest, writer_name='html')
        # Snip out just the body. Note that ``.`` needs the `re.DOTALL flag
        # <https://docs.python.org/2/library/re.html#re.DOTALL>`_ so that it
        # can match newlines.
        bodyMo = re.search('<body>\n(.*)</body>', html, re.DOTALL)
        body = bodyMo.group(1)
        # docutils wraps the resulting HTML in a <div>. Strip that out as well.
        divMo = re.search('<div class="document">\n\n\n(.*)\n</div>', body, re.DOTALL)
        div = divMo.group(1)
        return div

    # Test the harness -- can we pass a simple string through properly?
    def test_1(self):
        assert self.t('testing') == '<p>testing</p>'

    # Test the harness -- can we pass some code through properly?
    def test_2(self):
        assert (self.t('.. code::\n\n testing') ==
                '<pre class="code literal-block">\ntesting\n</pre>')

    # See if a fenced code block that's too short produces an error.
    def test_3(self):
        assert ('Fenced code block must contain at least two lines.' in
                self.t('.. fenced-code::') )
    def test_4(self):
        assert ('Fenced code block must contain at least two lines.' in
                self.t('.. fenced-code::\n\n First fence') )

    # Verify that a fenced code block with just fences complains about empty
    # output.
    def test_5(self):
        assert ('Content block expected for the '
        in self.t('.. fenced-code::\n\n First fence\n Second fence\n') )

# Check newline preservation **without** syntax highlighting
# ----------------------------------------------------------
    # Check output of a one-line code block surrounded by fences.
    def test_6(self):
        assert (self.t('.. fenced-code::\n\n First fence\n testing\n Second fence\n') ==
                '<pre class="code literal-block">\ntesting\n</pre>')

    # Check that leading newlines are preserved.
    def test_7(self):
        assert (self.t('.. fenced-code::\n\n First fence\n\n testing\n Second fence\n') ==
                '<pre class="code literal-block">\n \ntesting\n</pre>')

    # Check that trailing newlines are preserved.
    def test_8(self):
        assert (self.t('.. fenced-code::\n\n First fence\n testing\n\n Second fence\n') ==
                '<pre class="code literal-block">\ntesting\n \n</pre>')

# Check newline preservation **with** syntax highlighting
# -------------------------------------------------------
    # Check output of a one-line syntax-highlighted code block surrounded by fences.
    def test_9(self):
        assert (self.t('.. fenced-code:: python\n\n First fence\n testing\n Second fence\n') ==
                '<pre class="code python literal-block">\n<span class="name">testing</span>\n</pre>')

    # Check that leading newlines are preserved with syntax highlighting.
    def test_10(self):
        assert (self.t('.. fenced-code:: python\n\n First fence\n\n testing\n Second fence\n') ==
                '<pre class="code python literal-block">\n \n<span class="name">testing</span>\n</pre>')

    # Check that trailing newlines are preserved with syntax highlighting.
    def test_11(self):
        assert (self.t('.. fenced-code:: python\n\n First fence\n testing\n\n Second fence\n') ==
                '<pre class="code python literal-block">\n<span class="name">testing</span>\n \n</pre>')

# Poor coverage of code_to_html_file
# ==================================
class TestCodeToHtmlFile(object):
    def test_1(self):
        code_to_html_file('CodeToRestSphinx.py')

# Tests of lexer_to_code and subroutines
# ======================================
c_lexer = get_lexer_by_name('C')
py_lexer = get_lexer_by_name('Python')
class TestCodeToRestNew(object):
    # Check that a simple file or string is tokenized correctly.
    def test_1(self):
        test_py_code = '# A comment\nan_identifier\n'
        test_token_list = [(Token.Comment, u'# A comment'),
                           (Token.Text, u'\n'),
                           (Token.Name, u'an_identifier'),
                           (Token.Text, u'\n')]

        lexer = get_lexer_by_name('python')
        token_list = list( lex(test_py_code, lexer) )
        assert token_list == test_token_list

    test_c_code = \
"""#include <stdio.h>

/* A multi-
   line
   comment */

main(){
  // Empty.
}\n"""

    # Check grouping of a list of tokens.
    def test_2(self):
        lexer = get_lexer_by_name('c')
        token_iter = lex(self.test_c_code, lexer)
        # Capture both group and string for help in debugging.
        token_group = list(_group_lexer_tokens(token_iter))
        # But split the two into separate lists for unit tests.
        group_list, string_list = zip(*token_group)
        assert group_list == (
          _GROUP.other,               # The #include.
          _GROUP.whitespace,          # Up to the /* comment */.
          _GROUP.block_comment,  # The /* comment */.
          _GROUP.whitespace,          # Up to the code.
          _GROUP.other,               # main(){.
          _GROUP.whitespace,          # Up to the // comment.
          _GROUP.inline_comment, # // commnet.
          _GROUP.other,               # Closing }.
          _GROUP.whitespace, )        # Final \n.

    # Check grouping of an empty string.
    def test_3(self):
        # Note that this will add a newline to the lexed output, since the
        # `ensurenl <http://pygments.org/docs/lexers/>`_ option is True by
        # default.
        lexer = get_lexer_by_name('python')
        token_iter = lex('', lexer)
        # Capture both group and string for help in debugging.
        token_group = list(_group_lexer_tokens(token_iter))
        assert token_group == [(_GROUP.whitespace, u'\n')]

    # Check gathering of groups by newlines.
    def test_4(self):
        lexer = get_lexer_by_name('c')
        token_iter = lex(self.test_c_code, lexer)
        token_group = _group_lexer_tokens(token_iter)
        gathered_group = list(_gather_groups_on_newlines(token_group))
        expected_group = [
          [(_GROUP.other, u'#include <stdio.h>\n')],
          [(_GROUP.whitespace, u'\n')],
          [(_GROUP.block_comment_start, u'/* A multi-\n')],
          [(_GROUP.block_comment_body, u'   line\n')],
          [(_GROUP.block_comment_end, u'   comment */'),
           (_GROUP.whitespace, u'\n')],
          [(_GROUP.whitespace, u'\n')],
          [(_GROUP.other, u'main(){'), (_GROUP.whitespace, u'\n')],
          [(_GROUP.whitespace, u'  '),
           (_GROUP.inline_comment, u'// Empty.\n')],
          [(_GROUP.other, u'}'), (_GROUP.whitespace, u'\n')] ]
        assert gathered_group == expected_group

# remove_comment_chars tests
# --------------------------
    def test_4a(self):
        assert _remove_comment_delim(_GROUP.whitespace, 
          u'    ', c_lexer) == u'    '

    def test_4b(self):
        assert ( _remove_comment_delim(_GROUP.other, u'an_identifier', c_lexer) 
                == u'an_identifier' )

    def test_4c(self):
        assert _remove_comment_delim(_GROUP.inline_comment,
          u'// comment\n', c_lexer) == u' comment\n'

    def test_4d(self):
        assert _remove_comment_delim(_GROUP.block_comment,
          u'/* comment */', c_lexer) == u' comment '

    def test_4e(self):
        assert _remove_comment_delim(_GROUP.block_comment_start,
          u'/* comment\n', c_lexer) == u' comment\n'

    def test_4f(self):
        assert _remove_comment_delim(_GROUP.block_comment_body,
          u'comment\n', c_lexer) == u'comment\n'

    def test_4g(self):
        assert _remove_comment_delim(_GROUP.block_comment_end,
          u'comment */', c_lexer) == u'comment '

    # Newlines should be preserved.
    def test_4h(self):
        assert _remove_comment_delim(_GROUP.inline_comment,
          u'//\n', c_lexer) == u'\n'

    def test_4i(self):
        assert _remove_comment_delim(_GROUP.block_comment_start,
          u'/*\n', c_lexer) == u'\n'

    def test_4j(self):
        assert _remove_comment_delim(_GROUP.block_comment_body,
          u'\n', c_lexer) == u'\n'

    def test_4k(self):
        assert _remove_comment_delim(_GROUP.block_comment_end,
          u'*/', c_lexer) == u''

# _is_rest_comment tests
# ---------------------
    # newline only
    def test_4aa1(self):
        assert not _is_rest_comment([
          (_GROUP.whitespace, u'\n')], False, c_lexer)

    # // comments with and without preceeding whitespace.
    def test_4aa(self):
        assert _is_rest_comment([
          (_GROUP.inline_comment, u'// comment\n')], False, c_lexer)

    def test_4ab(self):
        assert _is_rest_comment([
          (_GROUP.inline_comment, u'//\n')], False, c_lexer)

    def test_4ac(self):
        assert _is_rest_comment([
          (_GROUP.whitespace, u'  '),
          (_GROUP.inline_comment, u'// comment\n')], False, c_lexer)

    def test_4ad(self):
        assert _is_rest_comment([
          (_GROUP.whitespace, u'  '),
          (_GROUP.inline_comment, u'//\n')], False, c_lexer)

    # //comments with and without preceeding whitespace.
    def test_4ae(self):
        assert not _is_rest_comment([
          (_GROUP.inline_comment, u'//comment\n')], False, c_lexer)

    def test_4af(self):
        assert not _is_rest_comment([
          (_GROUP.whitespace, u'  '),
          (_GROUP.inline_comment, u'//comment\n')], False, c_lexer)

    ## A /**/ comment.
    def test_4ag1(self):
        assert _is_rest_comment([
          (_GROUP.block_comment, u'/**/')], False, c_lexer)

    ## A /* */ comment.
    def test_4ag2(self):
        assert _is_rest_comment([
          (_GROUP.block_comment, u'/* */')], False, c_lexer)

    ## /* comments */ with and without preceeding whitespace.
    def test_4ag(self):
        assert _is_rest_comment([
          (_GROUP.block_comment, u'/* comment */')], False, c_lexer)

    def test_4ah(self):
        assert _is_rest_comment([
          (_GROUP.whitespace, u'  '),
          (_GROUP.block_comment, u'/* comment */')], False, c_lexer)

    ## /*comments */ with and without preceeding whitespace.
    def test_4ai(self):
        assert not _is_rest_comment([
          (_GROUP.block_comment, u'/*comment */')], False, c_lexer)

    def test_4aj(self):
        assert not _is_rest_comment([
          (_GROUP.whitespace, u'  '),
          (_GROUP.block_comment, u'/*comment */')], False, c_lexer)

    ## /* comments with and without preceeding whitespace.
    def test_4ak(self):
        assert _is_rest_comment([
          (_GROUP.block_comment_start, u'/* comment\n')], False, c_lexer)

    def test_4al(self):
        assert _is_rest_comment([
          (_GROUP.whitespace, u'  '),
          (_GROUP.block_comment_start, u'/* comment\n')], False, c_lexer)

    ## /*comments with and without preceeding whitespace.
    def test_4am(self):
        assert not _is_rest_comment([
          (_GROUP.block_comment_start, u'/*comment\n')], False, c_lexer)

    def test_4an(self):
        assert not _is_rest_comment([
          (_GROUP.whitespace, u'  '),
          (_GROUP.block_comment_start, u'/*comment\n')], False, c_lexer)

    # multi-line body and end comments.
    def test_4ao(self):
        assert _is_rest_comment([
          (_GROUP.block_comment_body, u'comment\n')], True, c_lexer)

    def test_4ao1(self):
        assert _is_rest_comment([
          (_GROUP.block_comment_body, u'\n')], True, c_lexer)

    def test_4ap(self):
        assert not _is_rest_comment([
          (_GROUP.block_comment_body, u'comment\n')], False, c_lexer)

    def test_4aq(self):
        assert _is_rest_comment([
          (_GROUP.block_comment_end, u'comment */')], True, c_lexer)

    def test_4ar(self):
        assert not _is_rest_comment([
          (_GROUP.block_comment_end, u'comment */')], False, c_lexer)

    ## Multiple /* comments */ on a line.
    def test_4as(self):
        assert _is_rest_comment([
          (_GROUP.block_comment, u'/* comment1 */'),
          (_GROUP.whitespace, u'  '),
          (_GROUP.block_comment, u'/*comment2 */')], False, c_lexer)

    def test_4at(self):
        assert _is_rest_comment([
          (_GROUP.whitespace, u'  '),
          (_GROUP.block_comment, u'/* comment1 */'),
          (_GROUP.whitespace, u'  '),
          (_GROUP.block_comment, u'/*comment2 */')], False, c_lexer)

    # Mixed comments and code.
    def test_4au(self):
        assert not _is_rest_comment([
          (_GROUP.whitespace, u'  '),
          (_GROUP.block_comment, u'/* comment */'),
          (_GROUP.other, u'foo();')], False, c_lexer)

    def test_4av(self):
        assert not _is_rest_comment([
          (_GROUP.block_comment_end, u'comment */'),
          (_GROUP.other, u'foo();')], True, c_lexer)

    def test_4aw(self):
        assert _is_rest_comment([
          (_GROUP.inline_comment, u'#'),
          (_GROUP.whitespace, u'\n')], True, py_lexer)

# Classifier tests
# ----------------
    # Test comment.
    def test_5(self):
        cg = list( _classify_groups([[
          (_GROUP.inline_comment, u'// comment\n')]], c_lexer) )
        assert cg == [(0, u'comment\n')]

    # Test whitespace comment.
    def test_6(self):
        cg = list( _classify_groups([[
          (_GROUP.whitespace, u'  '),
          (_GROUP.inline_comment, u'// comment\n')]], c_lexer) )
        assert cg == [(2, u'comment\n')]

    # Test code.
    def test_7(self):
        cg = list( _classify_groups([[
          (_GROUP.whitespace, u'  '),
          (_GROUP.other, u'foo();'),
          (_GROUP.whitespace, u'\n')]], c_lexer) )
        assert cg == [(-1, u'  foo();\n')]

    # Test multi-line comments.
    def test_8(self):
        cg = list( _classify_groups([
          [(_GROUP.block_comment_start, u'/* multi-\n')],
          [(_GROUP.block_comment_body,  u'   line\n')],
          [(_GROUP.block_comment_end,   u'   comment */')]], c_lexer) )
        assert cg == [(0, u'multi-\n'),
                      (0, u'   line\n'),
                      (0, u'   comment ')]

    def test_9(self):
        cg = list( _classify_groups([
          [(_GROUP.block_comment_start, u'/*multi-\n')],
          [(_GROUP.block_comment_body,  u'  line\n')],
          [(_GROUP.block_comment_end,   u'  comment*/')]], c_lexer) )
        assert cg == [(-1, u'/*multi-\n'),
                      (-1, u'  line\n'),
                      (-1, u'  comment*/')]

    # From code to classification.
    def test_10(self):
        lexer = get_lexer_by_name('c')
        token_iter = lex(self.test_c_code, lexer)
        token_group = _group_lexer_tokens(token_iter)
        gathered_group = _gather_groups_on_newlines(token_group)
        classified_group = list( _classify_groups(gathered_group, c_lexer) )
        assert classified_group == [(-1, u'#include <stdio.h>\n'),
                                    (-1, u'\n'),
                                    ( 0, u'A multi-\n'),
                                    ( 0, u'   line\n'),
                                    ( 0, u'   comment \n'),
                                    (-1, u'\n'),
                                    (-1, u'main(){\n'),
                                    ( 2,   u'Empty.\n'),
                                    (-1, u'}\n')]

# reST generation tests
# ---------------------
    def test_11(self):
        out_stringio = StringIO()
        generated_rest = _generate_rest(
          [(-1, u'\n'),
           (-1, u'code\n'),
           (-1, u'\n')], out_stringio)
        assert (out_stringio.getvalue() ==
# Note: Not using a """ string, since the string trailing whitespace option in
# Enki would remove some of the one-space lines.
'\n' +
'.. fenced-code::\n' +
'\n' +
' Beginning fence\n' +
' \n'
' code\n' +
' \n' +
' Ending fence\n' +
'\n')

    def test_12(self):
        out_stringio = StringIO()
        generated_rest = _generate_rest(
          [(0, u'\n'),
           (0, u'comment\n'),
           (0, u'\n')], out_stringio)
        assert (out_stringio.getvalue() ==
"""
comment

""")
    def test_13(self):
        out_stringio = StringIO()
        generated_rest = _generate_rest(
          [(3, u'\n'),
           (3, u'comment\n'),
           (3, u'\n')], out_stringio)
        assert (out_stringio.getvalue() ==
"""
.. raw:: html

 <div style="margin-left:1.5em;">


comment


.. raw:: html

 </div>

""")

