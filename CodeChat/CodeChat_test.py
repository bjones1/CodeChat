# -*- coding: utf-8 -*-
#
# Unit testing
# ------------
# This test bench exercises the CodeChat module. It cannot be run directly from Spyder, since that produces spurious errors (``ImportError: No module named CodeChat_test``). Therefore, the auto-run code (pytest.main()) is omitted.
#
# TODO

# This must appear before importing PyQt4, since it sets SIP's api version. Otherwise, this produces the error message ``ValueError: API 'QString' has already been set to version 1``.
from CodeChat import MruFiles, form_class
from PyQt4 import QtGui, QtCore

class CodeChatWindow(QtGui.QMainWindow, form_class):
    def __init__(self):
        # Let Qt and PyQt run their init first.
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)

class TestMruFiles(object):
    def setup(self):
        # Removing ``app =`` produces a ``QWidget: Must construct a QApplication before a QPaintDevice`` error.
        app = QtGui.QApplication([])
        mw = CodeChatWindow()
        settings = QtCore.QSettings("MSU BJones", "CodeChat_test")
        # Remove all keys
        for key in settings.allKeys():
            settings.remove(key)
        self.mru_files = MruFiles(mw, settings)

    # The MruFiles object should work with nothing in the MRU list.
    def test_mru_list_empty(self):
        # The MRU list should be empty
        assert self.mru_files.get_mru_list() == []
        # There's no MRU file to open.
        assert self.mru_files.open_mru() == False

    # This helper method inserts 'a'...'j' into the MRU list.
    def insert_letters(self):
        # Create a list ['a', 'b', ... 'j'], 10 items long.
        file_list = [chr(ord('a') + i) for i in range(10)]
        # Add these as files to the MRU list.
        for file_name in file_list:
            self.mru_files.add_file(file_name)
        return file_list

    # Insert items. The most recently inserted item should be at the top, while the first insertion is at the end of the list.
    def test_mru_insert_order(self):
        file_list = self.insert_letters()
        # Check the order.
        file_list.reverse()
        assert self.mru_files.get_mru_list() == file_list

    def test_mru_double_insert(self):
        file_list = self.insert_letters()
        self.mru_files.add_file('a')
        # Check the order.
        file_list.reverse()
        file_list = file_list[0:-1]
        file_list.insert(0, 'a')
        assert self.mru_files.get_mru_list() == file_list

