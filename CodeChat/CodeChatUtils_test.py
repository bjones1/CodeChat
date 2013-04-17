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
# *******************************
# CodeChat_test.py - Unit testing
# *******************************
# This test bench exercises the CodeChat module. It cannot be run directly from Spyder, since that produces spurious errors (``ImportError: No module named CodeChat_test``). Therefore, the auto-run code (``pytest.main()``) is omitted.
#
# Imports
# =======
# Local application imports
# -------------------------
# This import must appear before importing PyQt4, since it sets SIP's API version. Otherwise, this produces the error message ``ValueError: API 'QString' has already been set to version 1``.
from CodeChat import form_class
from CodeChatUtils import MruFiles, BackgroundSphinx

# Standard library
# ----------------
import os
import sys
import time

# Third-party imports
# -------------------
from PyQt4 import QtGui, QtCore
from PyQt4.QtTest import QTest
import sphinx

# MruFiles
# ========
# The following class providees a mock for CodeChatWindow for use with MruFiles testing. It provides an open() methods which simply records the passed file name, and also performs necessary GUI setup in __init__ so that testing of the Qt portions of the class will work.
class CodeChatWindowForMruFilesMock(QtGui.QMainWindow, form_class):
    def __init__(self):
        # Let Qt and PyQt run their init first.
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)
        self.open_list = []

    def open(self, file_name):
        self.open_list.append(file_name)

class TestMruFiles(object):
    # .. _setup:
    def setup(self):
        # Removing ``self.app =`` produces a ``QWidget: Must construct a QApplication before a QPaintDevice`` error. Storing this as ``app = ...`` allows app to be destructed when ``setup()`` exits, producing a string of ``QAction: Initialize QApplication before calling 'setVisible'`` warnings.
        self.app = QtGui.QApplication([])
        self.mw = CodeChatWindowForMruFilesMock()
        settings = QtCore.QSettings("MSU BJones", "CodeChat_test")
        # Remove all keys
        for key in settings.allKeys():
            settings.remove(key)
        self.mru_files = MruFiles(self.mw, settings)
        # Per the `QTest docs <http://qt-project.org/doc/qt-4.8/qtestlib-tutorial3.html>`_: "The widget must also be shown in order to correctly test keyboard shortcuts."
        self.mw.show()

    # The MruFiles object should work with nothing in the MRU list.
    def test_mru_list_empty(self):
        # The MRU list should be empty
        assert self.mru_files.get_mru_list() == []
        # There's no MRU file to open.
        assert self.mru_files.open_mru() == False

    # This helper method inserts a list of strings (fake files) into the MRU list.
    def insert_letters(self,
                       # Perform ``inserts_factor`` * (capacity of MRU list) inserts.
                       inserts_factor = 1):
        num_inserts = inserts_factor*self.mru_files.max_files
        # Create a list ['А', 'Б', ...] (of captial Cyrillic letters), which contains ``num_inserts`` elements.
        file_list = [unichr(ord(u'\u0410') + i) for i in range(num_inserts)]
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
        # Create a list of 'a', 'j', 'i', ... 'b', the correct order. (But 'j', 'i', 'b' are really their Cyrillic equivalents).
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

    # Open a non-ASCII test file to test Unicode support.
    def test_open_mru(self):
        unicode_file_name = u'\u0411.txt'
        # Create an empty test file with a Cyrillic name.
        with open(unicode_file_name, 'w'):
            pass
        self.mru_files.add_file(unicode_file_name)
        assert self.mru_files.open_mru()
        os.remove(unicode_file_name)
        # The open() function should have been called once, with the name of the test file.
        assert self.mw.open_list == [unicode_file_name]

    # Open a file that doesn't exist.
    def test_open_mru_nonexistant(self):
        self.mru_files.add_file('i do not exist.txt')
        assert self.mru_files.open_mru() == False

    # Execute an MRU open from the file menu.
    def test_file_menu_mru(self):
        unicode_file_name = u'test.txt'
        # Create an empty test file.
        with open(unicode_file_name, 'w'):
            pass
        self.mru_files.add_file(unicode_file_name)
        # Press Ctrl+0 to open the first element of the MRU list.
        QTest.keyClick(self.mw, '0', QtCore.Qt.ControlModifier)
        # Now press Alt+F, 0. The 0 keypress must go directly to the File menu object; sending it to the main window has no effect.
        QTest.keyClick(self.mw, 'f', QtCore.Qt.AltModifier)
        QTest.keyClick(self.mw.menu_File, '0')

        os.remove(unicode_file_name)
        # The open() function should have been called twice, with the name of the test file.
        assert self.mw.open_list == [unicode_file_name, unicode_file_name]

# BackgroundSphinx
# ================
# To test this, we must provide a mock Sphinx, a mock CodeChat, connect signals then call run_Sphinx directly (for single-threaded tests) or indirectly (for background thread tests).
#
# Sphinx mock
# -----------
# This mock Sphinx function writes a string to stdout, then one to stderr, then another to stdout to make sure the two stdout strings are not confused with stderr results.
def sphinx_cmdline_main_mock(cmdline_args):
    # The final argument to Sphinx must be the HTML output directory.
    assert cmdline_args[-1] == 'test_dir'
    # Perform I/O that should be logged per the explanation above.
    sys.stdout.write('Running Sphinx')
    sys.stderr.write('Error')
    sys.stdout.write('\nSphinx done.')

# Install our mock object in place of the real Sphinx.
sphinx.cmdline.main = sphinx_cmdline_main_mock

# CodeChat mock
# -------------
# This mock CodeChat class simply provides a way to receive emitted signals from run_Sphinx and log them.
class CodeChatWindowForBackgroundSphinxMock(QtGui.QMainWindow):
    signal_Sphinx_start = QtCore.pyqtSignal(unicode)

    def __init__(self):
        # Let Qt run its init first.
        QtGui.QMainWindow.__init__(self)
        # Start with empty results and done logs.
        self.results = []
        self.done = []

    # Log any calls to this in self.results.
    def Sphinx_results(self, s):
        self.results.append(s)

    # Log all calls to this in self.done.
    def after_Sphinx(self, s):
        self.done.append(s)

# Unit tests
# ----------
# With the mocks above in place, create a Qt app and connect the appropriate signals, then test.
class TestBackgroundSphinx(object):

    def setup(self):
        # See setup_ for details on this syntax.
        self.app = QtGui.QApplication([])
        self.mw = CodeChatWindowForBackgroundSphinxMock()
        self.mw.show()

    def test_run_Sphinx_background(self):
        # Create a thread to run BackgroundSphinx in and start it.
        bs = BackgroundSphinx(self.mw)

        # Emit a a signal to start a Sphinx run.
        self.mw.signal_Sphinx_start.emit('test_dir')

        # Wait for background thread to run (kludge). Calling processEvents is critical; otherwise, BackgroundSphinx signals won't be delivered yet.
        time.sleep(0.1)
        self.app.processEvents()

        # End Sphinx thread
        bs.thread.quit()
        bs.thread.wait()

        assert self.mw.results == ['Running Sphinx', '\nSphinx done.']
        assert self.mw.done == ['Error']
