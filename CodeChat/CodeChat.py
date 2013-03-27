# .. -*- coding: utf-8 -*-
#
# .. Copyright (C) 2012-2013 Bryan A. Jones.
#
# .. This file is part of CodeChat.
#
# .. CodeChat is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# .. CodeChat is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# .. You should have received a copy of the GNU General Public License along with CodeChat.  If not, see <http://www.gnu.org/licenses/>.
#
# CodeChat
# ========
# .. module:: CodeChat
#
# Author: Bryan A. Jones <bjones AT ece DOT msstate DOT edu>
#
# The :doc:`user manual <../README>` gives a broad overview of this system. In contrast, this document discusses the implementation specifics of the CodeChat system. The table below shows the overall structure of this package; the to do list reflects changes needed to make this happen.
#
# ==============================    ===================
# Functionality                     Module
# ==============================    ===================
# GUI                               :doc:`CodeChat.py`
# Source code to reST               :doc:`CodeToRest.py`
# Matching between text and HTML    :doc:`FindLongestMatchingString.py`
# ==============================    ===================
#
# .. contents::
#
# To do
# -----
# - Pre-process search text to convert images to alt text in web_to_code_sync:
#
#   - Create a list of (index, inserted alt text string length) to convert an index from the QTextEdit to an index in this text-only, images-replaced-as-alt-text version of the document.
# - Provide a styled preview: instead of styling only code, copy formatting from HTML version to plain text version using Scintilla's `styling <http://www.scintilla.org/ScintillaDoc.html#Styling>`_ feature. Basically, the code in the left view would have different font/size/color attributes, but be verbatim text. Any paragraph-level formatting (lists, indents, etc.) would be eventually handled by auto-word-wrap which makes the code look indented, etc, but not rely on any actual word-processor like formatting: the idea is to keep the code the same, just make it prettier. Perhaps have a toggle?
#
#   - One option is to throw away Scintilla's lexer for sytax coloring in favor of results copied from Pygments. This would be more consistent.
#   - One obvious problem: how to style text (comment characters, etc.) that doesn't appear in the HTML version?
#   - Use proportional text or not? Proportional provides a better preview, but makes some areas (getting title underline correct lengths) hard and others (working with tables) frustrating and nearly impossible.
#   - Implementation sketch: QTextEdit.document() gives a QTextDocument(). QTextDocument.begin() on this yields a QTextBlock; iterate using QTextBlock.next(). In each block, check QTextBlock.isValid(), then look at each QTextFragment in the block (QTextBlock.begin(); iterator.atEnd(), iterator.fragment().charFormat() use QTextBlock.text(), QTextBlock.charFormat().font() to get info.
#   - Other ideas:
#
#     - Extend Sphinx' HTML formatter to output everything (all whitespace, backticks, etc.). This would probably be hard, since HTML also eats whitespace by default, enforces paragraph spacing, etc.
#     - Extend CodeToRest to wrap all reST syntax so that it appears verbatim in the output. This would probably be hard.
# - Rewrite documentation in this program
# - Refactor to enable more unit testing
# - Preserve last cursor position in MRU list
# - Fix broken regexps for comments (#foo doesn't work)
# - Fix extensions in LanguageSpecificOptions
# - Create a short how-to video
# - Some way to display Sphinx errors then find the offending source line
# - Fix editor to render better HTML (long term -- probably QWebKit)
# - Port to Unix, Mac using CMake / CPack
# - Toolbars to insert common expressions (hyperlink, footnote, etc)
# - Optimization: have Sphinx read in doctrees, then stay in a reprocess loop, only writing results on close.
# - Provide a MRU list for projects. Have a unique file MRU list for each project.
#
# Imports
# -------
# These are listed in the order prescribed by `PEP 8 <http://www.python.org/dev/peps/pep-0008/#imports>`_.
#
# Standard library
# ^^^^^^^^^^^^^^^^
# We need this to open and save text files in Unicode.
import codecs
# Used to capture Sphinx's stderr output for display in the GUI.
from cStringIO import StringIO
import sys
# Use to copy a new project file.
import shutil
# Used to search for alt text in generated HTML.
import re
import os
#
# Third-party imports
# ^^^^^^^^^^^^^^^^^^^
# The default Python 3 PyQt interface provides automatic conversion between several basic Qt data types and their Puthon equivalent. For Python 2, to preserve compatibility with older apps, manual conversion is required. These lines select the Python 3 approach and must be executed before any PyQt imports. See http://pyqt.sourceforge.net/Docs/PyQt4/incompatible_apis.html for more information.
import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
# Not sure what this does -- I still have to use QtCore.QUrl to build urls. ??? It also makes the Spyder debugger mad, so omit for now.
## sip.setapi('QUrl', 2)

