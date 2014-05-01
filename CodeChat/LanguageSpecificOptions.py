# .. -*- coding: utf-8 -*-
#
#    Copyright (C) 2012-2013 Bryan A. Jones.
#
#    This file is part of CodeChat.
#
#    CodeChat is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#    CodeChat is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along with CodeChat.  If not, see <http://www.gnu.org/licenses/>.

# | Fix: Sphinx reports the error:
# |  ``Extension error:``
# |  ``Could not import extension CodeChat.CodeToRest (exception: No module named Qsci)``
# | on the import below. ??? We only need this import for the CodeChat app, so work around it for now.
try:
    from PyQt4.Qsci import QsciLexerCPP, QsciLexerPython
except ImportError as e:
    QsciLexerCPP, QsciLexerPython = (None, None)

# ****************************************************************************************
# LanguageSpecificOptions.py - assist in providing language-specific settings for CodeChat
# ****************************************************************************************
#
# LanguageSpecificOptions
# =======================
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
    unique_remove_str = u'wokifvzohtdlm'

    # .. attribute:: language_specific_options
    #
    #    A dict of language-specific options.
    extension_to_options = {
    ##  Pygments  lexer
    ##  Extension  Comment string, QScintilla lexer
      u'.c'      : (u'//',           QsciLexerCPP),
      u'.cc'     : (u'//',           QsciLexerCPP),
      u'.cpp'    : (u'//',           QsciLexerCPP),
      u'.h'      : (u'//',           QsciLexerCPP),
      u'.hh'     : (u'//',           QsciLexerCPP),
      u'.hpp'    : (u'//',           QsciLexerCPP),
      u'.py'     : (u'#',            QsciLexerPython),
      u'.s'      : (u';',            None),
      u'.php'    : (u'#',            None),
      u'.m'      : (u'%',            None),
      u'.bat'    : (u':',            None),
      u'.ini'    : (u';',            None),
      u'.iss'    : (u';',            None),
    }

    # .. method:: set_language(extension)
    #
    #    Sets the :class:`LanguageSpecificOptions` offered, where *extension* gives the extension for the desired language.
    def set_language(self, extension):
        # If the extension is unknown, then assign the comment string and lexer as None.
        (self.comment_string, self.lexer) = self.extension_to_options.get(extension, (None, None))
