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
# ************************
# |docname| - Unit testing
# ************************
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
# None.

# Third-party imports
# -------------------
# None.

# Local application imports
# -------------------------
from CodeChat.CodeToMarkdown import code_to_markdown_string, _fence, codechat_style


# Define the Markdown put at the beginning of any the outputs of ``code_to_markdown_string``.
prolog = codechat_style + "\n\n"


# Transform source code into its equivalent Markdown.
def code(code_str):
    return _fence + "\n" + code_str + _fence + "\n"


# ``_generate_rest`` inserts a ``<div>`` to format indented comments followed by
# a ``set-line`` directive to show line numbers of the comments correctly. This
# function generates the same string.
def div(
    # The size of the indent, in characters.
    size
):

    # Each space = 0.5 em, so a 3-space indent would be ``size=1.5``.
    return '\n<div class="CodeChat-indent" style="margin-left:{}em;">\n\n'.format(
        size * 0.5
    )


# The standard string which marks the end of a ``<div>``.
div_end = "\n</div>\n\n"


class TestCodeToMarkdown(object):
    # Provide a simple way to run a test.
    def run(self, code_str, expected_md_str, alias):
        md_str = code_to_markdown_string(code_str, alias=alias)
        print(md_str)
        assert prolog + expected_md_str == md_str
        return md_str

    # Test pure code.
    def test_1(self):
        self.run("x = 1", code("x = 1\n"), "Python")

    # Test only a comment.
    def test_2(self):
        self.run("# Testing", "Testing\n", "Python")

    # Test an indented comment.
    def test_3(self):
        self.run(
            "# Testing\n" "    # 1, 2, 3\n",
            "Testing\n" + div(4) + "1, 2, 3\n" + div_end,
            "Python",
        )

    # Test an indented comment with code.
    def test_4(self):
        self.run(
            "def foo(x):\n" "  # Testing\n" "  x = 1\n" "  # 1, 2, 3.\n",
            code("def foo(x):\n")
            + div(2)
            + "Testing\n"
            + div_end
            + code("  x = 1\n")
            + div(2)
            + "1, 2, 3.\n"
            + div_end,
            "Python",
        )

    # Test a syntax error in Python code.
    def test_5(self):
        self.run(
            " x = 1",
            "# Error\n"
            "SyntaxError: unexpected indent (line 1). Docstrings cannot be processed.\n"
            + "\n"
            + code(" x = 1\n"),
            "Python",
        )
