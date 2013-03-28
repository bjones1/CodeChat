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
#
# CodeToRest_test.py - Unit testing
# ---------------------------------
# This test bench exercises the CodeToRest module.

# Test the fixup code which removes junk lines used only to produce a desired indent.
from CodeToRest import sphinx_html_page_context
class TestSphinxHtmlPageContext(object):
    # Given a string, return it after sphinx_html_page_context processes it.
    def s(self, string):
        context = {'body' : string}
        sphinx_html_page_context(None, None, None, context, None)
        return context['body']

    # Show that normal text isn't changed
    def test_1(self):
        string = 'testing'
        ret = self.s(string)
        assert ret == string

from cStringIO import StringIO
from CodeToRest import code_to_rest
from LanguageSpecificOptions import LanguageSpecificOptions
from pygments.lexers.compiled import CLexer, CppLexer
from pygments.lexers.agile import PythonLexer
class TestCodeToRest(object):
    # Given a string and a language, run it through code_to_rest and return the resulting string.
    def t(self, in_string, language = CLexer()):
        # Use a StringIO object to act like file IO which code_to_rest expects.
        lso = LanguageSpecificOptions()
        lso.set_language(language)
        in_stringIO = StringIO(in_string)
        out_stringIO = StringIO()
        code_to_rest(lso, in_stringIO, out_stringIO)
        # For convenience, create the removal string for the chosen language
        unique_remove_comment = lso.comment_string + ' ' + lso.unique_remove_str + '\n'
        return out_stringIO.getvalue(), unique_remove_comment

    # A single line of code, without an ending \n
    def test_1(self):
        ret, comment = self.t('testing')
        assert ret ==  '\n\n::\n\n ' + comment + ' testing\n'

    # A single line of code, with an ending \n.
    def test_2(self):
        ret, comment = self.t('testing\n')
        assert ret == '\n\n::\n\n ' + comment + ' testing\n'

    # Several lines of code, with arbitrary indents
    def test_3(self):
        ret, comment = self.t('testing\n  test 1\n test 2\n   test 3')
        assert ret == '\n\n::\n\n ' + comment + ' testing\n   test 1\n  test 2\n    test 3\n'

    # A single line comment, no trailing \n
    def test_4(self):
        ret, comment = self.t('// testing')
        assert ret == '\ntesting\n'

    # A single line comment, trailing \n
    def test_5(self):
        ret, comment = self.t('// testing\n')
        assert ret == '\ntesting\n'

    # A multi line comment
    def test_5a(self):
        ret, comment = self.t('// testing\n// more testing')
        assert ret == '\ntesting\nmore testing\n'

    # A single line comment with no space after the comment should be treated like code
    def test_6(self):
        ret, comment = self.t('//testing')
        assert ret == '\n\n::\n\n ' + comment + ' //testing\n'

    # A singly indented single-line comment
    def test_7(self):
        ret, comment = self.t(' // testing')
        assert ret == '\n\n' + comment + '\n testing\n'

    # A doubly indented single-line comment
    def test_8(self):
        ret, comment = self.t('  // testing')
        assert ret == '\n\n' + comment + '\n ' + comment + '\n  testing\n'

    # A doubly indented multi-line comment
    def test_9(self):
        ret, comment = self.t('  // testing\n  // more testing')
        assert ret == '\n\n' + comment + '\n ' + comment + '\n  testing\n  more testing\n'

    # Code to comment transition
    def test_9a(self):
        ret, comment = self.t('testing\n// test')
        assert ret == '\n\n::\n\n ' + comment + ' testing\n ' + comment + '\ntest\n'

    # A line with just the comment char, but no trailing space.
    def test_10(self):
        ret, comment = self.t('//')
        # Two newlines: one gets added since code_to_rest prepends a \n, assuming a previous line existed; the second comes from the end of code_to_test, where a final \n is appended to make sure the file ends with a newlines.
        assert ret == '\n\n'

    # A line with just the comment char, with a Microsoft-style line end
    def test_11(self):
        ret, comment = self.t('//\r\n')
        # Two newlines: one gets added since code_to_rest prepends a \n, assuming a previous line existed; the second comes from the end of code_to_test, where a final \n is appended to make sure the file ends with a newlines.
        assert ret == '\n\n'

import pytest
def main():
    # Run all tests -- see http://pytest.org/latest/usage.html#calling-pytest-from-python-code.
    pytest.main()
    # Run a specifically-named test -- see above link plus http://pytest.org/latest/usage.html#specifying-tests-selecting-tests.
    #pytest.main('-k test_11')

if __name__ == '__main__':
    main()