# The excellent `PyQt4 library <http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/classes.html>`_ provides the GUI for this package.
from PyQt4 import QtGui, QtCore, uic

# `Scintilla <http://www.scintilla.org/ScintillaDoc.html>`_ (wrapped in Python) provides the text editor. However, the `Python documentation <http://www.riverbankcomputing.co.uk/static/Docs/QScintilla2/annotated.html>`_ for it was poor at best. Here's a `quick tutorial <http://eli.thegreenplace.net/2011/04/01/sample-using-qscintilla-with-pyqt/>`_ I found helpful.
from PyQt4.Qsci import QsciScintilla, QsciLexerCPP

# `Sphinx <http://sphinx.pocoo.org>`_ transforms `reST <http://docutils.sourceforge.net/docs/index.html>`_ to HTML, a core element of this tool.
import sphinx.cmdline

# `Pygments <http://pygments.org/>`_ is used to match an extension (such as .cc or .cpp) to a file type (C++ source code).
from pygments.lexers import get_lexer_for_filename
#
# Local application imports
# ^^^^^^^^^^^^^^^^^^^^^^^^^
# The GUI's layout is defined in the .ui file, which the following code loads. The .ui file could be in the current directory, if this module is executed directly; otherwise, it's in the directory which this module lives in, if imported the usual way.
try:
    module_path = os.path.dirname(__file__)
except NameError:
    module_path = ''

# When frozen, I get a "ImportError: No module named Qsci". However, it does work correctly if I just convert the .ui to a .py module. Oh, well.
try:
    form_class, base_class = uic.loadUiType(os.path.join(module_path, "CodeChat.ui"))
except (ImportError, IOError):
    from CodeChat_ui import Ui_MainWindow as form_class

from LanguageSpecificOptions import LanguageSpecificOptions

# The ability to match text in source code with text in HTML forms one of the core strengths of this module. See :doc:`FindLongestMatchingString.py` for details.
from FindLongestMatchingString import find_approx_text_in_target

# Display the version of this program in Help | About
import version

# MRU list
# --------
# This class provides a most-recently-used (where "used" is updated when a document is opened) menu item and the functionality to load in files from the MRU list. It stores the MRU list in the registry, pushing any updates to ``self.mru_action_list``, a list of File menu QActions (see update_gui_).
#
# Data structures:
#
# #. ``self.mru_action_list = [QAction(MRU list[0]), ...]`` stores the list of File menu MRU QActions. Each action stores data the from MRU list.
# #. The MRU list (obtained from ``self.get_mru_list() == [MRU_file_0_name, ...]`` stores a list of file names of MRU files.
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
        # Add file_name to the mru list, moving it to the top if it's already in the list.
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

