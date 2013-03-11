# -*- coding: utf-8 -*-
#
# Unit testing
# ------------
# This test bench exercises the CodeChat module. TODO!

import sys
from PyQt4 import QtGui, QtCore
from CodeChat import MruFiles, form_class

class CodeChatWindow(QtGui.QMainWindow, form_class):
    def __init__(self):
        # Let Qt and PyQt run their init first.
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)

class TestMruFiles(object):
    # The MruFiles object should work with nothing in the MRU list.
    def test_mru_list_empty(self):
        # Removing ``app =`` produces a ``QWidget: Must construct a QApplication before a QPaintDevice`` error.
        app = QtGui.QApplication(sys.argv)
        mw = CodeChatWindow()
        settings = QtCore.QSettings("MSU BJones", "CodeChat_test")
        # Remove all keys
        for key in settings.allKeys():
            settings.remove(key)
        mru_files = MruFiles(mw, settings)
        assert mru_files.get_mru_list() == []

import pytest
def main():
    # Run all tests -- see http://pytest.org/latest/usage.html#calling-pytest-from-python-code.
    pytest.main()
    # Run a specifically-named test -- see above link plus http://pytest.org/latest/usage.html#specifying-tests-selecting-tests.
    #pytest.main('-k test_11')

if __name__ == '__main__':
#    main()
    a = TestMruFiles()
    a.test_mru_list_empty()