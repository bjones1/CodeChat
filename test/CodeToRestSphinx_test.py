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
# **************************************************************
# |docname| - Unit testing for `../CodeChat/CodeToRestSphinx.py`
# **************************************************************
#
# Imports
# =======
# These are listed in the order prescribed by `PEP 8
# <http://www.python.org/dev/peps/pep-0008/#imports>`_.
#
# Library imports
# ---------------
from difflib import unified_diff
from pathlib import Path
import subprocess
import sys

# Third-party imports
# -------------------
# None.

# Local application imports
# -------------------------
# None.


# Tests
# =====
def test_1():
    root_path = Path(__file__).parents[1]
    try:
        # See `../codechat_config.yaml` for an explanation of these arguments.
        cp = subprocess.run(
            ["sphinx-build", "-E", ".", "_build"],
            capture_output=True,
            encoding="utf-8",
            check=True,
            cwd=str(root_path),
        )

        # Check errors and warnings.
        assert "ERROR" not in cp.stderr
        assert "WARNING" not in cp.stderr

        # Check styling.
        diff_files(root_path, "docs/style_test.py.html", "style_test.py.html")
        # Check Markdown rendering.
        diff_files(root_path, "docs/style_guide.md.cpp.html", "style_guide.md.cpp.html")
        # Check CodeChat_lexer_for_glob rendering.
        diff_files(root_path, ".flake8.html", ".flake8.html")

    except Exception as e:
        if isinstance(e, subprocess.CalledProcessError):
            cp = e
        # Print out the Sphinx results on any test failure.
        print(cp.stdout)
        print(cp.stderr)
        raise


def diff_files(
    # Root of this repo.
    root_path,
    # The actual file produced by Sphinx, relative to the Sphinx output directory.
    actual_relpath,
    # The expected results, relative to the test directory.
    expected_relapth,
):
    root_path = Path(__file__).parents[1]

    # Compare rendering of `../docs/style_test.py` to a known good copy.
    with open(
        root_path / "_build" / actual_relpath, encoding="utf-8"
    ) as actual_file, open(
        Path(__file__).parent / expected_relapth, encoding="utf-8"
    ) as expected_file:
        actual = remove_navigation(actual_file.readlines())
        expected = remove_navigation(expected_file.readlines())
        # If the files differ, show the diff.
        if actual != expected:
            sys.stderr.writelines(
                unified_diff(
                    actual,
                    expected,
                    "Actual - {}".format(actual_relpath),
                    "Expected - {}".format(expected_relapth),
                )
            )
            assert False


def remove_navigation(lines):
    for index, line in enumerate(lines):
        if line == "<h3>Navigation</h3>\n":
            return lines[:index]

    # We didn't find the navigation heading.
    assert False
