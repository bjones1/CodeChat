# .. -*- coding: utf-8 -*-
#
#    Copyright (C) 2012-2013 Bryan A. Jones.
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
# ****************************************************************************************
# LanguageSpecificOptions.py - assist in providing language-specific settings for CodeChat
# ****************************************************************************************
#
# LanguageSpecificOptions
# =======================
# For each programming language supported, ``set_language`` specifies:
#
# comment_string:
#    The string indicating the beginning of a comment in the chosen programming
#    language, or None if the CodeToRest process isn't supported. This must end
#    in a space for the regular expression in format to work. The space also
#    makes the output a bit prettier.
class LanguageSpecificOptions(object):
    # A unique string to mark lines for removal in HTML.
    unique_remove_str = u'wokifvzohtdlm'

    #  A dict of language-specific options.
    extension_to_options = {
    ##  Extension  Comment string
        u'.c'      : u'//',
        u'.cc'     : u'//',
        u'.cpp'    : u'//',
        u'.h'      : u'//',
        u'.hh'     : u'//',
        u'.hpp'    : u'//',
        u'.py'     : u'#',
        u'.s'      : u';',
        u'.php'    : u'#',
        u'.m'      : u'%',
        u'.bat'    : u':',
        u'.ini'    : u';',
        u'.iss'    : u';',
        u'.java'   : u'//',
    }

    def __init__(self):
        # Start with an unspecified comment_string.
        self.comment_string = None

    # Sets the ``LanguageSpecificOptions`` offered.
    def set_language(self,
      # The file extension selecting the desired language.
      extension):
        # If the extension is unknown, then assign the comment string = None.
        self.comment_string = self.extension_to_options.get(extension)
