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
# HtmlToCode_test.py - Unit testing
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
from CodeChat.RestToCode import html_to_code_file, html_to_code_string, \
    find_file_ext
from CodeChat.CodeToRest import code_to_html_string, code_to_html_file


# TODO. See last test in RestToCode_test.py.
def xtest_1():
    html_to_code_file('Python', 'C:\\Users\\Austin\\Desktop\\Test\\RestToCode.html')
