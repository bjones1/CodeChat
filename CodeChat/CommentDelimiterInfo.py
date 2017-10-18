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
# ************************************************************************
# CommentDelimiterInfo.py - Info on comment delimiters for many languages.
# ************************************************************************
# :doc:`CodeChat <__init__.py>` relies on knowledge of the comment
# delimiters for each supported language. This file consists of a large table
# which provides this information.
#
# Imports
# =======
# These are listed in the order prescribed by `PEP 8
# <http://www.python.org/dev/peps/pep-0008/#imports>`_.
#
# Third-party imports
# -------------------
from pygments.lexers import get_all_lexers
#
# Supported languages
# ===================
# Based on the unique name for each lexer, provide some additional information
# on comment delimiters that Pygments doesn't explicitly define. This data was
# mostly taken from the `Wikipedia page
# <http://en.wikipedia.org/wiki/Comparison_of_programming_languages_(syntax)#Comments>`_.
COMMENT_DELIMITER_INFO = {
  # These languages have unit tests which pass
  # ------------------------------------------
  # See :doc:`../test/CodeToRest_test.py` for the tests.
  ## Language name: inline, block opening, block closing
  'C':              ( '//',     '/*',            '*/'),
  'C++':            ( '//',     '/*',            '*/'),
  'Java':           ( '//',     '/*',            '*/'),
  'ActionScript':   ( '//',     '/*',            '*/'),
  'ActionScript 3': ( '//',     '/*',            '*/'),
  'C#':             ( '//',     '/*',            '*/'),
  # Note: also has   ``/+``  ~  ``+/`` for nested block comments.
  # (reST to code will use characters in tuple)
  'D':              ( '//',     '/*',            '*/'),
  'Go':             ( '//',     '/*',            '*/'),
  'JavaScript':     ( '//',     '/*',            '*/'),
  'Objective-C':    ( '//',     '/*',            '*/'),
  'Rust':           ( '//',     '/*',            '*/'),
  'Scala':          ( '//',     '/*',            '*/'),
  'Swift':          ( '//',     '/*',            '*/'),
  'verilog':        ( '//',     '/*',            '*/'),
  'systemverilog':  ( '//',     '/*',            '*/'),
  'Dart':           ( '//',     '/*',            '*/'),
  'Juttle':         ( '//',     '/*',            '*/'),
  'Objective-J':    ( '//',     '/*',            '*/'),
  'TypeScript':     ( '//',     '/*',            '*/'),
  'Arduino':        ( '//',     '/*',            '*/'),
  'Clay':           ( '//',     '/*',            '*/'),
  'CUDA':           ( '//',     '/*',            '*/'),
  'eC':             ( '//',     '/*',            '*/'),
  'MQL':            ( '//',     '/*',            '*/'),
  'nesC':           ( '//',     '/*',            '*/'),
  'Pike':           ( '//',     '/*',            '*/'),
  'SWIG':           ( '//',     '/*',            '*/'),
  'Vala':           ( '//',     '/*',            '*/'),
  'Zephir':         ( '//',     '/*',            '*/'),
  'Haxe':           ( '//',     '/*',            '*/'),

  # Note: PHP allows ``#`` or ``//`` as an inline comment. We only support
  # ``#``.
  'PHP':            ( '#',      '/*',            '*/'),
  # Block comments not tested.
  'NASM':           (';', '%comment\n', '%endcomment'),
  # PIC24 not tested.
  'PIC24':          (';',       '/*',            '*/'),
  # In Python, docstrings are treated as multi-line comments.
  'Python':         ( '#',      '"""',          '"""'),
  'Python 3':       ( '#',      '"""',          '"""'),
  'CSS':            (None,       '/*',           '*/'),
  # This covers csh and sh as well. Wikipedia claims that ``<#`` ~ ``#>`` are
  # block comments, but I don't see this anywhere in man bash. These aren't
  # supported.
  'Bash':           ( '#',      None,            None),
  'Tcsh':           ( '#',      None,            None),
  # The only valid comment type is ``REM``. Neither ``:`` or ``::`` are
  # classified as a comment.
  'Batchfile':      ( 'REM',    None,            None),
  'Matlab':         ( '%',      '%{',            '%}'),
  'SQL':            ( '--',     '/*',            '*/'),
  'PowerShell':     ( '#',      '<#',            '#>'),
  # ``/*`` ~ ``*/`` not supported (Pygments doesn't lex these).
  'GAS':            ( '#',      '/*',            '*/'),
  'autohotkey':     ( ';',      '/*',            '*/'),
  'Prolog':         ( '%',      '/*',            '*/'),
  'AutoIt':         ( ';',     '#cs',           '#ce'),

  # `PODs <https://docs.perl6.org/language/pod>`_ not supported. Only single line comments
  'Perl':           ( '#',      None,            None),
  # PODs not supported in Perl6, since they conflict with the new block-style
  # comments: ``#`[`` ~ ``]``, or any other pair.
  'Perl6':          ( '#',     "#'(",             ')'),

  'Ruby':           ( '#',  '=begin',          '=end'),
  'S':              ( '#',      None,            None),
  # `Bird style <https://wiki.haskell.org/Literate_programming#Bird_Style>`_
  # is not supported.
  'Haskell':        ( '--',     '{-',            '-}'),
  # ``(*`` ~ ``*)`` not supported.
  'Delphi':         ( '//',      '{',             '}'),
  'AppleScript':    ( '//',     '(*',            '*)'),
  'Common Lisp':    ( ';',      '#|',            '|#'),
  # ``--[=[`` ~ ``]=]`` not supported.
  'Lua':            ( '--',   '--[[',            ']]'),
  'Clojure':        ( ';',      None,            None),
  'Scheme':         ( ';',      None,            None),
  'HTML':           (None,    '<!--',           '-->'),
  'MXML':           (None,   '<!---',           '-->'),
  'Fortran':        ( '!',      None,            None),
  'APL':            ( '⍝',      None,            None),
  'Makefile':       ( '#',      None,            None),
  'RPMSpec':        ( '#',      None,            None),
  'Nimrod':         ( '#',      None,            None),
  ##                 ; or #
  # (reST to code will use '#')
  'NSIS':           ( '#',      None,            None),
  'TeX':            ( '%',      None,            None),
  'Erlang':         ( '%',      None,            None),
  'QBasic':         ( "'",      None,            None),
  'VB.net':         ( "'",      None,            None),
  'REBOL':          ( ';',      None,            None),
  'LLVM':           ( ';',      None,            None),
  'INI':            ( ';',      None,            None),
  'Ada':            ( '--',     None,            None),
  'Eiffel':         ( '--',     None,            None),
  'vhdl':           ( '--',     None,            None),
  # ``*>`` as an inline comment is not supported.
  # six spaces will precede '*' when converting reST to code
  ## Six ignored characters followed by * or /.
  'COBOL':          ('      *', None,            None),
  'YAML':           ( '#',      None,            None),

  # These languages have failing unit tests
  # ---------------------------------------
  # None at this time.
  }
#
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
