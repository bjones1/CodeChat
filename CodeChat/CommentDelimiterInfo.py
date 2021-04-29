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
# *********************************************************
# |docname| - Info on comment delimiters for many languages
# *********************************************************
# `CodeChat <__init__.py>` relies on knowledge of the comment
# delimiters for each supported language. This file consists of a large table
# which provides this information.
#
# Imports
# =======
# These are listed in the order prescribed by `PEP 8
# <http://www.python.org/dev/peps/pep-0008/#imports>`_.
#
# Standard library
# ----------------
# None
#
# Third-party imports
# -------------------
from pygments.lexers import get_all_lexers

# Local application imports
# -------------------------
# None.


# Supported languages
# ===================
# Based on the unique name for each lexer, provide some additional information
# on comment delimiters that Pygments doesn't explicitly define. This data was
# mostly taken from the `Wikipedia page
# <http://en.wikipedia.org/wiki/Comparison_of_programming_languages_(syntax)#Comments>`_.
#
# `Disable Black <https://github.com/psf/black#the-black-code-style>`_ for this block.
# fmt: off
COMMENT_DELIMITER_INFO = {
#
# These languages have unit tests which pass
# ------------------------------------------
# See :doc:`../test/CodeToRest_test.py` for the tests.
    ## Language name: inline, block opening, block closing
    "C":              ( ( "//", ),     "/*",            "*/"),
    "C++":            ( ( "//", ),     "/*",            "*/"),
    "Java":           ( ( "//", ),     "/*",            "*/"),
    "ActionScript":   ( ( "//", ),     "/*",            "*/"),
    "ActionScript 3": ( ( "//", ),     "/*",            "*/"),
    "C#":             ( ( "//", ),     "/*",            "*/"),
    # Note: also has   ``/+``  ~  ``+/`` for nested block comments.
    # (reST to code will use characters in tuple)
    "D":              ( ( "//", ),     "/*",            "*/"),
    "Go":             ( ( "//", ),     "/*",            "*/"),
    "JavaScript":     ( ( "//", ),     "/*",            "*/"),
    "Objective-C":    ( ( "//", ),     "/*",            "*/"),
    "Rust":           ( ( "//", ),     "/*",            "*/"),
    "Scala":          ( ( "//", ),     "/*",            "*/"),
    "Swift":          ( ( "//", ),     "/*",            "*/"),
    "verilog":        ( ( "//", ),     "/*",            "*/"),
    "systemverilog":  ( ( "//", ),     "/*",            "*/"),
    "Dart":           ( ( "//", ),     "/*",            "*/"),
    "Juttle":         ( ( "//", ),     "/*",            "*/"),
    "Objective-J":    ( ( "//", ),     "/*",            "*/"),
    "TypeScript":     ( ( "//", ),     "/*",            "*/"),
    "Arduino":        ( ( "//", ),     "/*",            "*/"),
    "Clay":           ( ( "//", ),     "/*",            "*/"),
    "CUDA":           ( ( "//", ),     "/*",            "*/"),
    "eC":             ( ( "//", ),     "/*",            "*/"),
    "MQL":            ( ( "//", ),     "/*",            "*/"),
    "nesC":           ( ( "//", ),     "/*",            "*/"),
    "Pike":           ( ( "//", ),     "/*",            "*/"),
    "SWIG":           ( ( "//", ),     "/*",            "*/"),
    "Vala":           ( ( "//", ),     "/*",            "*/"),
    "Zephir":         ( ( "//", ),     "/*",            "*/"),
    "Haxe":           ( ( "//", ),     "/*",            "*/"),
    "Thrift":         ( ( "//", ),     "/*",            "*/"),

    "PHP":            ( ( "#", "//"),  "/*",            "*/"),
    # Block comments not tested.
    "NASM":           ( ( ";", ), "%comment\n", "%endcomment"),
    "PIC24":          ( ( ";", ),      "/*",           "*/"),
    # In Python, docstrings are treated as multi-line comments.
    "Python 2.x":     ( ( "#", ),     '"""',          '"""'),
    "Python":         ( ( "#", ),     '"""',          '"""'),
    "CSS":            ( ( "", ),       "/*",           "*/"),
    # This covers csh and sh as well. Wikipedia claims that ``<#`` ~ ``#>`` are
    # block comments, but I don"t see this anywhere in man bash. These aren't
    # supported.
    "Bash":           ( ( "#", ),        "",              ""),
    "Tcsh":           ( ( "#", ),        "",              ""),
    # The only valid comment type is ``rem``. Neither ``:`` or ``::`` are
    # classified as a comment. Not that this must be a lower-case string, since it
    # will be compared to a lowercased comment.
    "Batchfile":      ( ( "rem", ),      "",              ""),
    "Matlab":         ( ("%", "..."),  "%{",            "%}"),
    "SQL":            ( ( "--", ),     "/*",            "*/"),
    "PL/pgSQL":       ( ( "--", ),     "/*",            "*/"),
    "PowerShell":     ( ( "#", ),      "<#",            "#>"),
    # ``/*`` ~ ``*/`` not supported (Pygments doesn't lex these).
    "GAS":            ( ( "#", ),      "/*",            "*/"),
    "autohotkey":     ( ( ";", ),      "/*",            "*/"),
    "Prolog":         ( ( "%", ),      "/*",            "*/"),
    "AutoIt":         ( ( ";", ),     "#cs",           "#ce"),

    # `PODs <https://docs.perl6.org/language/pod>`_ not supported. Only single line comments
    "Perl":           ( ( "#", ),        "",              ""),
    # PODs not supported in Perl6, since they conflict with the new block-style
    # comments: ``#`[`` ~ ``]``, or any other pair.
    "Perl6":          ( ( "#", ),     "#'(",             ")"),

    "Ruby":           ( ( "#", ),  "=begin",          "=end"),
    "S":              ( ( "#", ),        "",              ""),
    # `Bird style <https://wiki.haskell.org/Literate_programming#Bird_Style>`_
    # is not supported.
    "Haskell":        ( ( "--", ),     "{-",            "-}"),
    # ``(*`` ~ ``*)`` not supported.
    "Delphi":         ( ( "//", ),      "{",             "}"),
    "AppleScript":    ( ("--", "#"),   "(*",            "*)"),
    "Common Lisp":    ( ( ";", ),      "#|",            "|#"),
    # ``--[=[`` ~ ``]=]`` not supported.
    "Lua":            ( ( "--", ),   "--[[",            "]]"),
    "Clojure":        ( ( ";", ),        "",              ""),
    "Scheme":         ( ( ";", ),        "",              ""),
    "HTML":           ( (  "", ),    "<!--",           "-->"),
    "MXML":           ( (  "", ),   "<!---",           "-->"),
    "Fortran":        ( ( "!", ),        "",              ""),
    "APL":            ( ( "⍝", ),        "",              ""),
    "Makefile":       ( ( "#", ),        "",              ""),
    "RPMSpec":        ( ( "#", ),        "",              ""),
    "Nimrod":         ( ( "#", ),        "",              ""),
    # Comments continued on the next line with a ``\`` aren't supported.
    "NSIS":           ( ("#", ";"),      "",              ""),
    "TeX":            ( ( "%", ),        "",              ""),
    "Erlang":         ( ( "%", ),        "",              ""),
    "QBasic":         ( ( "'", ),        "",              ""),
    "VB.net":         ( ( "'", ),        "",              ""),
    "REBOL":          ( ( ";", ),        "",              ""),
    "LLVM":           ( ( ";", ),        "",              ""),
    "INI":            ( ( ";", "#"),     "",              ""),
    "Ada":            ( ( "--", ),       "",              ""),
    "Eiffel":         ( ( "--", ),       "",              ""),
    "vhdl":           ( ( "--", ),       "",              ""),
    # An inline comment is six ignored characters followed by ``*`` or ``/`` -- there's a `special case <COBOL special case>` in the code to handle this. ``*>`` as an inline comment is not supported.
    "COBOL":          ( ( "      *", ),  "",              ""),
    "YAML":           ( ( "#", ),        "",              ""),
    "TOML":           ( ( "#", ),        "",              ""),

# These languages lack unit tests
# -------------------------------
    "HTML+Django/Jinja": ( ( "", ),  "<!--",           "-->"),

# These languages have failing unit tests
# ---------------------------------------
# None at this time.
}
# fmt: on

# Supported extensions
# ====================
# Compute a list of supported filename globs: supported by the lexer and
# by CodeChat (inline / block comment info in ``COMMENT_DELIMITER_INFO``).
SUPPORTED_GLOBS = set()
# Per `get_all_lexers
# <http://pygments.org/docs/api/#pygments.lexers.get_all_lexers>`_, we get a
# tuple. Pick out only the filename and examine it.
for longname, aliases, filename_patterns, mimetypes in get_all_lexers():
    # Pick only filenames we have comment info for.
    if longname in COMMENT_DELIMITER_INFO:
        SUPPORTED_GLOBS |= set(filename_patterns)
