# .. Copyright (C) 2012-2016 Bryan A. Jones.
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
# This test bench exercises the CodeToRest module. First, set up for
# development (see :ref:`To-package`). To run, execute ``py.test`` from the
# command line. Note the period in this command -- ``pytest`` does **NOT** work
# (it is a completely different program).
#
# Imports
# =======
# These are listed in the order prescribed by `PEP 8
# <http://www.python.org/dev/peps/pep-0008/#imports>`_.
#
# Library imports
# ---------------
from io import StringIO
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
from CodeChat.CodeToRest import code_to_rest_string, code_to_html_file
from CodeChat.CodeToRest import _remove_comment_delim, _group_lexer_tokens, \
  _gather_groups_on_newlines, _is_rest_comment, _classify_groups, \
  _generate_rest, _is_space_indented_line, _is_delim_indented_line, _GROUP
from CodeChat.CommentDelimiterInfo import COMMENT_DELIMITER_INFO


# Define some commonly-used strings to make testing less verbose. Per the
# :ref:`summary_and_implementation`, "Code blocks must be preceeded and followed
# by a removed marker (fences)." These two functions (begin fence == ``bf``, end
# fence == ``ef``) contain the fence strings ``_generate_rest`` produces.
bf = ('\n'
      '.. fenced-code::\n'
      '\n'
      ' Beginning fence\n')
ef = (' Ending fence\n'
      '\n'
      '..\n'
      '\n')

# ``_generate_rest`` inserts a ``<div>`` to format indented comments followed by
# a ``set-line`` directive to show line numbers of the comments correctly. This
# function generates the same string.
def div(
   # The size of the indent, in em. Each space = 0.5 em, so a 3-space indent would be ``size=1.5``.
   size,
   # The line number  passed to ``sl`` below.
   line):

    return ('\n'
            '.. raw:: html\n'
            '\n <div style="margin-left:{}em;">\n'
            '\n').format(size) + sl(line)

# After a ``<div>``, ``_generate_rest`` inserts a ``set-line`` directive. This
# function provides that directive as a string.
def sl(
  # The line number for the set-line directive, which is comment_line - 4. For
  # example, for a comment in the first line of the file, implying
  # comment_line == 1, use ``sl(-3)``.
  line):
    return ('\n'
            '.. set-line:: {}\n'
            '\n'
            '..\n'
            '\n').format(line)

# The standard string which marks the end of a ``<div>``.
div_end = ('\n'
           '.. raw:: html\n'
           '\n'
           ' </div>\n'
           '\n'
           '..\n'
           '\n')

# This acutally tests using ``code_to_rest_string``, since that makes
# ``code_to_rest`` easy to call.
class TestCodeToRest(object):
# C-like language tests
# =====================
    # multi-test: Check that the given code's output is correct over several
    # C-like languages.
    def mt(self, code_str, expected_rest_str, alias_seq=('C', 'C', 'C++',
      'Java', 'ActionScript', 'C#', 'D', 'Go', 'JavaScript', 'Objective-C',
      'Rust', 'Scala', 'Swift', 'verilog', 'systemverilog')):

        for alias in alias_seq:
            rest = code_to_rest_string(code_str, alias=alias)
            assert rest == expected_rest_str

    # A single line of code.
    def test_1(self):
        self.mt('testing',
                bf +
                ' testing\n' +
                ef)

    # A single line of code, with an ending ``\n``.
    def test_2(self):
        self.mt('testing\n',
                bf +
                ' testing\n' +
                ef)

    # Several lines of code, with arbitrary indents.
    def test_3(self):
        self.mt('testing\n'
                '  test 1\n'
                ' test 2\n'
                '   test 3',
                bf +
                ' testing\n'
                '   test 1\n'
                '  test 2\n'
                '    test 3\n' +
                ef)

    # A single line comment, no trailing ``\n``.
    def test_4(self):
        self.mt('// testing',
                sl(-3) +
                'testing\n')

    # A single line comment, trailing ``\n``.
    def test_5(self):
        self.mt('// testing\n',
                sl(-3) +
                'testing\n')

    # A multi-line comment.
    def test_5a(self):
        self.mt('// testing\n'
                '// more testing',
                sl(-3) +
                'testing\n'
                'more testing\n')

    # A single line comment with no space after the comment should be treated
    # like code.
    def test_6(self):
        self.mt('//testing',
                bf +
                ' //testing\n' +
                ef)

    # A singly indented single-line comment.
    def test_7(self):
        self.mt(' // testing',
                div(0.5, -3) +
                'testing\n' +
                div_end)

    # A doubly indented single-line comment.
    def test_8(self):
        self.mt('  // testing',
                div(1.0, -3) +
                'testing\n' +
                div_end)

    # A doubly indented multi-line comment.
    def test_9(self):
        self.mt('  // testing\n'
                '  // more testing',
                div(1.0, -3) +
                'testing\n'
                'more testing\n' +
                div_end)

    # Code to comment transition.
    def test_9a(self):
        self.mt('testing\n'
                '// test',
                bf +
                ' testing\n' +
                ef +
                sl(-2) +
                'test\n')

    # A line with just the comment char, but no trailing space.
    def test_10(self):
        self.mt('//',
                sl(-3) +
                '\n')

    # Make sure an empty string works.
    def test_12(self):
        self.mt('',
                bf +
                ' \n' +
                ef)

    # Make sure Unicode works.
    def test_13(self):
        self.mt('ю',
                bf +
                ' ю\n' +
                ef)

    # Code to comment transition.
    def test_14(self):
        self.mt('testing\n'
                '// Comparing',
                bf +
                ' testing\n' +
                ef +
                sl(-2) +
                'Comparing\n')

    # Code to comment transition, with leading blank code lines.
    def test_15(self):
        self.mt(' \n'
                'testing\n'
                '// Comparing',
                bf + '  \n'
                ' testing\n' +
                ef +
                sl(-1) +
                'Comparing\n')

    # Code to comment transition, with trailing blank code lines.
    def test_16(self):
        self.mt('testing\n'
                '\n'
                '// Comparing',
                bf + ' testing\n'
                ' \n' +
                ef +
                sl(-1) +
                'Comparing\n')

    # Comment to code transition.
    def test_17(self):
        self.mt('// testing\n'
                'Comparing',
                sl(-3) +
                'testing\n' +
                bf +
                ' Comparing\n' +
                ef)

    # Comment to code transition, with leading blank code lines.
    def test_18(self):
        self.mt('// testing\n'
                '\n'
                'Comparing',
                sl(-3) +
                'testing\n' +
                bf +
                ' \n'
                ' Comparing\n' +
                ef)

    # Comment to code transition, with trailing blank code lines.
    def test_19(self):
        self.mt('// testing\n'
                'Comparing\n'
                '\n',
                sl(-3) +
                'testing\n' +
                bf +
                ' Comparing\n' +
                ef)

    # Block comments.
    def test_19_1(self):
        self.mt('/* multi-\n'
                'line\n'
                'comment */\n',
                sl(-3) +
                'multi-\n'
                'line\n'
                'comment \n')

    # Comments with headings.
    def test_19_a(self):
        self.mt('  // Heading\n'
                '  // =======\n'
                '  // Body.\n',
                div(1.0, -3) +
                'Heading\n'
                '=======\n'
                'Body.\n' +
                div_end)

    # Indented comments following code.
    def test_19_b(self):
        self.mt('Code\n'
                '//  Comment\n',
                bf +
                ' Code\n' +
                ef +
                sl(-2) +
                ' Comment\n')
