# -*- coding: utf-8 -*-
"""
Created on Thu Nov 17 13:18:41 2011

@author: bjones
"""

import unittest
import html_edit
import sys
from PyQt4 import QtGui

# Find a location in a source file based on a given location in the resulting
# html.
class Test_find_code_from_html(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        app = QtGui.QApplication(sys.argv)
        form = html_edit.MyWidget(None)
        self.html_text = unicode(form.textEdit.toPlainText())
        self.source_text = html_edit.rest_text
        
    def test_1(self):
        loc = (155, 148, 166)
        pos = html_edit.highlight_plain_text(self.html_text, loc, 
                                             self.source_text)
        self.assertEqual(pos, 618)

if __name__ == '__main__':
    unittest.main()

