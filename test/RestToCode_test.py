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
#
# Imports
# =======
# These are listed in the order prescribed by `PEP 8
# <http://www.python.org/dev/peps/pep-0008/#imports>`_.
#
# Third-party imports
# -------------------
# Used to run docutils.
from docutils import io
from tempfile import mkstemp
import os
#
# Local application imports
# -------------------------
from CodeChat.RestToCode import rest_to_code_file, rest_to_code_string, \
    find_file_ext
from CodeChat.CodeToRest import code_to_rest_file, code_to_rest_string




# The string that results from rest_to_code not understanding the material.
error_str = "This was not recognised as valid reST. Please check your input and try again."


class TestRestToCodeErrCatching(object):

    # Error testing main code
    def et(self, rest, alias_seq=('C', 'C', 'C++',
      'Java', 'ActionScript', 'C#', 'D', 'Go', 'JavaScript', 'Objective-C',
      'Rust', 'Scala', 'Swift', 'verilog', 'systemverilog', 'Dart', 'Juttle',
      'Objective-J', 'TypeScript', 'Arduino', 'Clay', 'CUDA', 'eC', 'MQL',
      'nesC', 'Pike', 'SWIG', 'Vala', 'Zephir', 'Haxe')):

        for alias in alias_seq:

            code = rest_to_code_string(rest, alias)
            assert code == error_str


    def test_1(self):
        self.et('hello')

    def test_2(self):
        self.et('\n'
                '.. fenced-code::\n'
                '\n'
                ' Beginning fene\n')


class TestRestToCodeString(object):

    def mt(self, given_code, expected_code, lang):

        rest = code_to_rest_string(given_code, alias=lang)
        code = rest_to_code_string(rest, lang)
        assert code == expected_code


    # Inline comment to code transition
    def test_1(self):
        self.mt('// Comment\n'
                'Code\n',
                '// Comment\n'
                'Code\n',
                'C')

    # Single line block comment  to code transition
    def test_2(self):
        self.mt('/* Single line block comment*/\n'
                'Code\n',
                '// Single line block comment\n'
                'Code\n',
                'C++')

    # Single line block comment  to code transition
    # No inline delimiters
    def test_2b(self):
        self.mt('/* Single line block comment*/\n'
                'Code\n',
                '/* Single line block comment*/\n'
                'Code\n',
                'CSS')

    # Multi-line block comment to code transition
    def test_3(self):
        self.mt('/* Multi-line\n'
                ' * block\n'
                ' * comment*/\n'
                'Code\n',
                '// Multi-line\n'
                '// block\n'
                '// comment\n'
                'Code\n',
                'C')

    # Multi-line block comment to code transition
    # No inline delimiters
    def test_3b(self):
        self.mt('/* Multi-line\n'
                ' * block\n'
                ' * comment*/\n'
                'Code\n',
                '/* Multi-line*/\n'
                '/* block*/\n'
                '/* comment*/\n'
                'Code\n',
                'CSS')

    #  ``<div>`` testing
    def test_4(self):
        self.mt('\t// Comment\n'
                '\tCode\n'
                'Code2\n',
                '    // Comment\n'
                '    Code\n'
                'Code2\n',
                'C')

    #  ``<div>`` testing
    # No inline delimiters
    def test_4b(self):
        self.mt('\t/* Comment*/\n'
                '\tCode\n'
                'Code2\n',
                '    /* Comment*/\n'
                '    Code\n'
                'Code2\n',
                'CSS')



class TestRestToCodeFileTests(object):

    # Round trip testing in files with a given name
    def rt_given_file(self, code_file_name=None, lang='Python', lexer=None):

        # Get the extension of the given file so you can match it with the temporary files.
        file_name = code_file_name.rsplit('.')
        ext = '.' + file_name[-1]
        # Create the 'temporary files <https://docs.python.org/3/library/tempfile.html#tempfile.mkstemp>'_.
        fr, rest_file = mkstemp(suffix='.rst')
        fm1, modded_code_file1 = mkstemp(suffix=ext)
        fm2, modded_code_file2 = mkstemp(suffix=ext)
        # Close all files. This is done on an os level because the os thinks they are open.
        # The files are opened in python during the translation process so they needed to be closed first.
        os.close(fr)
        os.close(fm1)
        os.close(fm2)
        # Translate the code to rest and back again twice. This will ensure that it is round trip stable.
        code_to_rest_file(code_file_name, rest_file, alias=lexer)
        rest_to_code_file(lang, rest_file, modded_code_file1)
        code_to_rest_file(modded_code_file1, rest_file, alias=lexer)
        rest_to_code_file(lang, rest_file, modded_code_file2)
        # Open and read the two code files.
        f1 = io.FileInput(source_path=modded_code_file1)
        f2 = io.FileInput(source_path=modded_code_file2)
        code1 = f1.read()
        code2 = f2.read()
        # Remove the temporary files from the system.
        os.remove(rest_file)
        os.remove(modded_code_file1)
        os.remove(modded_code_file2)
        # Make sure the code is the same; this shows round trip stability.
        assert (code1 == code2)



    # Python file test
    def test_1(self):
        self.rt_given_file(code_file_name='CodeChat/CodeToRest.py')

    # CSS file test
    def test_2(self):
        self.rt_given_file(code_file_name='CodeChat.css', lang='CSS', lexer='css')

    # Empty file (C) test
    def test_3(self):
        fd, tmp_path = mkstemp(suffix='.c')
        os.close(fd)
        self.rt_given_file(code_file_name=tmp_path, lang='C')
        os.remove(tmp_path)

    # find_file_ext test
    def test_find_file_ext_1(self):
        ext = find_file_ext('Python')
        assert ext == '.py'

    def test_find_file_ext_2(self):
        ext = find_file_ext('Pthon')
        assert ext is None

    def test_find_file_ext_3(self):
        ext = find_file_ext('C')
        assert ext == '.c'
