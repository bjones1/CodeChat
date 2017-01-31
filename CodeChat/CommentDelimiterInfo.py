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
  ##                   //,     /*,            */
  'C':              ( '//',   '/*',          '/*'),
  'C++':            ( '//',   '/*',          '/*'),
  'Java':           ( '//',   '/*',          '/*'),
  'ActionScript':   ( '//',   '/*',          '/*'),
  'ActionScript 3': ( '//',   '/*',          '/*'),
  'C#':             ( '//',   '/*',          '/*'),
  # Note: also has   ``/+`` ~ ``+/`` for nested block comments.
  'D':              ( '//',   '/*',          '/*'),
  'Go':             ( '//',   '/*',          '/*'),
  'JavaScript':     ( '//',   '/*',          '/*'),
  'Objective-C':    ( '//',   '/*',          '/*'),
  'Rust':           ( '//',   '/*',          '/*'),
  'Scala':          ( '//',   '/*',          '/*'),
  'Swift':          ( '//',   '/*',          '/*'),
  'verilog':        ( '//',   '/*',          '/*'),
  'systemverilog':  ( '//',   '/*',          '/*'),
  'Dart':           ( '//',   '/*',          '/*'),
  'Juttle':         ( '//',   '/*',          '/*'),
  'Objective-J':    ( '//',   '/*',          '/*'),
  'TypeScript':     ( '//',   '/*',          '/*'),
  'Arduino':        ( '//',   '/*',          '/*'),
  'Clay':           ( '//',   '/*',          '/*'),
  'CUDA':           ( '//',   '/*',          '/*'),
  'eC':             ( '//',   '/*',          '/*'),
  'MQL':            ( '//',   '/*',          '/*'),
  'nesC':           ( '//',   '/*',          '/*'),
  'Pike':           ( '//',   '/*',          '/*'),
  'SWIG':           ( '//',   '/*',          '/*'),
  'Vala':           ( '//',   '/*',          '/*'),
  'Zephir':         ( '//',   '/*',          '/*'),
  'Haxe':           ( '//',   '/*',          '/*'),

  # Note: PHP allows ``#`` or ``//`` as an inline comment. We only support
  # ``#``.
  ##                  #,     /*,            */
  'PHP':            ( '#',      '/*',            '/*'),
  ##                  ;, %comment\n, %endcomment  -- block comments not tested.
  'NASM':           ( 1,      9,           11),
  # In Python, docstrings are treated as multi-line comments.
  ##                  #,    """,          """
  'Python':         ( 1,      3,            3),
  'Python 3':       ( 1,      3,            3),
  ##                         /*,            */
  'CSS':            (None,    2,            2),
  # This covers csh and sh as well. Wikipedia claims that ``<#`` ~ ``#>`` are
  # block comments, but I don't see this anywhere in man bash. These aren't
  # supported.
  ##                  #
  'Bash':           ( 1,   None,         None),
  'Tcsh':           ( 1,   None,         None),
  # The only valid comment type is ``REM``. Neither ``:`` or ``::`` are
  # classified as a comment.
  ##                REM
  'Batchfile':      ( 3,   None,         None),
  ##                  %,     %{,            %}
  'Matlab':         ( 1,      2,            2),
  ##                 --,     /*,            */
  'SQL':            ( 2,      2,            2),
  ##                  #,     <#,            #>
  'PowerShell':     ( 1,      2,            2),
  # ``/*`` ~ ``*/`` not supported (Pygments doesn't lex these).
  ##                  #,     /*,            */
  'GAS':            ( 1,      2,            2),
  ##                  ;,     /*,            */
  'autohotkey':     ( 1,      2,            2),
  ##                  %,     /*,            */
  'Prolog':         ( 1,      2,            2),
  ##                  ;,    #cs,           #ce
  'AutoIt':         ( 1,      3,            3),
  # PODs begin and end on a line starting with =string. Toss the entire line by
  # making the delimiter length large. This allows it to work with ``=head1``,
  # ``=begin``, ``=begin comment``, and a host of others.
  ##                  #, =a string, =another string
  'Perl':           ( 1,   1000,         1000),
  # PODs not supported in Perl6, since they conflict with the new block-style
  # comments: ``#`[`` ~ ``]``, or any other pair.
  ##                  #,    #'(,             )
  'Perl6':          ( 1,      3,            1),
  ##                  #, =begin,          =end
  'Ruby':           ( 1,      6,            4),
  ##                  #
  'S':              ( 1,   None,         None),
  # `Bird style <https://wiki.haskell.org/Literate_programming#Bird_Style>`_
  # is not supported.
  ##                 --,     {-,            -}
  'Haskell':        ( 2,      2,            2),
  # ``(*`` ~ ``*)`` not supported.
  ##                 //,      {,             }
  'Delphi':         ( 2,      1,            1),
  ##                 //,     (*,            *)
  'AppleScript':    ( 2,      2,            2),
  ##                  ;,     #|,            |#
  'Common Lisp':    ( 1,      2,            2),
  # ``--[=[`` ~ ``]=]`` not supported.
  ##                 --,   --[[,            ]]
  'Lua':            ( 2,      4,            2),
  ##                  ;
  'Clojure':        ( 1,   None,         None),
  ##                  ;,
  'Scheme':         ( 1,   None,         None),
  ##                       <!--,           -->
  'HTML':           (None,    4,            3),
  ##                      <!---,           -->
  'MXML':           (None,    5,            3),
  ##                  !
  'Fortran':        ( 1,   None,         None),
  ##                  ⍝
  'APL':            ( 1,   None,         None),
  ##                  #
  'Makefile':       ( 1,   None,         None),
  'RPMSpec':        ( 1,   None,         None),
  'Nimrod':         ( 1,   None,         None),
  ##                  ; or #
  'NSIS':           ( 1,   None,         None),
  ##                  %
  'TeX':            ( 1,   None,         None),
  ##                  %
  'Erlang':         ( 1,   None,         None),
  ##                  '
  'QBasic':         ( 1,   None,         None),
  'VB.net':         ( 1,   None,         None),
  ##                  ;
  'REBOL':          ( 1,   None,         None),
  'LLVM':           ( 1,   None,         None),
  ##                 --
  'Ada':            ( 2,   None,         None),
  'Eiffel':         ( 2,   None,         None),
  'vhdl':           ( 2,   None,         None),
  # ``*>`` as an inline comment is not supported.
  ##                  Six ignored characters followed by * or /.
  'COBOL':          ( 7,   None,         None),
  ##                  ;
  'INI':            ( 1,   None,         None),
  ##                  #
  'YAML':           ( 1,   None,         None),

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