# Background Sphinx execution
# ---------------------------
# This class is run in a separate thread to perform a Sphinx build in the background. It captures stdout and stderr from Sphinx, passing them back to the GUI for display. To begin, this program establishes a set of signal/slot connections in the :ref:`CodeChat constructor <BackgroundSphinx init>` between the CodeChat object (running in the main thread) and the BackgroundSphinx object (which runs in a separate worker thread), illustrated in the diagram below. Boxes represent objects, which ellipses represent methods of that object. Numbers indicate the sequence of events, which is further explained below.
#
# The process begins at (1), when CodeChat.save_then_update_html emits signal_Sphinx_start, which Qt then places in the BackgroundSphinx message queue. When BackgroundSphinx is idle, this message then invokes run_Sphinx(), which executes Sphinx in the worker thread. As Sphinx runs, any status messages produced cause run_sphinx() to emit signal_Sphinx_results in step (2), which delivers these status messages to the GUI queue; when the GUI is idle, these messages then invoke Sphinx_results, which displays them in the bottom pane of the GUI. When Sphinx finishes, step (3) shows that run_Sphinx() emits signal_Sphinx_done with any error messages produced during the build.
#
# This message-passing approach to concurrency helps avoid many of the common errors found in multi-threaded programming. In particular, BackgroundSphinx and CodeChat have no shared state to protect; all shared information is instead passed in messages. Therefore, there is no mutex/semaphore usage, and no consequent livelock / deadlock errors.
#
# .. _BackgroundSphinx diagram:
#
# .. digraph:: GUI_and_BackgroundSphinx_synchronization
#
#    subgraph cluster_CodeChat {
#      label = "CodeChat";
#      "save_then_update_html";
#      "Sphinx_results";
#      "after_Sphinx";
#    }
#    subgraph cluster_BackgroundSphinx {
#      label = "BackgroundSphinx";
#      "run_Sphinx"
#    }
#    "run_Sphinx" -> "Sphinx_results" [label = "signal_Sphinx_results(unicode str)", taillabel="(2)"];
#    "run_Sphinx" -> "after_Sphinx" [label = "signal_Sphinx_done(unicode str)", taillabel="(3)"];
#    "save_then_update_html" -> "run_Sphinx" [label = "signal_Sphinx_start()", taillabel="(1)"];
class BackgroundSphinx(QtCore.QObject):
    # run_Sphinx emits this as Sphinx produces results from the build.
    signal_Sphinx_results = QtCore.pyqtSignal(unicode)

    # run_Sphinx emits this when the Sphinx build finishes with the results from stderr.
    signal_Sphinx_done = QtCore.pyqtSignal(unicode)

    def run_Sphinx(self, html_dir):
        # Redirect Sphinx output to the results window. Save stderr results until the build is finished; display progress from the build by emitting signal_Sphinx_results during the build.
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = self  # This object's write() and flush() methods act like stdout.
        sys.stderr = my_stderr = StringIO()

        # Run Sphinx. The `command-line options <http://sphinx-doc.org/invocation.html>`_ are:
        sphinx.cmdline.main( ('',
                              # Name of the Sphinx executable. Not needed here.
                              '-b', 'html',
                              # Select the HTML builder.
                              '.',
                              # Source directory: the current directory.
                              html_dir) )
                              # Build directory: place the resulting HTML files in html_dir.

        # Restore stdout and stderr.
        sys.stdout = old_stdout
        sys.stderr = old_stderr

        # Send a signal with the stderr string now that Sphinx is finished.
        self.signal_Sphinx_done.emit(my_stderr.getvalue())

    # This object emit()s all stdout writes to the GUI thread for immediate display.
    def write(self, s):
        self.signal_Sphinx_results.emit(s)

    # Sphinx calls flush(), so we need a dummy implementation.
    def flush(self):
        pass

# Resettable timer
# ----------------
# A convenience class to add a restart() method to a QTimer.
class QRestartableTimer(QtCore.QTimer):
    def restart(self):
        self.stop()
        self.start()