#
# Block comment indent removal: indents with spaces
# -------------------------------------------------
    # Removal of leading whitespace in block comments.
    def test_19_1_1(self):
        self.mt('/* multi-\n'
                '   line\n'
                '   comment\n'
                ' */\n',
                sl(-3) +
                'multi-\n'
                'line\n'
                'comment\n'
                ' \n')

    # Inconsistent whitespace -- no removal.
    def test_19_1_2(self):
        self.mt('/* multi-\n'
                ' line\n'
                '   comment\n'
                ' */\n',
                sl(-3) +
                'multi-\n'
                ' line\n'
                '   comment\n'
                ' \n')

    # Too little whitespace to line up with initial comment.
    def test_19_1_3(self):
        self.mt('/* multi-\n'
                ' line\n'
                ' comment */\n',
                sl(-3) +
                'multi-\n'
                ' line\n'
                ' comment \n')

    # Indented block comments with whitespace removal.
    def test_19_1_4(self):
        self.mt(' /* multi-\n'
                '    line\n'
                '    comment\n'
                '  */\n',
                div(0.5, -3) +
                'multi-\n'
                'line\n'
                'comment\n'
                '  \n' +
                div_end)
#
# Block comment indent removal: indents with delimiters
# -----------------------------------------------------
    # Removal of leading whitespace in block comments.
    def test_19_1_5(self):
        self.mt('/* multi-\n'
                ' * line\n'
                ' * comment\n'
                ' */\n',
                sl(-3) +
                'multi-\n'
                'line\n'
                'comment\n'
                ' \n')

    # Inconsistent whitespace -- no removal.
    def test_19_1_6(self):
        self.mt('/* multi-\n'
                '*line\n'
                ' * comment\n'
                ' */\n',
                sl(-3) +
                'multi-\n'
                '*line\n'
                ' * comment\n'
                ' \n')

    # Too little whitespace to line up with initial comment.
    def test_19_1_7(self):
        self.mt('/* multi-\n'
                '*line\n'
                '*comment */\n',
                sl(-3) +
                'multi-\n'
                '*line\n'
                '*comment \n')

    # Indented block comments with whitespace removal.
    def test_19_1_8(self):
        self.mt(' /* multi-\n'
                '  * line\n'
                '  * comment\n'
                '  */\n',
                div(0.5, -3) +
                'multi-\n'
                'line\n'
                'comment\n'
                '  \n' +
                div_end)
#
# Other block comment testing
# ---------------------------
    def test_19_2(self):
        self.mt('/*multi-\n'
                'line\n'
                'comment */\n',
                bf +
                ' /*multi-\n'
                ' line\n'
                ' comment */\n' +
                ef)

    def test_19_3(self):
        self.mt('/* block */ //inline\n',
                sl(-3) +
                'block  inline\n')

    def test_19_4(self):
        self.mt('/* block */ /**/\n',
                sl(-3) +
                'block  \n')

    def test_19_5(self):
        self.mt('/* multi-\n'
                'line\n'
                'comment */ //inline\n',
                sl(-3) +
                'multi-\n'
                'line\n'
                'comment  inline\n')
