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
# *********************************************************
# RestToCode.py - a module to translate reST to source code
# *********************************************************
#
#
# .. contents::
#
# Imports
# =======
# These are listed in the order prescribed by `PEP 8
# <http://www.python.org/dev/peps/pep-0008/#imports>`_.
#
# Standard library
# ----------------
# For stderr.
import sys
# For calling code_to_rest with a string. While using cStringIO would be
# great, it doesn't support Unicode, so we can't.
from io import StringIO
# To find a file's extension and locate data files.
import os.path
# For enumerations.
from enum import Enum
# To clean up docstrings.
import inspect
#
# Third-party imports
# -------------------
# For the docutils default stylesheet and template
from pygments.lexers import get_all_lexers

#
# Local application imports
# -------------------------
from CommentDelimiterInfo import COMMENT_DELIMITER_INFO
#


# Functions
# =========
# Converting the reST file into whatever language code you would like
#

# Find the file extension needed, given the language name
def find_file_ext(new_file_language):
    found = 0
    for longname, aliases, filename_patterns, mimetypes in get_all_lexers():
        # Pick only filenames we have comment info for.
        if longname in COMMENT_DELIMITER_INFO:
            if longname == new_file_language:
                file_ext_raw = filename_patterns[0]
                found = 1
    # If we support the language, return the file extension.
    # Else, return None
    if found == 1:
        # Use only the '.py' part of '*.py' and similar.
        file_ext_list = file_ext_raw.split('*', 1)
        file_ext = file_ext_list[-1]
        return file_ext
    else:
        return None
#
# Gather the location of the file to be translated and the name of the language
# that the file will be translated into.
def file_info():
    file_name_raw = str(input('What is the name of the file to be translated? '))
    # This takes just the file location and name (it removes the extension)
    file_name_list = file_name_raw.rsplit('.', 1)
    file_name = file_name_list[0]

    new_file_language = str(input('What is the language you would like? '))
    file_ext = None
    while file_ext is None:
        file_ext = find_file_ext(new_file_language)
        if file_ext is not None:
            break
        new_file_language = str(input('We could not find that one. Please try again: '))

    return [file_name, new_file_language, file_ext]
#

# Get the tuple of delimiters from our dictionary.
def restore_comments(language):
    return COMMENT_DELIMITER_INFO[language]
#

# Allows the use of languages that have only inline comments or only block comments
# Checks to make sure the comment type is available and returns that information
def language_comment_type(comment_delimiters):
    inline = False
    block = False
    if comment_delimiters[0] is not None:
        inline = True
    if comment_delimiters[1] is not None:
        block = True
    return [inline, block]
#

# Tells the program whether to make a block comment or an inline comment.
# Number of lines required for the block comment to activate is currently 10,000 consecutive comments.
# Block comments also activate if the language has no inline comments.
# Inline comments also activate if the language has no block comments.
def formulate_comment(list, new_file_language, is_block_comment, position, line_counter):
    comment_delimiters = restore_comments(new_file_language)
    comment_type = language_comment_type(comment_delimiters)
    if is_block_comment is False and comment_type[0] is True:
        return formulate_inline_comment(list, comment_delimiters)
    elif is_block_comment is True and comment_type[1] is False:
        return formulate_inline_comment(list, comment_delimiters)
    else:
        if is_block_comment is False:
            line_counter = None
        return formulate_block_comment(list, comment_delimiters, position, line_counter)
#

#
def formulate_inline_comment(list, comment_delimiters):

    f = '{} '.format(comment_delimiters[0]) + list + '\n'
    return f


def formulate_block_comment(list, comment_delimiters, position, line_counter):

    if line_counter is None:
        f = '{} '.format(comment_delimiters[1]) + list + ' {}'.format(comment_delimiters[2]) + '\n'

    else:
        if position == line_counter:
            f = '{} '.format(comment_delimiters[1]) + list + '\n'
        elif position > 0:
            f = ' * ' + list + '\n'
        else:
            f = ' * ' + list + ' {}'.format(comment_delimiters[2]) + '\n'

    return f


def file_interpreter():

    file_name, new_file_language, file_ext = file_info()


    file = open('{}.rst'.format(file_name))
    string = file.read()
    file.close()

    file_out = open('{}{}'.format(file_name, file_ext), 'w')
    f = rest_to_code(string, new_file_language)
    file_out.write(f)
    file_out.close()


# core function: take string as input, returns a string
# TODO write tests also junk input and empty file, a bunch of different languages
# TODO comments
def rest_to_code(string, new_language):
    i = 0
    string = string.replace('\t', '    ')
    list = string.split('\n')
    string_out = ""
    while i < len(list):
        try:
            list[i+1]
            if list[i+1] == '.. fenced-code::':
                i += 4
                while list[i] != ' Ending fence':
                    s = list[i].split(' ', 1)
                    f = s[1] + '\n'
                    string_out += f
                    # file_out.write(f)
                    i += 1
                try:
                    # skips over the  added code including the setline part of the code.
                    i += 9 # TODO assert the code between here to make sure it is what we think it should be
                # this exception catches the case that the file ends with code rather than a comment
                except:
                    i += 8

            # This is to find the <div> comments and turn them into comments.
            elif list[i+1] == '.. raw:: html':
                # used to control the line number of the document
                i += 3
                # splits the line into ' <div style="margin-left' and '{size}em;">'
                s = list[i].split(':', 1)
                # splits '{size}em;">' into '{size}' and 'm;">'
                s2 = s[1].split('e', 1)
                # turns '{size}' into a number of divs ex. 1.0 or 3.5
                size = float(s2[0])
                # gets the number of spaces needed to put the comment(s) back where it was
                # also, needs to be int() in order to work in the for loop. size starts out as a float.
                size = int(size*2)

                # skips over the  added code including the setline part of the code.
                i += 7

                while list[i+1] != '.. raw:: html':
                    spaces = ''
                    for index in range(size):
                        spaces += ' '

                    s = formulate_comment(list[i], new_language, False, 0, None)
                    f = spaces + s
                    string_out += f
                    # file_out.write(f)
                    i += 1

                # skips over the  added code including the setline part of the code.
                i += 7


            else:

                i += 0

                temp_i = i
                line_counter = 0

                while list[temp_i+1] != '.. fenced-code::':
                    line_counter += 1
                    temp_i += 1
                    try:
                        list[temp_i+1]
                        stuff = 0
                    except:
                        temp_i += 1
                        break
                # This line sets the limit for consecutive comments turning into block comments
                if line_counter < 10000:
                    is_block_comment = False
                    position = 0
                else:
                    is_block_comment = True
                    position = line_counter


                while list[i+1] != '.. fenced-code::':
                    f = formulate_comment(list[i], new_language, is_block_comment, position, line_counter)
                    string_out += f
                    # file_out.write(f)
                    position -= 1
                    i += 1
                    try:
                        list[i+1]
                        stuff = 0
                    except:
                        f = formulate_comment(list[i], new_language, is_block_comment, position, line_counter)
                        string_out += f
                        # file_out.write(f)
                        i += 1
                        break
        except:
            i += 1
            break


    return string_out
    # file_out.close()




file_interpreter()