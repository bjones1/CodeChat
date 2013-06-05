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
# *******************************************************************
# CodeChatUtils.py - Provide a set of utilities in support of the GUI
# *******************************************************************
# .. contents:: Table of Contents
#    :local:
#    :depth: 1
#
# Imports
# =======
# These are listed in the order prescribed by `PEP 8 <http://www.python.org/dev/peps/pep-0008/#imports>`_.
#
# Standard library
# ----------------
import os
import subprocess
#
# Third-party imports
# -------------------
# The excellent `PyQt4 library <http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/classes.html>`_ provides the GUI for this package.
from PyQt4 import QtGui, QtCore
#
# Local imports
# -------------
import MultiprocessingSphinx

# MRU list
# ========
# This class provides a most-recently-used (where "used" is updated when a document is opened) menu item and the functionality to load in files from the MRU list. It stores the MRU list in the registry, pushing any updates to ``self.mru_action_list``, a list of File menu QActions (see update_gui_).
#
# Data structures:
#
# #. ``self.mru_action_list = [QAction(MRU list[0]), ...]`` stores the list of File menu MRU QActions. Each action stores data the from MRU list.
# #. The MRU list (obtained from ``self.get_mru_list() == [MRU_file_0_name, ...]`` stores a list of most-recently-used file names.
class MruFiles(object):
    # Initialize the MRU list and the File menu's MRU items.
    def __init__(self,
                 # The parent CodeChatWindow; this class will modify its File menu and call its open() method.
                 parent,
                 # An instance of QSettings in which this class will store MRU information.
                 settings):
        self.mru_list_key = "MRU list"
        self.max_files = 10
        self.settings = settings
        self.parent = parent
        # Create ``self.max_files`` QActions for MRU entries and place them (hidden) in the File menu.
        self.mru_action_list = []
        for index in range(self.max_files):
            mru_item = QtGui.QAction(parent)
            mru_item.setVisible(False)
            # Assign a ctrl+number shortcut key if possible.
            if (index < 10):
                mru_item.setShortcut(QtGui.QKeySequence(u'Ctrl+' + unicode(index)))
            # Notify this class when an MRU item on the file menu is triggered.
            mru_item.triggered.connect(self.mru_triggered)
            parent.menu_File.addAction(mru_item)
            self.mru_action_list.append(mru_item)
        # Perform an initial update of the File menu items, now that they're created.
        self.update_gui()

    def open_mru(self):
        # Open the most recently used file (the file that was open when the program exited).
        mru_list = self.get_mru_list()
        if mru_list:
            file_name = mru_list[0]
            # TODO: This is the wrong approach. What if the file was deleted just after this check? Instead, open should throw an exception that this code should catch and return false with.
            if os.path.exists(file_name):
                self.parent.open(file_name)
                return True
        return False

    # Called when an MRU file is triggered.
    @QtCore.pyqtSlot()
    def mru_triggered(self):
        # Determine which action sent this signal
        mru_action = self.parent.sender()
        if mru_action:
            # Get the file name stored within that action
            file_name = mru_action.data()
            # TODO: Catch any exceptions thrown by this open.
            self.parent.open(file_name)

    # Returns the registry's MRU list as a Python list.
    def get_mru_list(self):
        return list(self.settings.value(self.mru_list_key, []))

    # Adds a file to the MRU list.
    def add_file(self, file_name):
        # Add file_name to the MRU list, moving it to the top if it's already in the list.
        mru_list = self.get_mru_list()
        if file_name in mru_list:
            mru_list.remove(file_name)
        mru_list.insert(0, file_name)
        # Trim the list if it is too long.
        if len(mru_list) > self.max_files:
            mru_list.pop()
        # Update the stored MRU list.
        self.settings.setValue(self.mru_list_key, mru_list)
        # Update the GUI.
        self.update_gui()

    # .. _update_gui:
    #
    # Take the MRU list stored in the registry and update the File menu to reflect these registry contents.
    def update_gui(self):
        # For each elemnt in the MRU list, update the menu item.
        mru_list = self.get_mru_list()
        for index in range(len(mru_list)):
            mru_action = self.mru_action_list[index]
            mru_action.setText('&%d %s' % (index, mru_list[index]))
            mru_action.setData(mru_list[index])
            mru_action.setVisible(True)
        # Hide the rest of the actions.
        for index in range(len(mru_list), self.max_files):
            self.mru_action_list[index].setVisible(False)
