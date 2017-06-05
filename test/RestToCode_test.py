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
from CodeChat.RestToCode import rest_to_code_file
from CodeChat.CodeToRest import code_to_rest_file





class TestRestToCode_file_tests(object):

    # Testing in files
    def ft(self, code_file_name=None, lang='Python', lexer=None):

        file_name = code_file_name.rsplit('.')
        ext = '.' + file_name[-1]
        fr, rest_file = mkstemp(suffix='.rst')
        fm1, modded_code_file1 = mkstemp(suffix=ext)
        fm2, modded_code_file2 = mkstemp(suffix=ext)
        os.close(fr)
        os.close(fm1)
        os.close(fm2)
        code_to_rest_file(code_file_name, rest_file, alias=lexer)
        rest_to_code_file(rest_file, modded_code_file1, lang)
        code_to_rest_file(modded_code_file1, rest_file, alias=lexer)
        rest_to_code_file(rest_file, modded_code_file2, lang)
        f1 = io.FileInput(source_path=modded_code_file1)
        f2 = io.FileInput(source_path=modded_code_file2)
        code1 = f1.read()
        code2 = f2.read()
        os.remove(rest_file)
        os.remove(modded_code_file1)
        os.remove(modded_code_file2)
        assert (code1 == code2)




    def test_1(self):
        self.ft(code_file_name='CodeChat\\CodeToRest.py')


    def test_2(self):
        self.ft(code_file_name='CodeChat.css',lang='CSS',lexer='css')


    def test_3(self):
        fd, tmp_path = mkstemp(suffix='.c')
        os.close(fd)
        self.ft(code_file_name=tmp_path,lang='C')
        os.remove(tmp_path)