# CodeChatWindow
# --------------
# This class provides the bulk of the functionality. Almost evrything is GUI logic; the text to HTML matching ability is imported.
#
class CodeChatWindow(QtGui.QMainWindow, form_class):
    # This signal starts a Sphinx background run; the parameter is the HTML directory to use.
    signal_Sphinx_start = QtCore.pyqtSignal(str)

    def __init__(self, app):
        # Let Qt and PyQt run their init first.
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)

        # Store a reference to this window's containing application.
        self.app = app

        self.project_dir_key = 'project directory'
        # A path to the generated HTML files, relative to the project directory
        self.html_dir = '_build/html'
        self.settings = QtCore.QSettings("MSU BJones", "CodeChat")

        # Open the last project directory of we can; otherwise, us the current directory.
        self.project_dir = self.settings.value(self.project_dir_key, os.getcwd())
        try:
            os.chdir(self.project_dir)
        except OSError:
            pass
        self.project_dir = os.getcwd()

        # Restore state from last run, if it exists and is valid.
        self.restoreGeometry(bytearray(self.settings.value('geometry', [])))
        self.restoreState(bytearray(self.settings.value('windowState', [])))
        self.splitter.restoreState(bytearray(self.settings.value('splitterSizes', [])))
        self.splitter_2.restoreState(bytearray(self.settings.value('splitter_2Sizes', [])))

        # Select a larger font for the HTML editor
        self.textBrowser.zoomIn(3)
        # Clicking on an external link produces a blank screen. I'm not sure why; perhaps Qt expects me to do this in my own code on anchorClicked signals. For simplicity, just use an external browswer.
        self.textBrowser.setOpenExternalLinks(True)
        # Switch views on a double-click
        self.textBrowser.mouseDoubleClickEvent = lambda e: self.web_to_code_sync()

        # | --Configure QScintilla--
        # | Set the default font
        self.font = QtGui.QFont()
        self.font.setFamily('Courier New')
        self.font.setFixedPitch(True)
        self.font.setPointSize(10)
        self.plainTextEdit.setFont(self.font)
        self.plainTextEdit.setMarginsFont(self.font)
        # Margin 0 is used for line numbers. Configure it.
        fontmetrics = QtGui.QFontMetrics(self.font)
        self.plainTextEdit.setMarginWidth(0, fontmetrics.width("00000") + 6)
        self.plainTextEdit.setMarginLineNumbers(0, True)
        self.plainTextEdit.setMarginsBackgroundColor(QtGui.QColor("#cccccc"))
        # Brace matching: enable for a brace immediately before or after
        # the current position
        self.plainTextEdit.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        # Enable word wrap
        self.plainTextEdit.setWrapMode(QsciScintilla.WrapWord)
        # Make home go to the beginning of the line, then to the first non-blank character in the paragraph, then to the beginning of the paragraph. Have end go to the end of the line, then to the end of the paragraph. Default behavior is to always go to the beginning/end of the paragraph.
        self.plainTextEdit.SendScintilla(QsciScintilla.SCI_ASSIGNCMDKEY, QsciScintilla.SCK_HOME, QsciScintilla.SCI_VCHOMEWRAP)
        self.plainTextEdit.SendScintilla(QsciScintilla.SCI_ASSIGNCMDKEY, QsciScintilla.SCK_END, QsciScintilla.SCI_LINEENDWRAP)
        # Use this for shift+home/end as well.
        self.plainTextEdit.SendScintilla(QsciScintilla.SCI_ASSIGNCMDKEY, QsciScintilla.SCK_HOME + (QsciScintilla.SCMOD_SHIFT << 16), QsciScintilla.SCI_VCHOMEWRAPEXTEND)
        self.plainTextEdit.SendScintilla(QsciScintilla.SCI_ASSIGNCMDKEY, QsciScintilla.SCK_END + (QsciScintilla.SCMOD_SHIFT << 16), QsciScintilla.SCI_LINEENDWRAPEXTEND)
        # Try at removing ctrl-T key binding (use as toggle views instead). Fails -- just using SCI_CLEARCMDKEY produces no action (i.e. keystroke isn't acted on by Scintilla, but isn't passed to QT either)
        ## self.plainTextEdit.SendScintilla(QsciScintilla.SCI_ASSIGNCMDKEY, ord('T') + (QsciScintilla.SCMOD_CTRL << 16), 0)
        # Show a difference background for the line the cursor is in
        self.plainTextEdit.SendScintilla(QsciScintilla.SCI_SETCARETLINEBACK, 0x99FFFF)
        self.plainTextEdit.SendScintilla(QsciScintilla.SCI_SETCARETLINEVISIBLE, True)
        # Auto-save and build whenever edits are made.
        self.plainTextEdit.modificationChanged.connect(self.on_code_changed)
        # Update web hilight whenever code cursor moves and the app is idle.
        self.timer_sync_code_to_web = QRestartableTimer()
        self.timer_sync_code_to_web.setSingleShot(True)
        self.timer_sync_code_to_web.setInterval(250)
        self.timer_sync_code_to_web.timeout.connect(self.code_to_web_sync)
        self.plainTextEdit.cursorPositionChanged.connect(lambda line, pos: self.timer_sync_code_to_web.restart())

        # Prepare for running Sphinx in the background. Getting this right was very difficult for me. My best references: I stole the code from http://stackoverflow.com/questions/6783194/background-thread-with-qthread-in-pyqt and tried to understand the explanation at http://qt-project.org/wiki/ThreadsEventsQObjects#913fb94dd61f1a62fc809f8d842c3afa.
        #
        # First, set up state variables used to do this.
        self.is_building = False
        self.need_to_build = True
        self.ignore_code_modified = False
        # .. _BackgroundSphinx init:
        #
        # Next, create a series of signal/slot connections per the :ref:`diagram <BackgroundSphinx diagram>` then run a thread which waits for a signal to arrive in the background Sphinx thread.
        self.thread_Sphinx = QtCore.QThread()
        self.background_sphinx = BackgroundSphinx()
        self.background_sphinx.moveToThread(self.thread_Sphinx)
        self.background_sphinx.signal_Sphinx_results.connect(self.Sphinx_results)
        self.background_sphinx.signal_Sphinx_done.connect(self.after_Sphinx)
        self.signal_Sphinx_start.connect(self.background_sphinx.run_Sphinx)
        self.thread_Sphinx.start()

        # Set up the file MRU from the registry
        self.mru_files = MruFiles(self, self.settings)
        # Load the last open, or choose a default file name and open it if it exists.
        if not self.mru_files.open_mru():
            self.open_contents()

    def on_code_changed(self, modified):
        if not self.ignore_code_modified:
            self.save_then_update_html()