#
# Other languages
# ---------------
    # A bit of Python testing.
    def test_20(self):
        self.mt('# testing\n'
                '#\n'
                '# Trying\n',
                sl(-3) +
                'testing\n'
                '\n'
                'Trying\n',
                ('Python', 'Python3'))

    def test_21(self):
        self.mt('#\n',
                sl(-3) +
                '\n', ('Python', 'Python3'))

    def test_22(self):
        self.mt(' \n'
                'foo()\n'
                '\n'
                '# bar\n',
                bf +
                '  \n'
                ' foo()\n'
                ' \n' +
                ef +
                sl(0) +
                'bar\n',
                ('Python', 'Python3'))

    # Some CSS.
    def test_23(self):
        self.mt(' \n'
                'div {}\n'
                '\n'
                '/* comment */\n',
                bf +
                '  \n'
                ' div {}\n'
                ' \n' +
                ef +
                sl(0) +
                'comment \n', ['CSS'])

    def test_24(self):
        self.mt('/* multi-\n'
                'line\n'
                'comment */\n',
                sl(-3) +
                'multi-\n'
                'line\n'
                'comment \n', ['CSS'])

    # Assembly (NASM).
    def test_25(self):
        self.mt('; Comment\n'
                ' \n'
                'start: bra start\n'
                ' \n',
                sl(-3) +
                'Comment\n' +
                bf +
                '  \n'
                ' start: bra start\n'
                '  \n' +
                ef, ['NASM'])

    # Bash.
    def test_26(self):
        self.mt('# Comment\n'
                ' \n'
                'echo "hello world"\n'
                ' \n',
                sl(-3) +
                'Comment\n' +
                bf +
                '  \n'
                ' echo "hello world"\n'
                '  \n' +
                ef, ['Bash'])

    # PHP. While the `PHP manual
    # <http://php.net/manual/en/language.basic-syntax.comments.php>`_ confirms
    # support for ``//`` inline comments, Pygments doesn't appear to support
    # these; they are output as code.
    def test_27(self):
        self.mt("<?php\n"
                "echo 'Hello world'\n"
                "// Comment1\n"
                "# Comment2\n"
                "/* Comment3 */\n",
                bf +
                " <?php\n"
                " echo 'Hello world'\n" +
                " // Comment1\n" +
                ef +
                sl(0) +
                "Comment2\n"
                "Comment3 \n", ['PHP'])

    # Batch file.
    def test_28(self):
        self.mt('echo Hello\n'
                'rem Comment\n',
                bf +
                ' echo Hello\n' +
                ef +
                sl(-2) +
                'Comment\n', ['Batch'])

    # MATLAB.
    def test_29(self):
        self.mt('a = [1 2 3 4];\n'
                '% Hello\n'
                '  %{\n'
                '     to the\n'
                '     world\n'
                '  %}\n',
                bf +
                ' a = [1 2 3 4];\n' +
                ef +
                sl(-2) +
                'Hello\n' +
                div(1.0, -1) +
                '\n'
                'to the\n'
                'world\n'
                '  \n' +
                div_end, ['Matlab'])

    # Ruby.
    def test_30(self):
        self.mt('puts "Hello World!"\n'
                '# Comment here\n',
                bf +
                ' puts "Hello World!"\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['Ruby'])

    def test_31(self):
        self.mt('puts "Hello World!"\n',
                bf +
                ' puts "Hello World!"\n' +
                ef, ['Ruby'])

    def test_32(self):
        self.mt('=begin\n'
                'multi-\n'
                'line\n'
                'comment\n'
                '=end\n',
                sl(-3) +
                '\n'
                'multi-\n'
                'line\n'
                'comment\n'
                '\n', ['Ruby'])

    # SQL.
    def test_33(self):
        self.mt('SELECT column0,column1\n'
                'FROM table\n',
                bf +
                ' SELECT column0,column1\n' +
                ' FROM table\n' +
                ef, ['SQL'])

    def test_34(self):
        self.mt('SELECT aBetter, example\n'
                '-- with interlaced comments\n'
                'FROM ourTestUnit\n',
                bf +
                ' SELECT aBetter, example\n' +
                ef +
                sl(-2) +
                'with interlaced comments\n' +
                bf +
                ' FROM ourTestUnit\n' +
                ef, ['SQL'])

    # Powershell.
    def test_35(self):
        self.mt('Write-Host "Hello World!"\n'
                '# comment here\n',
                bf +
                ' Write-Host "Hello World!"\n' +
                ef +
                sl(-2) +
                'comment here\n', ['Powershell'])

    def test_36(self):
        self.mt('<# testing block comment beginning here\n'
                ' continuing on this line\n'
                'and ending on this line #>\n',
                sl(-3) +
                'testing block comment beginning here\n'
                ' continuing on this line\n'
                'and ending on this line \n', ['Powershell'])

    # GAS. Pygments does not lex multi-line comments, therefore CodeChat 
    # does not support them.
    def test_37_a(self):
        self.mt('# comment\n',
                sl(-3) +
                'comment\n', ['GAS'])

    def test_37_b(self):
        self.mt('        .text\n'
                '# comment\n',
                bf +
                '         .text\n' +
                ef +
                sl(-2) +
                'comment\n', ['GAS'])

    # autohotkey.
    """
    def test_39_a(self):
        self.mt('; Comment here\n',
                sl(-3) +
                'Comment here\n', ['autohotkey'])

    def test_39_b(self):
        self.mt('Msgbox, Hello World!\n'
                '; Comment here\n',
                bf +
                ' Msgbox, Hello World!\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['autohotkey'])
    """
    def test_40(self):
        self.mt('/*\n'
                'multi-\n'
                'line\n'
                'comment\n'
                '*/\n',
                sl(-3) +
                '\nmulti-\n'
                'line\n'
                'comment\n\n', ['autohotkey'])

    # Prolog.
    def test_41(self):
        self.mt('?- write("Hello world!").\n'
                '% Comment here\n',
                bf +
                ' ?- write("Hello world!").\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['Prolog'])

    def test_42(self):
        self.mt('/*\n'
                'multi-\n'
                'line\n'
                'comment\n'
                '*/\n',
                sl(-3) +
                '\nmulti-\n'
                'line\n'
                'comment\n\n', ['Prolog'])

    # AutoIt.
    def test_43(self):
        self.mt('ConsoleWrite(\'Hello World!\')\n'
                '; Comment here\n',
                bf +
                ' ConsoleWrite(\'Hello World!\')\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['AutoIt'])

    def test_44(self):
        self.mt('#cs\n'
                'multi-\n'
                'line\n'
                'comment\n'
                '#ce\n',
                sl(-3) +
                '\nmulti-\n'
                'line\n'
                'comment\n\n', ['AutoIt'])


    # Perl.
    def test_45(self):
        self.mt('print "Hello World!"\n'
                '# Comment here\n',
                bf +
                ' print "Hello World!"\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['Perl'])

    def test_46(self):
        self.mt('print "Hello World!"\n',
                bf +
                ' print "Hello World!"\n' +
                ef, ['Perl'])

    def test_47_a(self):
        self.mt('=pod\n'
                'multi-\n'
                'line\n'
                'comment\n'
                '=cut\n',
                sl(-3) +
                'multi-\n'
                'line\n'
                'comment\n'
                '\n', ['Perl'])

    def test_47_b(self):
        self.mt('=for\n'
                'multi-\n'
                'line\n'
                'comment\n'
                '=cut\n',
                sl(-3) +
                'multi-\n'
                'line\n'
                'comment\n'
                '\n', ['Perl'])

    def test_47_c(self):
        self.mt('=begin\n'
                'multi-\n'
                'line\n'
                'comment\n'
                '=cut\n',
                sl(-3) +
                '\n'
                'multi-\n'
                'line\n'
                'comment\n'
                '\n', ['Perl'])

    # Perl6.
    """
    def test_48_a(self):
        self.mt('# Comment here\n',
                sl(-3) +
                'Comment here\n', ['Perl6'])

    def test_48_b(self):
        self.mt('say "Hello World!";\n'
                '# Comment here\n',
                bf +
                ' say "Hello World!";\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['Perl6'])

    def test_49_a(self):
        self.mt('#\'(\n'
                'multi-\n'
                'line\n'
                'comment\n'
                ')\n',
                'multi-\n'
                'line\n'
                'comment\n', ['Perl6'])

    def test_49_b(self):
        self.mt('=begin\n'
                'multi-\n'
                'line\n'
                'comment\n'
                '=end\n',
                'multi-\n'
                'line\n'
                'comment\n', ['Perl6'])
    """

    # S.
    def test_50(self):
        self.mt('# Comment here\n',
                sl(-3) +
                'Comment here\n', ['S'])

    """
    def test_51(self):
        self.mt('#iffalse\n'
                'multi-\n'
                'line\n'
                'comment\n'
                '#endif\n',
                sl(-3) +
                'multi\n'
                'line\n'
                'comment\n', ['S'])
    """

    # Haskell.
    def test_52(self):
        self.mt('putStrLn "Hello World!"\n'
                '-- Comment here\n',
                bf +
                ' putStrLn "Hello World!"\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['Haskell'])

    def test_53(self):
        self.mt('{-\n'
                'multi-\n'
                'line\n'
                'comment\n'
                '-}\n',
                sl(-3) +
                '\nmulti-\n'
                'line\n'
                'comment\n\n', ['Haskell'])

    # Delphi.
    def test_54(self):
        self.mt('writeln(\'Hello World!\');\n'
                '// Comment here\n',
                bf +
                ' writeln(\'Hello World!\');\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['Delphi'])

    def test_55(self):
        self.mt('{\n'
                'multi-\n'
                'line\n'
                'comment\n'
                '}\n',
                sl(-3) +
                '\nmulti-\n'
                'line\n'
                'comment\n\n', ['Delphi'])

    # AppleScript.
    def test_56_a(self):
        self.mt('-- Comment here\n',
                sl(-3) +
                'Comment here\n', ['AppleScript'])

    def test_56_b(self):
        self.mt('display dialog "Hello World!"\n'
                '-- Comment here\n',
                bf +
                ' display dialog "Hello World!"\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['AppleScript'])

    def test_57(self):
        self.mt('(*\n'
                'multi-\n'
                'line\n'
                'comment\n'
                '*)\n',
                sl(-3) +
                '\nmulti-\n'
                'line\n'
                'comment\n\n', ['AppleScript'])

    # Common Lisp.
    def test_58(self):
        self.mt('(princ (code-char 69))\n'
                '; Comment here\n',
                bf +
                ' (princ (code-char 69))\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['common-lisp'])

    def test_59(self):
        self.mt('#|\n'
                'multi-\n'
                'line\n'
                'comment\n'
                '|#\n',
                sl(-3) +
                '\nmulti-\n'
                'line\n'
                'comment\n\n', ['common-lisp'])

    # Lua.
    def test_60(self):
        self.mt('print(\'Hello World!\')\n'
                '-- Comment here\n',
                bf +
                ' print(\'Hello World!\')\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['Lua'])

    def test_61(self):
        self.mt('--[[\n'
                'multi-\n'
                'line\n'
                'comment\n'
                ']]\n',
                sl(-3) +
                '\nmulti-\n'
                'line\n'
                'comment\n\n', ['Lua'])

    # Clojure.
    def test_62(self):
        self.mt('; Comment here\n',
                sl(-3) +
                'Comment here\n', ['Clojure'])

    # Scheme.
    def test_63(self):
        self.mt('Hello World!\n'
                '; Comment here\n',
                bf +
                ' Hello World!\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['Scheme'])

    # HTML.
    """
    def test_64_a(self):
        self.mt('; Comment here\n',
                sl(-3) +
                'Comment here\n', ['HTML'])

    def test_64_b(self):
        self.mt('Hello World!\n'
                '; Comment here\n',
                bf +
                ' Hello World!\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['HTML'])
    """
    def test_65(self):
        self.mt('<!--\n'
                'multi-\n'
                'line\n'
                'comment\n'
                '-->\n',
                sl(-3) +
                '\nmulti-\n'
                'line\n'
                'comment\n\n', ['HTML'])

    # Fortran.
    def test_66(self):
        self.mt('write(*,*) "Hello World!"\n'
                '! Comment here\n',
                bf +
                ' write(*,*) "Hello World!"\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['Fortran'])

    # APL.
    def test_67(self):
        self.mt('Hello World!\n'
                '⍝ Comment here\n',
                bf +
                ' Hello World!\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['APL'])

    # Makefile.
    def test_68(self):
        self.mt('@echo \'Hello World!\'\n'
                '# Comment here\n',
                bf +
                ' @echo \'Hello World!\'\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['Makefile'])

    # RPMSpec.
    def test_69(self):
        self.mt('echo \'Hello World!\'\n'
                '# Comment here\n',
                bf +
                ' echo \'Hello World!\'\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['spec'])

    # Nimrod.
    def test_70_a(self):
        self.mt('# Comment here\n',
                sl(-3) +
                'Comment here\n', ['Nimrod'])

    def test_70_b(self):
        self.mt('Hello World!\n'
                '# Comment here\n',
                bf +
                ' Hello World!\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['Nimrod'])

    # NSIS.
    def test_71_a(self):
        self.mt('; Comment here\n',
                sl(-3) +
                'Comment here\n', ['NSIS'])

    def test_71_b(self):
        self.mt('# Comment here\n',
                sl(-3) +
                'Comment here\n', ['NSIS'])

    def test_71_c(self):
        self.mt('DetailPrint "Hello World!"\n'
                '; Comment here\n',
                bf +
                ' DetailPrint "Hello World!"\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['NSIS'])

    def test_72_d(self):
        self.mt('DetailPrint "Hello World!"\n'
                '# Comment here\n',
                bf +
                ' DetailPrint "Hello World!"\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['NSIS'])

    # TeX.
    def test_72(self):
        self.mt('Hello World!\n'
                '% Comment here\n',
                bf +
                ' Hello World!\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['TeX'])

    # Erlang.
    def test_73(self):
        self.mt('Hello World!.\n'
                '% Comment here\n',
                bf +
                ' Hello World!.\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['Erlang'])

    # QBasic.
    def test_74(self):
        self.mt('PRINT "Hello World!";\n'
                '\' Comment here\n',
                bf +
                ' PRINT "Hello World!";\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['QBasic'])

    # VB.net.
    def test_75(self):
        self.mt('Console.WriteLine("Hello World!")\n'
                '\' Comment here\n',
                bf +
                ' Console.WriteLine("Hello World!")\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['VB.net'])

    # REBOL.
    def test_76(self):
        self.mt('view [text "Hello World!"]\n'
                '; Comment here\n',
                bf +
                ' view [text "Hello World!"]\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['REBOL'])

    # LLVM.
    def test_77_a(self):
        self.mt('; Comment here\n',
                sl(-3) +
                'Comment here\n', ['LLVM'])

    def test_77_b(self):
        self.mt('Hello World!\n'
                '; Comment here\n',
                bf +
                ' Hello World!\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['LLVM'])

    # Ada.
    def test_78(self):
        self.mt('Put_Line("Hello World!");\n'
                '-- Comment here\n',
                bf +
                ' Put_Line("Hello World!");\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['Ada'])

    # Eiffel.
    def test_79(self):
        self.mt('print ("Hello World!%N")\n'
                '-- Comment here\n',
                bf +
                ' print ("Hello World!%N")\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['Eiffel'])

    # Vhdl.
    """
    def test_80(self):
        self.mt('assert false report "Hello World!"\n'
                '-- Comment here\n',
                bf +
                ' assert false report "Hello World!"\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['Vhdl'])
    """

    # COBOL.
    """
    def test_81_a(self):
        self.mt('*> Comment here\n',
                sl(-3) +
                'Comment here\n', ['COBOL'])

    def test_81_b(self):
        self.mt('DISPLAY "Hello World!".\n'
                '* Comment here\n',
                bf +
                ' DISPLAY "Hello World!".\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['COBOL'])

    def test_81_c(self):
        self.mt('/ Comment here\n',
                sl(-3) +
                'Comment here\n', ['COBOL'])

    def test_81_d(self):
        self.mt('DISPLAY "Hello World!"\n'
                '/ Comment here\n',
                bf +
                ' DISPLAY "Hello World!"\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['COBOL'])

    def test_81_e(self):
        self.mt('-- Comment here\n',
                sl(-3) +
                'Comment here\n', ['COBOL'])
    """

    # INI.
    def test_82_a(self):
        self.mt('; Comment here\n',
                sl(-3) +
                'Comment here\n', ['INI'])

    def test_82_b(self):
        self.mt('Hello World!\n'
                '; Comment here\n',
                bf +
                ' Hello World!\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['INI'])

    # YAML.
    def test_83_a(self):
        self.mt('# Comment here\n',
                sl(-3) +
                'Comment here\n', ['YAML'])

    def test_83_b(self):
        self.mt('invoice: 34843\n'
                '# Comment here\n',
                bf +
                ' invoice: 34843\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['YAML'])

# Fenced code block testing
# =========================
# Use docutils to test converting a fenced code block to HTML.

class TestRestToHtml(object):
    # Use docutils to convert reST to HTML, then look at the resulting string.
    def t(self, rest):
        html = core.publish_string(rest, writer_name='html').decode('utf-8')
        # Snip out just the body. Note that ``.`` needs the `re.DOTALL flag
        # <https://docs.python.org/2/library/re.html#re.DOTALL>`_ so that it
        # can match newlines.
        bodyMo = re.search('<body>\n'
                           '(.*)</body>', html, re.DOTALL)
        body = bodyMo.group(1)
        # docutils wraps the resulting HTML in a <div>. Strip that out as well.
        divMo = re.search('<div class="document"[^>]*>\n'
                          '+(.*)\n'
                          '</div>', body,
                          re.DOTALL)
        div = divMo.group(1)
        return div

    # Test the harness -- can we pass a simple string through properly?
    def test_1(self):
        assert self.t('testing') == '<p>testing</p>'

    # Test the harness -- can we pass some code through properly?
    def test_2(self):
        assert (self.t('.. code::\n'
                       '\n testing') ==
                       '<pre class="code literal-block">\n'
                       'testing\n'
                       '</pre>')

    # See if a fenced code block that's too short produces an error.
    def test_3(self):
        assert ('Fenced code block must contain at least two lines.' in
                self.t('.. fenced-code::') )
    def test_4(self):
        assert ('Fenced code block must contain at least two lines.' in
                self.t('.. fenced-code::\n'
                       '\n'
                       ' First fence') )

    # Verify that a fenced code block with just fences complains about empty
    # output.
    def test_5(self):
        assert ('Content block expected for the '
        in self.t('.. fenced-code::\n'
                  '\n'
                  ' First fence\n'
                  ' Second fence\n') )
#
# Check newline preservation **without** syntax highlighting
# ----------------------------------------------------------
    # Check output of a one-line code block surrounded by fences.
    def test_6(self):
        assert (self.t('.. fenced-code::\n'
                       '\n First fence'
                       '\n testing'
                       '\n'
                       ' Second fence\n') ==
                       '<pre class="code literal-block">\n'
                       'testing\n'
                       '</pre>')

    # Check that leading newlines are preserved.
    def test_7(self):
        assert (self.t('.. fenced-code::\n'
                       '\n'
                       ' First fence\n'
                       '\n testing'
                       '\n'
                       ' Second fence\n') ==
                       '<pre class="code literal-block">\n'
                       ' \n'
                       'testing\n'
                       '</pre>')

    # Check that trailing newlines are preserved.
    def test_8(self):
        assert (self.t('.. fenced-code::\n'
                       '\n'
                       ' First fence\n'
                       ' testing\n'
                       '\n'
                       ' Second fence\n') ==
                       '<pre class="code literal-block">\n'
                       'testing\n'
                       ' \n'
                       '</pre>')
#
# Check newline preservation **with** syntax highlighting
# -------------------------------------------------------
    # Check output of a one-line syntax-highlighted code block surrounded by
    # fences.
    def test_9(self):
        assert (self.t('.. fenced-code:: python\n'
                       '\n'
                       ' First fence\n'
                       ' testing\n'
                       ' Second fence\n') ==
                       '<pre class="code python literal-block">\n'
                       '<span class="name">testing</span>\n'
                       '</pre>')

    # Check that leading newlines are preserved with syntax highlighting.
    def test_10(self):
        assert (self.t('.. fenced-code:: python\n'
                       '\n'
                       ' First fence\n'
                       '\n'
                       ' testing\n'
                       ' Second fence\n') ==
                       '<pre class="code python literal-block">\n'
                       ' \n'
                       '<span class="name">testing</span>\n'
                       '</pre>')

    # Check that trailing newlines are preserved with syntax highlighting.
    def test_11(self):
        assert (self.t('.. fenced-code:: python\n'
                       '\n'
                       ' First fence\n'
                       ' testing\n'
                       '\n'
                       ' Second fence\n') ==
                       '<pre class="code python literal-block">\n'
                       '<span class="name">testing</span>\n'
                       ' \n'
                       '</pre>')

    # Test translation of indented headings. Note that the enclosing <div>,
    # which surrounds the heading in reST, is moved to only surround the body in
    # the resulting HTML.
    def test_12(self):
        assert (self.t(div(1.0, -3) +
                       'Heading\n'
                       '=======\n'
                       'Body.\n' +
                       div_end) ==
                       '<h1 class="title">Heading</h1>\n'
                       '\n'
                       '<div style="margin-left:1.0em;"><!--  -->\n'
                       '<p>Body.</p>\n'
                       '</div><!--  -->')

    # Test translation of an indented comment following code.
    def test_13(self):
        assert (self.t(bf +
                       ' Code\n' +
                       ef +
                       sl(-2) +
                       ' Comment\n') ==
                       '<pre class="code literal-block">\n'
                       'Code\n'
                       '</pre>\n'
                       '<!--  -->\n'
                       '<!--  -->\n'
                       '<blockquote>\n'
                       'Comment</blockquote>')

#
# Poor coverage of code_to_html_file
# ==================================
class TestCodeToHtmlFile(object):
    def test_1(self):
        code_to_html_file('CodeChat/CodeToRestSphinx.py')
#
# Tests of lexer_to_code and subroutines
# ======================================
c_lexer = COMMENT_DELIMITER_INFO[get_lexer_by_name('C').name]
py_lexer = COMMENT_DELIMITER_INFO[get_lexer_by_name('Python').name]
class TestCodeToRestNew(object):
    # Check that a simple file or string is tokenized correctly.
    def test_1(self):
        test_py_code = '# A comment\nan_identifier\n'
        test_token_list = [(Token.Comment.Single, '# A comment'),
                           (Token.Text, '\n'),
                           (Token.Name, 'an_identifier'),
                           (Token.Text, '\n')]

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
        token_group = list(_group_lexer_tokens(token_iter, False, False))
        # But split the two into separate lists for unit tests.
        group_list, string_list = list(zip(*token_group))
        assert group_list == (
          _GROUP.other,               # The #include.
          _GROUP.whitespace,          # The space after #include.
          _GROUP.other,               # <stdio.h>\n
          _GROUP.whitespace,          # \n
          _GROUP.block_comment,       # The /* comment */.
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
        token_group = list(_group_lexer_tokens(token_iter, True, False))
        assert token_group == [(_GROUP.whitespace, '\n')]

    # Check gathering of groups by newlines.
    def test_4(self):
        lexer = get_lexer_by_name('c')
        token_iter = lex(self.test_c_code, lexer)
        token_group = _group_lexer_tokens(token_iter, False, False)
        gathered_group = list(_gather_groups_on_newlines(token_group,
                                                         (1, 2, 2)))
        expected_group = [
          [(_GROUP.other, 0, '#include'),
            (_GROUP.whitespace, 0, ' '),
            (_GROUP.other, 0, '<stdio.h>\n')],
          [(_GROUP.whitespace, 0, '\n')],
          [(_GROUP.block_comment_start, 3, '/* A multi-\n')],
          [(_GROUP.block_comment_body,  3, '   line\n')],
          [(_GROUP.block_comment_end,   3, '   comment */'),
           (_GROUP.whitespace, 0, '\n')],
          [(_GROUP.whitespace, 0, '\n')],
          [(_GROUP.other, 0, 'main(){'), (_GROUP.whitespace, 0, '\n')],
          [(_GROUP.whitespace, 0, '  '),
           (_GROUP.inline_comment, 0, '// Empty.\n')],
          [(_GROUP.other, 0, '}'), (_GROUP.whitespace, 0, '\n')] ]
        assert gathered_group == expected_group
#
# remove_comment_chars tests
# --------------------------
    def test_4a(self):
        assert _remove_comment_delim(_GROUP.whitespace,
          '    ', c_lexer) == '    '

    def test_4b(self):
        assert ( _remove_comment_delim(_GROUP.other, 'an_identifier', c_lexer)
                == 'an_identifier' )

    def test_4c(self):
        assert _remove_comment_delim(_GROUP.inline_comment,
          '// comment\n', c_lexer) == ' comment\n'

    def test_4d(self):
        assert _remove_comment_delim(_GROUP.block_comment,
          '/* comment */', c_lexer) == ' comment '

    def test_4e(self):
        assert _remove_comment_delim(_GROUP.block_comment_start,
          '/* comment\n', c_lexer) == ' comment\n'

    def test_4f(self):
        assert _remove_comment_delim(_GROUP.block_comment_body,
          'comment\n', c_lexer) == 'comment\n'

    def test_4g(self):
        assert _remove_comment_delim(_GROUP.block_comment_end,
          'comment */', c_lexer) == 'comment '

    # Newlines should be preserved.
    def test_4h(self):
        assert _remove_comment_delim(_GROUP.inline_comment,
          '//\n', c_lexer) == '\n'

    def test_4i(self):
        assert _remove_comment_delim(_GROUP.block_comment_start,
          '/*\n', c_lexer) == '\n'

    def test_4j(self):
        assert _remove_comment_delim(_GROUP.block_comment_body,
          '\n', c_lexer) == '\n'

    def test_4k(self):
        assert _remove_comment_delim(_GROUP.block_comment_end,
          '*/', c_lexer) == ''
#
# _is_space_indented_line tests
# -----------------------------
    # Tests of block comment body indentation using spaces.
    def test_4_1(self):
        assert _is_space_indented_line('comment\n',
                                       3, '*', False, (2, 2, 2)) == False
        assert _is_space_indented_line('  comment\n',
                                       3, '*', False, (2, 2, 2)) == False
        assert _is_space_indented_line('   comment\n',
                                       3, '*', False, (2, 2, 2)) == True

    # Tests of block comment end indentation using spaces.
    def test_4_2(self):
        assert _is_space_indented_line('*/',
                                       3, '*', True, (2, 2, 2)) == True
        assert _is_space_indented_line(' */',
                                       3, '*', True, (2, 2, 2)) == True

    # Tests of block comment body indentation using spaces.
    def test_4_3(self):
        assert _is_delim_indented_line('comment\n',
                                       3, '*', False, (2, 2, 2)) == False
        assert _is_delim_indented_line(' *comment\n',
                                       3, '*', False, (2, 2, 2)) == False
        assert _is_delim_indented_line(' * comment\n',
                                       3, '*', False, (2, 2, 2)) == True
        assert _is_delim_indented_line(' *\n',
                                       3, '*', False, (2, 2, 2)) == True

    # Tests of block comment end indentation using spaces.
    def test_4_4(self):
        assert _is_delim_indented_line('*/',
                                       3, '*', True, (2, 2, 2)) == False
        assert _is_delim_indented_line(' */',
                                       3, '*', True, (2, 2, 2)) == True
#
# _is_rest_comment tests
# ----------------------
    # newline only
    def test_4aa1(self):
        assert not _is_rest_comment([
          (_GROUP.whitespace, 0, '\n')], False, c_lexer)

    # // comments with and without preceeding whitespace.
    def test_4aa(self):
        assert _is_rest_comment([
          (_GROUP.inline_comment, 0, '// comment\n')], False, c_lexer)

    def test_4ab(self):
        assert _is_rest_comment([
          (_GROUP.inline_comment, 0, '//\n')], False, c_lexer)

    def test_4ac(self):
        assert _is_rest_comment([
          (_GROUP.whitespace, 0, '  '),
          (_GROUP.inline_comment, 0, '// comment\n')], False, c_lexer)

    def test_4ad(self):
        assert _is_rest_comment([
          (_GROUP.whitespace, 0, '  '),
          (_GROUP.inline_comment, 0, '//\n')], False, c_lexer)

    # //comments with and without preceeding whitespace.
    def test_4ae(self):
        assert not _is_rest_comment([
          (_GROUP.inline_comment, 0, '//comment\n')], False, c_lexer)

    def test_4af(self):
        assert not _is_rest_comment([
          (_GROUP.whitespace, 0, '  '),
          (_GROUP.inline_comment, 0, '//comment\n')], False, c_lexer)

    ## A /**/ comment.
    def test_4ag1(self):
        assert _is_rest_comment([
          (_GROUP.block_comment, 0, '/**/')], False, c_lexer)

    ## A /* */ comment.
    def test_4ag2(self):
        assert _is_rest_comment([
          (_GROUP.block_comment, 0, '/* */')], False, c_lexer)

    ## /* comments */ with and without preceeding whitespace.
    def test_4ag(self):
        assert _is_rest_comment([
          (_GROUP.block_comment, 0, '/* comment */')], False, c_lexer)

    def test_4ah(self):
        assert _is_rest_comment([
          (_GROUP.whitespace, 0, '  '),
          (_GROUP.block_comment, 0, '/* comment */')], False, c_lexer)

    ## /*comments */ with and without preceeding whitespace.
    def test_4ai(self):
        assert not _is_rest_comment([
          (_GROUP.block_comment, 0, '/*comment */')], False, c_lexer)

    def test_4aj(self):
        assert not _is_rest_comment([
          (_GROUP.whitespace, 0, '  '),
          (_GROUP.block_comment, 0, '/*comment */')], False, c_lexer)

    ## /* comments with and without preceeding whitespace.
    def test_4ak(self):
        assert _is_rest_comment([
          (_GROUP.block_comment_start, 0, '/* comment\n')], False, c_lexer)

    def test_4al(self):
        assert _is_rest_comment([
          (_GROUP.whitespace, 0, '  '),
          (_GROUP.block_comment_start, 0, '/* comment\n')], False, c_lexer)

    ## /*comments with and without preceeding whitespace.
    def test_4am(self):
        assert not _is_rest_comment([
          (_GROUP.block_comment_start, 0, '/*comment\n')], False, c_lexer)

    def test_4an(self):
        assert not _is_rest_comment([
          (_GROUP.whitespace, 0, '  '),
          (_GROUP.block_comment_start, 0, '/*comment\n')], False, c_lexer)

    # multi-line body and end comments.
    def test_4ao(self):
        assert _is_rest_comment([
          (_GROUP.block_comment_body, 0, 'comment\n')], True, c_lexer)

    def test_4ao1(self):
        assert _is_rest_comment([
          (_GROUP.block_comment_body, 0, '\n')], True, c_lexer)

    def test_4ap(self):
        assert not _is_rest_comment([
          (_GROUP.block_comment_body, 0, 'comment\n')], False, c_lexer)

    def test_4aq(self):
        assert _is_rest_comment([
          (_GROUP.block_comment_end, 0, 'comment */')], True, c_lexer)

    def test_4ar(self):
        assert not _is_rest_comment([
          (_GROUP.block_comment_end, 0, 'comment */')], False, c_lexer)

    ## Multiple /* comments */ on a line.
    def test_4as(self):
        assert _is_rest_comment([
          (_GROUP.block_comment, 0, '/* comment1 */'),
          (_GROUP.whitespace, 0, '  '),
          (_GROUP.block_comment, 0, '/*comment2 */')], False, c_lexer)

    def test_4at(self):
        assert _is_rest_comment([
          (_GROUP.whitespace, 0, '  '),
          (_GROUP.block_comment, 0, '/* comment1 */'),
          (_GROUP.whitespace, 0, '  '),
          (_GROUP.block_comment, 0, '/*comment2 */')], False, c_lexer)

    # Mixed comments and code.
    def test_4au(self):
        assert not _is_rest_comment([
          (_GROUP.whitespace, 0, '  '),
          (_GROUP.block_comment, 0, '/* comment */'),
          (_GROUP.other, 0, 'foo();')], False, c_lexer)

    def test_4av(self):
        assert not _is_rest_comment([
          (_GROUP.block_comment_end, 0, 'comment */'),
          (_GROUP.other, 0, 'foo();')], True, c_lexer)

    def test_4aw(self):
        assert _is_rest_comment([
          (_GROUP.inline_comment, 0, '#'),
          (_GROUP.whitespace, 0, '\n')], True, py_lexer)
#
# Classifier tests
# ----------------
    # Test comment.
    def test_5(self):
        cg = list( _classify_groups([[
          (_GROUP.inline_comment, 0, '// comment\n')]], c_lexer) )
        assert cg == [(0, 'comment\n')]

    # Test whitespace comment.
    def test_6(self):
        cg = list( _classify_groups([[
          (_GROUP.whitespace, 0, '  '),
          (_GROUP.inline_comment, 0, '// comment\n')]], c_lexer) )
        assert cg == [(2, 'comment\n')]

    # Test code.
    def test_7(self):
        cg = list( _classify_groups([[
          (_GROUP.whitespace, 0, '  '),
          (_GROUP.other, 0, 'foo();'),
          (_GROUP.whitespace, 0, '\n')]], c_lexer) )
        assert cg == [(-1, '  foo();\n')]

    # Test multi-line comments.
    def test_8(self):
        cg = list( _classify_groups([
          [(_GROUP.block_comment_start, 0, '/* multi-\n')],
          [(_GROUP.block_comment_body,  3, '   line\n')],
          [(_GROUP.block_comment_end,   3, '   comment */')]], c_lexer) )
        assert cg == [(0, 'multi-\n'),
                      (0, 'line\n'),
                      (0, 'comment ')]

    def test_9(self):
        cg = list( _classify_groups([
          [(_GROUP.block_comment_start, 2, '/*multi-\n')],
          [(_GROUP.block_comment_body,  2, '  line\n')],
          [(_GROUP.block_comment_end,   2, '  comment*/')]], c_lexer) )
        assert cg == [(-1, '/*multi-\n'),
                      (-1, '  line\n'),
                      (-1, '  comment*/')]

    # From code to classification.
    def test_10(self):
        lexer = get_lexer_by_name('c')
        token_iter = lex(self.test_c_code, lexer)
        token_group = _group_lexer_tokens(token_iter, False, False)
        gathered_group = _gather_groups_on_newlines(token_group, (2, 2, 2))
        classified_group = list( _classify_groups(gathered_group, c_lexer) )
        assert classified_group == [(-1, '#include <stdio.h>\n'),
                                    (-1, '\n'),
                                    ( 0, 'A multi-\n'),
                                    ( 0, 'line\n'),
                                    ( 0, 'comment \n'),
                                    (-1, '\n'),
                                    (-1, 'main(){\n'),
                                    ( 2,   'Empty.\n'),
                                    (-1, '}\n')]
#
# reST generation tests
# ---------------------
    def test_11(self):
        out_stringio = StringIO()
        generated_rest = _generate_rest(
          [(-1, '\n'),
           (-1, 'code\n'),
           (-1, '\n')], out_stringio)
        assert (out_stringio.getvalue() ==
          # Note: Not using a """ string, since the string trailing whitespace option in
          # Enki would remove some of the one-space lines.
          bf +
          ' \n'
          ' code\n' +
          ' \n' +
          ef)

    def test_12(self):
        out_stringio = StringIO()
        generated_rest = _generate_rest(
          [(0, '\n'),
           (0, 'comment\n'),
           (0, '\n')], out_stringio)
        assert (out_stringio.getvalue() == sl(-3) +
"""
comment

""")
    def test_13(self):
        out_stringio = StringIO()
        generated_rest = _generate_rest(
          [(3, '\n'),
           (3, 'comment\n'),
           (3, '\n')], out_stringio)
        assert (out_stringio.getvalue() == div(1.5, -3) + '\ncomment\n\n' + div_end)

