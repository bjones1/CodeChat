# -*- coding: utf-8 -*-
#
# Unit testing
# ------------
# This test bench exercises the FindLongestMatchingString module.

from FindLongestMatchingString import find_approx_text_in_target as f

# Find a location in a source file based on a given location in the resulting
# html.
class TestFindLongestMatchingString(object):
    # Show that we can match identical text
    def test_1(self):
        index = f(search_anchor = 2,
                  search_text = 'test',
                  target_text = 'test')
        assert index == 2

    # Show that we can match with a initial Python comment
    def test_2(self):
        index = f(search_anchor = 4,
                  search_text = '# test',
                  target_text = 'test')
        assert index == 2

    # Show that we can match with a initial C/C++ comment
    def test_3(self):
        index = f(search_anchor = 5,
                  search_text = '// test',
                  target_text = 'test')
        assert index == 2

    # Show that we can match at the end of a line
    def test_4(self):
        index = f(search_anchor = 4,
                  search_text = 'test\ntest',
                  target_text = 'test\ntest')
        assert index == 4

    # Show that we can match at the end of a line with a Python comment
    def test_5(self):
        index = f(search_anchor = 6,
                  search_text = '# test\n# test',
                  target_text = 'test\ntest')
        assert index == 4

    def test_6(self):
        index = f(search_anchor = 73-34,
                  search_text = '# The :doc:`README` user manual gives a broad overview of this system. In contrast, this document discusses the implementation specifics of the CodeChat system.',
                  target_text = 'The CodeChat user manual gives a broad overview of this system. In contrast, this document discusses the implementation specifics of the CodeChat system.')
        assert index == 66-34
import pytest
def main():
    # Run all tests -- see http://pytest.org/latest/usage.html#calling-pytest-from-python-code.
    pytest.main()
    # Run a specifically-named test -- see above link plus http://pytest.org/latest/usage.html#specifying-tests-selecting-tests.
    #pytest.main('-k test_11')

if __name__ == '__main__':
    main()