#
# .. _Background-Sphinx-execution:
#
# Background Sphinx execution
# ===========================
# This class is run in a separate thread to perform a Sphinx build in another process. It captures stdout and stderr from Sphinx, passing them back to the GUI for display. To begin, this program establishes a set of signal/slot connections in the constructor below between the CodeChat object (running in the main thread) and the BackgroundSphinx object (which runs in a separate worker thread), illustrated in the diagram below. Boxes represent objects, which ellipses represent methods of that object. Numbers indicate the sequence of events, which is further explained below.
#
# The process begins at (1a), when :ref:`CodeChatWindow.save_then_update_html <CodeChatWindow-save_then_update_html>` emits :ref:`signal_Sphinx_start <CodeChatWindow-signal_Sphinx_start>`, which Qt then places in the BackgroundSphinx message queue. When BackgroundSphinx is idle, this message then invokes :ref:`run_Sphinx() <BackgroundSphinx-run_Sphinx>`, which starts Sphinx execution in a separate process via an IPC pipe write in (1b). As Sphinx runs, the worker thread waits for any status messages produced by the IPC pipe in (2a), which cause :ref:`run_Sphinx() <BackgroundSphinx-run_Sphinx>` to emit :ref:`signal_Sphinx_results <BackgroundSphinx-signal_Sphinx_results>` in step (2b), in order to deliver these status messages to the GUI queue; when the GUI is idle, these messages then invoke :ref:`Sphinx_results <CodeChatWindow-Sphinx_results>`, which displays them in the bottom pane of the GUI. When Sphinx finishes, step (3) shows that :ref:`run_Sphinx() <BackgroundSphinx-run_Sphinx>` emits :ref:`signal_Sphinx_done <BackgroundSphinx-signal_Sphinx_done>` to :ref:`after_Sphinx <CodeChatWindow-after_Sphinx>` with any error messages produced during the build.
#
# This message-passing approach to concurrency helps avoid many of the common errors found in multi-threaded programming. In particular, BackgroundSphinx and CodeChat have no shared state to protect; all shared information is instead passed in messages. Therefore, there is no mutex/semaphore usage, and no consequent livelock / deadlock errors.
#
# .. _BackgroundSphinx diagram:
#
# .. digraph:: GUI_and_BackgroundSphinx_synchronization
#
#    subgraph cluster_CodeChat {
#      label = "CodeChatWindow";
#      "save_then_update_html";
#      "Sphinx_results";
#      "after_Sphinx";
#    }
#    subgraph cluster_BackgroundSphinx {
#      label = "BackgroundSphinx";
#      "run_Sphinx"
#    }
#    subgraph cluster_MultiprocessingSphinx {
#      label = "MultiprocessingSphinx";
#      "run_Sphinx_process"
#    }
#    "save_then_update_html" -> "run_Sphinx" [label = "signal_Sphinx_start", taillabel = "(1a)"];
#    "run_Sphinx" -> "run_Sphinx_process" [taillabel = "(1a)"];
#    "run_Sphinx_process" -> "run_Sphinx" [taillabel = "(2a)"];
#    "run_Sphinx" -> "Sphinx_results" [label = "signal_Sphinx_results", taillabel = "(2b)"];
#    "run_Sphinx" -> "after_Sphinx" [label = "signal_Sphinx_done", taillabel = "(3)"];
#
# This class must inherit from a QObject in order to support the signal/slot mechanism.
class BackgroundSphinx(QtCore.QObject):
# Construction
# ------------
# This section of the object builds the graph shown above, initializing this object then running it run in a newly-created background thread. **Note: this code runs in the GUI thread.** Everything else in this object runs in the background thread.
#
    # .. _BackgroundSphinx-signal_Sphinx_results:
    #
    # run_Sphinx emits this as Sphinx produces results from the build.
    signal_Sphinx_results = QtCore.pyqtSignal(unicode)

    # .. _BackgroundSphinx-signal_Sphinx_done:
    #
    # run_Sphinx emits this when the Sphinx build finishes with the results from stderr.
    signal_Sphinx_done = QtCore.pyqtSignal(unicode)

    def __init__(self, parent):
        QtCore.QObject.__init__(self)

        # Obtain a reference to the multiprocessing Sphinx connection object from the parent.
        self.parent_conn = parent.multiprocessing_Sphinx_manager.parent_conn

        # Start a thread for backgroun Sphinx operation, which waits for signals to arrive from the parent to begin processing. Doing this right isn't obvious; the best reference and short example code is given in the `QThread docs <http://qt-project.org/doc/qt-4.8/qthread.html#details>`_.
        self.thread = QtCore.QThread()
        self.moveToThread(self.thread)
        self.thread.start()

        # Create a series of signal/slot connections per the :ref:`diagram <BackgroundSphinx diagram>`. These connections must be established **after** the call to moveToThread, so that they're be delivered asynchronoushly. Otherwise, the background Sphinx thread will cause the GUI thread to block until it completes.
        self.signal_Sphinx_results.connect(parent.Sphinx_results)
        self.signal_Sphinx_done.connect(parent.after_Sphinx)
        parent.signal_Sphinx_start.connect(self.run_Sphinx)

