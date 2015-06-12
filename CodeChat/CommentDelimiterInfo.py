# .. -*- coding: utf-8 -*-
#
#    Copyright (C) 2012-2015 Bryan A. Jones.
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
# Based on the unique name for each lexer, provide some additional information
# on comment delimiters that Pygments doesn't explicitly define. This data was
# mostly taken from the `Wikipedia page
# <http://en.wikipedia.org/wiki/Comparison_of_programming_languages_(syntax)#Comments>`_.
COMMENT_DELIMITER_INFO = {
  ## Language name: inline, block opening, block closing
  ##                 //,     /*,            */
  # Note: the following langauges have unit tests to verify that they work.
  'C':              ( 2,      2,            2),
  'C++':            ( 2,      2,            2),
  'Java':           ( 2,      2,            2),
  'ActionScript':   ( 2,      2,            2),
  'ActionScript 3': ( 2,      2,            2),
  'C#':             ( 2,      2,            2),
  'D':              ( 2,      2,            2), #  Note: also has /+ ~ +/ for
                                                ## nested block comments.
  'Go':             ( 2,      2,            2),
  'JavaScript':     ( 2,      2,            2),
  'Objective-C':    ( 2,      2,            2),
  'Rust':           ( 2,      2,            2),
  'Scala':          ( 2,      2,            2),
  'Sass':           ( 2,      2,            2), # ??? Doesn't work in tests
  'Swift':          ( 2,      2,            2),
  'verilog':        ( 2,      2,            2),
  'systemverilog':  ( 2,      2,            2),
  ##                  #,    N/A,          N/A
  'Python':         ( 1,   None,         None),
  'Python 3':       ( 1,   None,         None),
  ##                         /*,            */
  'CSS':            (None,    2,            2),
  ##                  ;, %comment\n, %endcomment  -- block comments not tested.
  'NASM':           ( 1,      9,           11),

  # These langauges have **NOT** been tested.
  ##                  #      /*             */
  'GAS':            ( 1,      2,            2),
  ##                  ;      /*,            */
  'autohotkey':     ( 1,      2,            2),
  ##                 --      /*,            */
  'SQL':            ( 2,      2,            2),
  ##                  #      /*,            */
  'PHP':            ( 1,      2,            2),
  # Note: PHP allows # or // as an inline comment. We only support #.

  ##                       <!--,           -->
  'HTML':           (None,    4,            3),
  ##                  %      /*,            */
  'Prolog':         ( 1,      2,            2),
  ##                  ;,    #cs,           #ce
  'AutoIt':         ( 1,      3,            3),
  ##                  #,     <#,            #>
  'PowerShell':     ( 1,      2,            2),
  ##                  #, =begin,          =cut
  'Perl':           ( 1,      6,            4),
  ##                  #,    #'(,             )  # Or #`[ ~ ], or any other pairs.
  'Perl6':          ( 1,      3,             1),
  ##                  #, =begin,          =end
  'Ruby':           ( 1,      6,            4),
  ##                  #, #iffalse,      #endif
  'S':              ( 1,      8,            6),
  ##                 --,     {-,            -}
  'Haskell':        ( 2,      2,            2), # Bird style not supported. See
                     # https://wiki.haskell.org/Literate_programming#Bird_Style.
  ##                 //,      {,             }
  'Delphi':         ( 2,      1,            1),  # (* ~ *) not supported.
  ##                 //,     (*,            *)
  'AppleScript':    ( 2,      2,            2),
  ##                  %      %{,            %}
  'Matlab':         ( 1,      2,            2),
  ##                  ;,     #|,            |#
  'Common Lisp':    ( 1,      2,            2),
  'Scheme':         ( 1,   None,         None),
  ##                 --,   --[[,            ]]
  'Lua':            ( 2,      4,            2),  # --[=[ ~ ]=] not supported.
  ##                  ;, (comment,           )
  'Clojure':        ( 1,      8,            1),
  ##                  #,     <#,            #>
  # This covers csh and sh as well.
  'Bash':           ( 1,      2,            2),
  'Tcsh':           ( 1,      2,            2),

  ## Languages with no block comments.

  ##                  C or !
  'Fortran':        ( 1,   None,         None),
  ##                  :
  # Note: for simplicity, I don't support :: or REM as a valid comment type.
  # Something for future work.
  'Batchfile':      ( 1,   None,         None),
  ##                  ⍝
  'APL':            ( 1,   None,         None),
  ##                  #
  'Makefile':       ( 1,   None,         None),
  'Nimrod':         ( 1,   None,         None),
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
  'Vhdl':           ( 2,   None,         None),
  ##                  * or /
  'COBOL':          ( 1,   None,         None),  #  *> as inline comment not
                                                 ## supported.
  }


