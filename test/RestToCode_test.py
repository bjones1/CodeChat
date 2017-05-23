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
#
# Local application imports
# -------------------------
from CodeChat.RestToCode import rest_to_code_file
from CodeChat.CodeToRest import code_to_rest_file





class TestRestToCode_file_tests(object):

    # Testing in files
    def ft(self, code_file, rest_file, modded_code_file1, modded_code_file2, lang='Python'):

        code_to_rest_file(code_file, rest_file)
        rest_to_code_file(rest_file, modded_code_file1, lang)
        code_to_rest_file(modded_code_file1, rest_file)
        rest_to_code_file(rest_file, modded_code_file2, lang)
        f1 = io.FileInput(source_path=modded_code_file1)
        f2 = io.FileInput(source_path=modded_code_file2)
        code1 = f1.read()
        code2 = f2.read()
        assert (code1 == code2)




    def test_1(self):
        self.ft('CodeChat\\CodeToRest.py','TestFiles\\t.rst','TestFiles\\t1.py','TestFiles\\t2.py')

#TODO test 2 currently fails due to the interpreted lexer being 'CSS+Lasso'
    def test_2(self):
        self.ft('CodeChat.css','TestFiles\\t.rst','TestFiles\\t1.css','TestFiles\\t2.css','CSS')


    def test_3(self):
        self.ft('TestFiles\\Empty.c','TestFiles\\t.rst','TestFiles\\t1.c','TestFiles\\t2.c','C')