# Worker routine
# --------------
    # This routine is (indirectly) invoked by :ref:`CodeChatWindow.save_then_update_html <CodeChatWindow-save_then_update_html>`. It returns nothing, instead emitting signals when output is ready, as explained above. run_Sphinx assumes that all Sphinx input files have been saved to the disk in the current directory tree.
    #
    # The actual work is done in a separate process, to overcome GIL-enforced single-tasking. The approach:
    #
    # #. Start up Sphinx in a separate process, giving it a pipe end. Done by the :ref:`MultiprocessingSphinxManager constructor <MultiprocessingSphinxManager-__init-__>`.
    # #. Sphinx blocks on a pipe read, which gives it (current dir, html_dir)
    # #. Sphinx begins processing; this worker thread blocks on a pipe read of (is_message_from_stderr, message_text). It emits signals for both, ending when it gets a stderr message and going to the previous step to wait for another Sphinx run.
    #
    # .. _BackgroundSphinx-run_Sphinx:
    #
    def run_Sphinx(self, html_dir, build_tool):
                         # Directory in which Sphinx should place the HTML output from the build.

        if build_tool == BUILD_TOOL_DOXYGEN:
            # A better way to get real-time output: http://stackoverflow.com/questions/1388753/how-to-get-output-from-subprocess-popen/1388807#1388807
            try:
                output = subprocess.check_output('doxygen', stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                output = e.output

            self.signal_Sphinx_done.emit(output)

        elif build_tool == BUILD_TOOL_SPHINX:
            # Start the build by sending params.
            self.parent_conn.send([os.getcwd(), html_dir])
            # Send any stdout as a signal
            is_stderr = False
            while not is_stderr:
                is_stderr, txt = self.parent_conn.recv()
                if not is_stderr:
                    # Send any stdout text along
                    self.signal_Sphinx_results.emit(txt)
            # Send a signal with the stderr string now that Sphinx is finished.
            self.signal_Sphinx_done.emit(txt)
        else:
            assert False
#
# Resettable timer
# ================
# A convenience class to add a restart() method to a QTimer.
class QRestartableTimer(QtCore.QTimer):
    def restart(self):
        self.stop()
        self.start()
#
# Build tools enum
# ================
BUILD_TOOL_SPHINX, BUILD_TOOL_DOXYGEN = range(2)
