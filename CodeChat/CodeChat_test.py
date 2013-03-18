# -*- coding: utf-8 -*-
#
# Unit testing
# ------------
# This test bench exercises the CodeChat module. It cannot be run directly from Spyder, since that produces spurious errors (``ImportError: No module named CodeChat_test``). Therefore, the auto-run code (``pytest.main()``) is omitted.
#
# TODO
#
# This must appear before importing PyQt4, since it sets SIP's API version. Otherwise, this produces the error message ``ValueError: API 'QString' has already been set to version 1``.
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
        # TODO: I get lots of ``QAction: Initialize QApplication before calling 'setVisible'`` errors when a test fails. I'm not sure how to fix this.

    # The MruFiles object should work with nothing in the MRU list.
    def test_mru_list_empty(self):
        # The MRU list should be empty
        assert self.mru_files.get_mru_list() == []
        # There's no MRU file to open.
        assert self.mru_files.open_mru() == False

    # This helper method inserts 'a'...'j' into the MRU list.
    def insert_letters(self,
                       # Perform ``inserts_factor`` * (capacity of MRU list) inserts.
                       inserts_factor = 1):
        num_inserts = inserts_factor*self.mru_files.max_files
        # Create a list ['a', 'b', ...], which contains num_inserts elements.
        file_list = [chr(ord('a') + i) for i in range(num_inserts)]
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

    # Insering an item twice causes it to rise to the top of the MRU list.
    def test_mru_double_insert(self):
        file_list = self.insert_letters()
        self.mru_files.add_file('a')
        # Create a list of 'a', 'j', 'i', ... 'b', the correct order.
        file_list.reverse()
        file_list = file_list[0:-1]
        file_list.insert(0, 'a')
        # Check the order -- did 'a' rise to the top?
        assert self.mru_files.get_mru_list() == file_list

    def test_insert_past_capacity(self):
        file_list = self.insert_letters(2)
        file_list.reverse()
        ml = self.mru_files.get_mru_list()
        assert ml == file_list[0:len(ml)]
