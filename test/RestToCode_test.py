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
# RestToCode_test.py - Unit testing
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
# Local application imports
# -------------------------
from CodeChat.RestToCode import rest_to_code
from CodeChat.CodeToRest import code_to_rest_string


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

error_str = "This was not recognised as valid reST. Please check your input and try again."

# This acutally tests rest to code by giving 'rest_to_code' reST derived from 'code_to_rest_string'
# It then completes one round trip from reST to code to reST to code again. The two codes are tested
# against each other to verify that the program is round trip stable.
class TestRestToCode(object):
# C-like language tests
# =====================
    # multi-test: Check that the given code's output is correct over several
    # C-like languages.
    def mt(self, code_str, expected_rest_str, alias_seq=('C', 'C', 'C++',
      'Java', 'ActionScript', 'C#', 'D', 'Go', 'JavaScript', 'Objective-C',
      'Rust', 'Scala', 'Swift', 'verilog', 'systemverilog', 'Dart', 'Juttle',
      'Objective-J', 'TypeScript', 'Arduino', 'Clay', 'CUDA', 'eC', 'MQL',
      'nesC', 'Pike', 'SWIG', 'Vala', 'Zephir', 'Haxe')):

        for alias in alias_seq:

            rest = code_to_rest_string(code_str, alias=alias)
            code = rest_to_code(rest, alias)
            rest2 = code_to_rest_string(code_str, alias=alias)
            code2 = rest_to_code(rest2, alias)
            assert code == code2

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

    # Blank code
    def test_19_blank(self):
        self.mt('', '')

    # Just Newline Character
    def test_19_blank(self):
        self.mt('\n', '')

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

    # Perl. (currently not available)
    """def test_45(self):
        self.mt('print "Hello World!"\n'
                '# Comment here\n',
                bf +
                ' print "Hello World!"\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['Perl6', 'Perl'])

    def test_46(self):
        self.mt('print "Hello World!"\n',
                bf +
                ' print "Hello World!"\n' +
                ef, ['Perl6', 'Perl'])

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
                'multi-\n'
                'line\n'
                'comment\n'
                '\n', ['Perl'])

    # New comment syntax in Perl6. No PODs supported.
    def test_49(self):
        self.mt('#`( embedded comment)\n',
                sl(-3) +
                'embedded comment\n', ['Perl6'])"""

    # S.
    def test_50(self):
        self.mt('# Comment here\n',
                sl(-3) +
                'Comment here\n', ['S'])

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

    # MXML.
    def test_101(self):
        self.mt('Hello World!\n'
                '<!---\n'
                'multi-\n'
                'line\n'
                'comment\n'
                '-->\n',
                bf +
                ' Hello World!\n' +
                ef +
                sl(-2) +
                '\nmulti-\n'
                'line\n'
                'comment\n\n', ['MXML'])

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

    # VHDL.
    def test_80(self):
        self.mt('assert false report "Hello World!"\n'
                '-- Comment here\n',
                bf +
                ' assert false report "Hello World!"\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['vhdl'])

    # COBOL.
    def test_81_a(self):
        self.mt('       DISPLAY "Hello World!".\n'
                '      * Comment here\n',
                bf +
                '        DISPLAY "Hello World!".\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['COBOL'])

    def test_81_b(self):
        self.mt('      / Comment here\n',
                sl(-3) +
                'Comment here\n', ['COBOL'])

    def test_81_c(self):
        self.mt('       DISPLAY "Hello World!"\n'
                '      / Comment here\n',
                bf +
                '        DISPLAY "Hello World!"\n' +
                ef +
                sl(-2) +
                'Comment here\n', ['COBOL'])

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

# DocString Testing
# =================
    # Single Line.
    def test_84_a(self):
        self.mt('def foo():\n'
                '    \"""single-line docstring.\"""\n'
                '    pass\n',
                bf +
                ' def foo():\n' +
                ef +
                div(2.0, -2) +
                'single-line docstring.\n' +
                div_end +
                bf +
                '     pass\n' +
                ef, ['Python3'])

    # Single Line, with incorrect syntax.
    def test_84_b(self):
        self.mt('def foo():\n'
                '    \"""single-line docstring.\"""\n'
                '    if (1 <> 2):\n'
                '        pass\n',
                bf +
                ' def foo():\n' +
                '     \"""single-line docstring.\"""\n'
                '     if (1 <> 2):\n'
                '         pass\n' +
                ef, ['Python'])

    # Multi Line.
    def test_85(self):
        self.mt('def foo():\n'
                '    \"""multi-\n'
                '    line\n'
                '    docstring.\n'
                '    \"""\n'
                '    pass\n',
                bf +
                ' def foo():\n' +
                ef +
                div(2.0, -2) +
                'multi-\n'
                'line\n'
                'docstring.\n'
                '\n' +
                div_end +
                bf +
                '     pass\n' +
                ef, ['Python3'])

    # Multiple comments.
    def test_86(self):
        self.mt('\"""Module docstring.\"""\n'
                '\n'
                'def foo():\n'
                '    \"""Function docstring.\"""\n'
                '    pass\n'
                '\n'
                'class bar():\n'
                '    \"""Class docstring.\"""\n'
                '\n'
                '    def one(self):\n'
                '        \"""Method (actually function) docstring.\"""\n'
                '        pass\n',
                sl(-3) +
                'Module docstring.\n' +
                bf +
                ' \n'
                ' def foo():\n' +
                ef +
                div(2.0, 0) +
                'Function docstring.\n' +
                div_end +
                bf +
                '     pass\n'
                ' \n'
                ' class bar():\n' +
                ef +
                div(2.0, 4) +
                'Class docstring.\n' +
                div_end +
                bf +
                ' \n'
                '     def one(self):\n' +
                ef +
                div(4.0, 7) +
                'Method (actually function) docstring.\n' +
                div_end +
                bf +
                '         pass\n' +
                ef, ['Python3'])


class TestRestToCode_ERR_Catching(object):

    # Error testing main code
    def et(self, rest, alias_seq=('C', 'C', 'C++',
      'Java', 'ActionScript', 'C#', 'D', 'Go', 'JavaScript', 'Objective-C',
      'Rust', 'Scala', 'Swift', 'verilog', 'systemverilog', 'Dart', 'Juttle',
      'Objective-J', 'TypeScript', 'Arduino', 'Clay', 'CUDA', 'eC', 'MQL',
      'nesC', 'Pike', 'SWIG', 'Vala', 'Zephir', 'Haxe')):

        for alias in alias_seq:

            code = rest_to_code(rest, alias)
            assert code == error_str


    def test_1(self):
        self.et('hello')

    def test_2(self):
        self.et('\n'
                '.. fenced-code::\n'
                '\n'
                ' Beginning fene\n')