# File operations
# ^^^^^^^^^^^^^^^
    # Open a new source file
    def open(self, source_file):
        # Split the source file into a path relative to the project direcotry, a base name, and an extension
        self.source_file = os.path.relpath(source_file)
        # Choose a language
        self.language_specific_options = LanguageSpecificOptions()
        self.language_specific_options.set_language(get_lexer_for_filename(source_file))
        # If this is a code-to-reST file, append .html to the filename
        if self.language_specific_options.comment_string:
            self.html_file = os.path.join(self.html_dir, self.source_file) + '.html'
        # Otherwise, replace the extension with .html
        else:
            head, tail = os.path.split(self.source_file)
            name, ext = os.path.splitext(tail)
            self.html_file = os.path.join(self.html_dir, head, name) + '.html'
        # Choose a lexer
        # Set style for comments to a fixed-width courier font.
        lexer_class = self.language_specific_options.lexer
        if lexer_class is not None:
            lexer = lexer_class()
            lexer.setDefaultFont(self.font)
            self.plainTextEdit.setLexer(lexer)
        else:
            # Disable lexer
            self.plainTextEdit.setLexer()
        self.plainTextEdit.SendScintilla(QsciScintilla.SCI_STYLESETFONT,
                                         QsciLexerCPP.Comment, 'Courier New')
        self.plainTextEdit.SendScintilla(QsciScintilla.SCI_STYLESETFONT,
                                         QsciLexerCPP.CommentLine, 'Courier New')
        self.plainTextEdit.SendScintilla(QsciScintilla.SCI_STYLESETFONT,
                                         QsciLexerCPP.CommentDoc, 'Courier New')
        self.setWindowTitle('CodeChat - ' + self.project_dir + ' - ' + self.source_file)
        self.reload()

    # Reload the source file then regenerate the HTML file from it, if necessary.
    def reload(self):
        assert not self.plainTextEdit.isModified()
        # Save the cursor position for the code view.
        # TODO: save selection, not just cursor position.
        code_pos = self.plainTextEdit.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS)
        # Reload text file
        try:
            with codecs.open(self.source_file, 'r', encoding = 'utf-8') as f:
                self.ignore_code_modified = True
                self.plainTextEdit.setText(f.read())
        except (IOError, ValueError) as e:
            self.ignore_code_modified = False
            QtGui.QMessageBox.critical(self, "CodeChat", str(e))
            return
        # Update modification time
        self.source_file_time = os.path.getmtime(self.source_file)
        self.plainTextEdit.setModified(False)
        self.ignore_code_modified = False
        self.mru_files.add_file(self.source_file)
        # Restore cursor positions
        self.plainTextEdit.SendScintilla(QsciScintilla.SCI_SETSEL, -1, code_pos)
        # Force a rebuild to display this new document
        self.need_to_build = True
        self.save_then_update_html()

    def open_contents(self):
        self.source_file = 'contents.rst'
        # If this file doesn't exist, create a blank one.
        if not os.path.exists(self.source_file):
            # Create a blank file
            try:
                with open(self.source_file, 'w'):
                    # Write nothing, so it's empty.
                    pass
            except IOError:
                print('Panic!')
        # Now open it.
        self.open(self.source_file)

    def eventFilter(self, obj, event):
        # Look for a switch to this application to check for an updated file. This is installed in main(). For more info, see http://qt-project.org/doc/qt-4.8/qobject.html#installEventFilter.
        if obj is self.app and event.type() == QtCore.QEvent.ApplicationActivate:
            try:
                if os.path.getmtime(self.source_file) != self.source_file_time:
                    self.reload()
            except os.error:
                # Ignore if the file no longer exists.
                pass

        # Look for idle time by resetting our timer on any event.
        if ( ((event.type() == QtCore.QEvent.KeyPress) or
              (event.type() == QtCore.QEvent.MouseMove)) and
              self.timer_sync_code_to_web.isActive() ):
            self.timer_sync_code_to_web.restart()

        # Allow default Qt event processing
        return QtGui.QMainWindow.eventFilter(self, obj, event)

    def save(self):
        try:
            with codecs.open(self.source_file, 'w', encoding = 'utf-8') as f:
                f.write(self.plainTextEdit.text())
            self.source_file_time = os.path.getmtime(self.source_file)
        except (IOError, ValueError) as e:
            QtGui.QMessageBox.critical(self, "CodeChat", str(e))
            return
        self.plainTextEdit.setModified(False)

    # If necessary, ask the user to save the current file before closing it. Returns True unless the user cancels.
    def save_before_close(self):
        if self.plainTextEdit.isModified():
            ret = QtGui.QMessageBox.warning(self, 'CodeChat', 'The file ' + self.source_file + ' had been modified. Do you want to save your changes?',
 QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard | QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Save)
            if ret == QtGui.QMessageBox.Save:
                self.save()
                return True
            elif ret == QtGui.QMessageBox.Discard:
                return True
            elif ret ==  QtGui.QMessageBox.Cancel:
                return False
            else:
                assert False
        else:
            return True

    # If the file on disk changed and the file is modified, ask the user which to keep. Returns True if the on disk file should be reloaded.
    def save_before_reload(self):
        if self.plainTextEdit.isModified():
            ret = QtGui.QMessageBox.warning(self, 'CodeChat', 'The file ' + self.source_file + ' had been edited and modified on disk. Do you want to save your changes, overwriting the changes on disk, or discard your changes and reload from disk?',
 QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard | QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Save)
            if ret == QtGui.QMessageBox.Save:
                self.save()
                return False
            elif ret == QtGui.QMessageBox.Discard:
                return True
            elif ret ==  QtGui.QMessageBox.Cancel:
                return False
            else:
                assert False
        else:
            return True

    def save_then_update_html(self):
        if self.is_building:
            return
        self.is_building = True

        # TODO: if Sphinx gets stuck, this will never save your work!
        if self.plainTextEdit.isModified():
            self.save()

        # Erase any previous build results.
        self.results_plain_text_edit.setPlainText('')
        # Start the Sphinx build in the background.
        self.signal_Sphinx_start.emit(self.html_dir)

    def Sphinx_results(self, results):
        # Append Sphinx build output. Just calling ``self.results_plain_text_edit.appendPlainText(results)`` appends an unnecessary newline.
        c = self.results_plain_text_edit.textCursor()
        c.movePosition(QtGui.QTextCursor.End)
        c.insertText(results)
        self.results_plain_text_edit.setTextCursor(c)
        # Scroll to bottom to show these results.
        self.results_plain_text_edit.ensureCursorVisible()

    def after_Sphinx(self, stderr):
        # Provide a "done" notification. Show stderr in red if available.
        html = '<pre>Done.\n</pre>'
        # If there's no stderr output, suppress the extra line created by a <pre>.
        if stderr:
            html += '<pre style="color:red">' + stderr + '</pre>'
        self.results_plain_text_edit.appendHtml(html)
        # Scroll to bottom to show these results.
        self.results_plain_text_edit.ensureCursorVisible()

        # Update the browser with Sphinx's output.
        if os.path.exists(self.get_html_file()):
            # Keep the same scroll position after reloading the file.
            slider_pos = self.textBrowser.verticalScrollBar().sliderPosition()
            self.textBrowser.setSource(self.html_url())
            # If the source URL doesn't change, but the file it points to does, reload it; otherwise, QT won't update itself.
            self.textBrowser.reload()
            self.textBrowser.verticalScrollBar().setSliderPosition(slider_pos)
        else:
            self.textBrowser.setHtml('')
        self.textBrowser.plain_text = self.textBrowser.toPlainText()

        # Resync web with code -- this also prevents the screen from jumping around (on a reload(), it jumps to the top). Since we're syncing now, cancel any future syncs.
        self.timer_sync_code_to_web.stop()
        self.code_to_web_sync()

        # Update state and start a new build if necessary
        self.is_building = False
        if self.plainTextEdit.isModified() or self.need_to_build:
            self.need_to_build = False
            self.save_then_update_html()

    def html_url(self):
        return QtCore.QUrl('file:///' + self.get_html_file().replace('\\', '/'))

    def get_html_file(self):
        return os.path.join(self.project_dir, self.html_file)

