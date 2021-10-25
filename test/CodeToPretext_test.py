# .. Copyright (C) 2012-2020 Bryan A. Jones.
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
# **********************************
# |docname| - Unit tests for PreTeXt
# **********************************
# This test bench exercises the CodeToPretext module. First, set up for
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
from textwrap import dedent

# Third-party imports
# -------------------
# None.
#
# Local application imports
# -------------------------
from CodeChat.CodeToPretext import code_to_pretext_string


# Globals
# =======
# Define the PreTeXt put at the beginning of the output of ``code_to_pretext_string``.
prolog = "<program><input>"

# Define the PreTeXt put at the end.
epilog = "</input></program>"


# Tests
# =====
class TestCodeToPretext(object):
    # Provide a simple way to run a test.
    def run(self, code_str, expected_md_str, alias, parse_error=None):
        ptx_str = code_to_pretext_string(code_str, alias=alias)
        print(ptx_str)
        assert (
            f"<warning>{parse_error}</warning>" if parse_error else ""
        ) + prolog + expected_md_str + epilog == ptx_str
        return ptx_str

    # Test pure code, ensuring that entities are translated.
    def test_1(self):
        self.run(
            "y = '&' if x < 1 else ''", "y = '&amp;' if x &lt; 1 else ''\n", "Python"
        )

    # Test only a comment with no XML included.
    def test_2(self):
        self.run("# Testing", "<p>Testing</p>\n", "Python")

    # Test a comment with XML ``<p>`` tags included.
    def test_3(self):
        self.run("#  <p  >Testing></p >  ", " <p  >Testing></p >  \n", "Python")

    # Test an indented comment.
    def test_4(self):
        self.run(
            "  # 1, 2, 3\n",
            "  <p>1, 2, 3</p>\n",
            "Python",
        )

    # Test an indented comment with code.
    def test_5(self):
        self.run(
            dedent(
                """\
                def foo(x):
                    # Testing
                    x = 1
                    # 1, 2, 3."""
            ),
            dedent(
                """\
                def foo(x):
                    <p>Testing</p>
                    x = 1
                    <p>1, 2, 3.</p>
                """
            ),
            "Python",
        )

    # Test a syntax error in Python code.
    def test_6(self):
        self.run(
            " x = 1",
            " x = 1\n",
            "Python",
            parse_error="CodeChat parse error: SyntaxError: unexpected indent (line 1). Docstrings cannot be processed.",
        )
