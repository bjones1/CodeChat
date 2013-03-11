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
    # The MruFiles object should work with nothing in the MRU list.
    def test_mru_list_empty(self):
        # Removing ``app =`` produces a ``QWidget: Must construct a QApplication before a QPaintDevice`` error.
        app = QtGui.QApplication([])
        mw = CodeChatWindow()
        settings = QtCore.QSettings("MSU BJones", "CodeChat_test")
        # Remove all keys
        for key in settings.allKeys():
            settings.remove(key)
        mru_files = MruFiles(mw, settings)
        assert mru_files.get_mru_list() == []
