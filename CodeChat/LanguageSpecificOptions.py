# .. -*- coding: utf-8 -*-
#
# .. Copyright (C) 2012-2013 Bryan A. Jones.
#
# .. This file is part of CodeChat.
#
# .. CodeChat is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# .. CodeChat is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# .. You should have received a copy of the GNU General Public License along with CodeChat.  If not, see <http://www.gnu.org/licenses/>.

from PyQt4.Qsci import QsciLexerCPP, QsciLexerPython, QsciLexerBash
from pygments.lexers.compiled import CLexer, CppLexer
from pygments.lexers.agile import PythonLexer
from pygments.lexers.text import RstLexer
from pygments.lexers.math import SLexer
from pygments.lexers.shell import BashLexer
from pygments.lexers.web import PhpLexer
from pygments.lexers.math import MatlabLexer


# Language Specific Options
# ==============================================================================
# For each programming language supported, :meth:`set_language` specifies:
#
# .. attribute:: comment_string
#
#    The string indicating the beginning of a comment in the chosen programming language, or None if the CodeToRest process isn't supported. This must end in a space for the regular expression in format to work. The space also makes the output a bit prettier.
#
# .. attribute:: lexer
#
#    The QScintilla lexer to use, or None to disable syntax highlighting in the text pane
#
# .. class:: LanguageSpecificOptions()
class LanguageSpecificOptions(object):
    # .. attribute:: unique_remove_str
    #
    #    A unique string to mark lines for removal in HTML.
    unique_remove_str = 'wokifvzohtdlm'

    # .. attribute:: language_specific_options
    #
    #    A tuple of language-specific options, indexed by the class of the parser which Pygments selects.
    language_specific_options = {
    ##  Pygments  lexer
    ##  |                        Comment string, QScintilla lexer, extension list
      CLexer().__class__      : ('//',          QsciLexerCPP,     ('.c', '.h')),
      CppLexer().__class__    : ('//',          QsciLexerCPP,     ('.cpp',)),
      PythonLexer().__class__ : ('#',           QsciLexerPython,  ('.py',)),
      RstLexer().__class__    : (None,          None,             ()),
      SLexer().__class__      : (';',           None,             ('.s',)),
      BashLexer().__class__   : ('#',           QsciLexerBash,    ('.bash',)),
      PhpLexer().__class__    : ('#',           None,             ('.php', )),
      MatlabLexer().__class__ : ('%',           None,             ('.m', )),
    }

    # .. method:: set_language(language_)
    #
    #    Sets the :class:`LanguageSpecificOptions` offered, where *language_* gives the Pygments lexer for the desired language.
    def set_language(self, language_):
        language = language_.__class__
        (self.comment_string, self.lexer, self.extensions) = \
          self.language_specific_options[language]