# Syncing between code and web
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    # When syncing, this code attempts to locate the same text in ther other view.
    #
    # To sync, find the same text under the plain text cursor in the htmn document and select around it to show the user where on the screen the equivalent content is.
    def code_to_web_sync(self):
        # If any links were clicked, go back to document matching the code view. Note: just calling setSource scrolls to the top of the document; to avoid this, only setSource if source changed.
        html_url = self.html_url()
        if self.textBrowser.source() != html_url and os.path.exists(self.get_html_file()):
            self.textBrowser.setSource(html_url)

        plainTextEdit_cursor_pos = self.plainTextEdit.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS)
        found = find_approx_text_in_target(self.plainTextEdit.text(),
                                           plainTextEdit_cursor_pos,
                                           self.textBrowser.plain_text)
        if found >= 0:
            # Select the line containing the found location
            cursor = self.textBrowser.textCursor()
            cursor.setPosition(found, QtGui.QTextCursor.MoveAnchor)
            cursor.select(QtGui.QTextCursor.LineUnderCursor)
            self.textBrowser.setTextCursor(cursor)
            # This scrolls the viewport so the hilighted text is often underneat the horizontal scroll bar. We want it to be centered in the viewport.
            self.textBrowser.ensureCursorVisible()
            cursor_center_y = self.textBrowser.cursorRect().top() + self.textBrowser.cursorRect().height()/2
            viewport_center_y = self.textBrowser.y() + self.textBrowser.height()/2
            delta = cursor_center_y - viewport_center_y
            # Note: We can't use the temptingly-named scrollContentsBy: per the `docs <http://doc.qt.digia.com/qt/qabstractscrollarea.html#scrollContentsBy>`_, "Calling this function in order to scroll programmatically is an error, use the scroll bars instead."
            self.textBrowser.verticalScrollBar().setSliderPosition(self.textBrowser.verticalScrollBar().sliderPosition() + delta)

    def web_to_code_sync(self):
        # Get the HTML as text, the source of our search string.
        search_text = self.textBrowser.plain_text
        search_index = self.textBrowser.textCursor().position()

        # If an image was clicked, insert its alt text in the search string.
        format = self.textBrowser.textCursor().charFormat()
        if format.isImageFormat():
            # This is the name of the image. Look through the html to find the alt tag following the image's name.
            image_path = format.toImageFormat().name()
            # Can't use self.textBrowser.toHtml(), since Qt strips out the alt tag, which we need. Instead, read it from the file.
            try:
                with open(self.get_html_file(), 'r') as html_file:
                    html = html_file.read()
                # Group 1 of this regular expression will contain the alt text.
                match = re.search('src="%s" alt="([^"]*)"' % re.escape(image_path), html)
                if match:
                    # If found, insert it at the cursor.
                    search_text = search_text[:search_index] + match.group(1) + search_text[search_index:]
                    #print('Searching for ' + match.group(1))
            except IOError:
                pass

        found = find_approx_text_in_target(search_text,
                                           search_index,
                                           self.plainTextEdit.text())
        # Update position in plain text widget if text was found.
        if found >= 0:
            self.plainTextEdit.SendScintilla(QsciScintilla.SCI_GOTOPOS, found)
        # Hide html, show plain text widgets. Placing this code at the beginning of this function makes it find the wrong location (???).
        self.plainTextEdit.setFocus()

    def change_project_dir(self, project_dir):
        try:
            os.chdir(project_dir)
        except OSError as e:
            QtGui.QMessageBox.critical(self, "CodeChat", str(e))
            return
        self.project_dir = project_dir
        self.settings.setValue(self.project_dir_key, self.project_dir)
        # Try loading the contents for this project.
        self.open_contents()

