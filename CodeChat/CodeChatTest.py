# -*- coding: utf-8 -*-

# This test bench exercises the FindLongestMatchingString module.

import unittest
from FindLongestMatchingString import find_approx_text_in_target as f

# A diagnostic function to match then print the returned match.
def p(search_text, search_anchor, target_text):
    index = f(search_text, search_anchor, target_text)
    print(search_text[search_anchor:] + '\n' + target_text[index:])
    return index


# Find a location in a source file based on a given location in the resulting
# html.
class TestFindLongestMatchingString(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        
    # Show that we can match identical text
    def test_1(self):
        index = f(search_anchor = 2,
                  search_text = 'test',
                  target_text = 'test')
        self.assertEqual(index, 2)

    # Show that we can match with a initial Python comment
    def test_2(self):
        index = f(search_anchor = 4,
                  search_text = '# test',
                  target_text = 'test')
        self.assertEqual(index, 2)

    # Show that we can match with a initial C/C++ comment
    def test_3(self):
        index = f(search_anchor = 5,
                  search_text = '// test',
                  target_text = 'test')
        self.assertEqual(index, 2)

    # Show that we can match at the end of a line
    def test_4(self):
        index = f(search_anchor = 4,
                  search_text = 'test\ntest',
                  target_text = 'test\ntest')
        self.assertEqual(index, 4)

    # Show that we can match at the end of a line with a Python comment
    def test_5(self):
        index = f(search_anchor = 6,
                  search_text = '# test\n# test',
                  target_text = 'test\ntest')
        self.assertEqual(index, 4)

    def test_6(self):
        index = p(search_anchor = 73-34,
                  search_text = '# The :doc:`README` user manual gives a broad overview of this system. In contrast, this document discusses the implementation specifics of the CodeChat system.',
                  target_text = 'The CodeChat user manual gives a broad overview of this system. In contrast, this document discusses the implementation specifics of the CodeChat system.')
        self.assertEqual(index, 66-34)

def run_one_test(test_name):
    suite = unittest.TestSuite()
    suite.addTest(TestFindLongestMatchingString(test_name))
    unittest.TextTestRunner().run(suite)

if __name__ == '__main__':
    run_one_test('test_6')
#    unittest.main()