# Menu item actions
# ^^^^^^^^^^^^^^^^^
    # The decorator below prevents this method from being called twice, per http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/new_style_signals_slots.html#connecting-slots-by-name.
    @QtCore.pyqtSlot()
    def on_action_Create_new_project_triggered(self):
        project_dir = QtGui.QFileDialog.getExistingDirectory()
        if project_dir and self.save_before_close():
            template_dir = os.path.abspath(os.path.join(module_path, '../template'))
            # TODO: copytree works only if the directory doesn't exist, so tack on an extra name here. It would be better to simply place this in the indicated directory.
            project_dir = os.path.join(project_dir, 'template')
            try:
                shutil.copytree(template_dir, project_dir)
            except (shutil.Error, OSError) as e:
                QtGui.QMessageBox.critical(self, "CodeChat", str(e))
                return
            self.change_project_dir(project_dir)

    @QtCore.pyqtSlot()
    def on_action_Choose_project_dir_triggered(self):
        project_dir = QtGui.QFileDialog.getExistingDirectory()
        if project_dir and project_dir != self.project_dir and self.save_before_close():
            self.change_project_dir(project_dir)

    @QtCore.pyqtSlot()
    def on_action_Open_triggered(self):
        source_file = QtGui.QFileDialog.getOpenFileName()
        if source_file and self.save_before_close():
            self.open(source_file)

    @QtCore.pyqtSlot()
    def on_action_Reload_triggered(self):
        if self.save_before_reload():
            self.reload()

    @QtCore.pyqtSlot()
    def on_action_in_browser_triggered(self):
        self.save_then_update_html()
        QtGui.QDesktopServices.openUrl(self.html_url())

    def on_action_CodeChat_documentation_triggered(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl('http://bitbucket.org/bjones/documentation'))

    @QtCore.pyqtSlot()
    def on_action_ReST_cheat_sheet_triggered(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl('http://dl.dropbox.com/u/2337351/rst-cheatsheet.html'))

    def on_action_Sphinx_reST_primer_triggered(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl('http://sphinx-doc.org/rest.html'))

    @QtCore.pyqtSlot()
    def on_action_Sphinx_markup_triggered(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl('http://sphinx-doc.org/markup/index.html'))

    @QtCore.pyqtSlot()
    def on_action_LaTeX_math_reference_triggered(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl('http://en.wikibooks.org/wiki/LaTeX/Mathematics'))

    @QtCore.pyqtSlot()
    def on_action_GraphViz_reference_triggered(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl('http://www.graphviz.org/Documentation.php'))

    @QtCore.pyqtSlot()
    def on_action_About_triggered(self):
        QtGui.QMessageBox.about(self, 'CodeChat',
          u'CodeChat, a conversational coding system,\n' +
          u'was last revised on ' + version.PROGRAM_DATE + '.\n\n' +
          u'\u00A9 Copyright 2013 by Bryan A. Jones.')

    # Before closing the application, check to see if the user's work should be saved.
    def closeEvent(self, e):
        # If the user cancels, don't close.
        if not self.save_before_close():
            e.ignore()
        else:
            # Save settings
            self.settings.setValue("splitterSizes", self.splitter.saveState())
            self.settings.setValue("splitter_2Sizes", self.splitter_2.saveState())
            self.settings.setValue("windowState", self.saveState())
            self.settings.setValue("geometry", self.saveGeometry())
            # End Sphinx thread
            self.thread_Sphinx.quit()
            self.thread_Sphinx.wait()


# main()
# ------
# These routines run the CodeChat application.
def main():
    # Instantiate the app and GUI then run them
    app = QtGui.QApplication(sys.argv)
    window = CodeChatWindow(app)
    # Install an event filter to catch ApplicationActivate events (see CodeChatWindow.eventFilter)
    app.installEventFilter(window)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    # This line allows running this module as a script from Spyder. Without it, Sphinx reports ``Extension error: Could not import extension CodeChat.CodeToRest (exception: No module named CodeToRest)``.
    sys.path[0] = '.'
    main()
