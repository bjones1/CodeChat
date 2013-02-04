# .. -*- coding: utf-8 -*-
#
# CodeChat
# ========
#
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
# Unit test                         :doc:`CodeChat_test.py`
# ==============================    ===================
#
# .. contents::
#
# To do
# -----
# - Rewrite documentation in this program
# - Refactor to enable more unit testing
# - Preserve last cursor position in MRU list
# - Fix broken regexps for comments (#foo doesn't work)
# - Fix extensions in LanguageSpecificOptions
# - Create a short how-to video
# - Some way to display Sphinx errors then find the offending source line
# - Fix editor to render better HTML (long term -- probably QWebKit)
# - Port to Unix, Mac using CMake / CPack
#
# MRU list
# --------
# This class provides a most-recently-used (where "used" is updated when a document is opened) menu item and the functionality to load in files from the MRU list. It stores the MRU list in the registry.
#
# The default Python 3 PyQt interface provides automatic conversion between several basic Qt data types and their Puthon equivalent. For Python 2, to preserve compatibility with older apps, manual conversion is required. These lines select the Python 3 approach and must be executed before any PyQt imports. See http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/incompatible_apis.html for more information.
import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
# Not sure what this does -- I still have to use QtCore.QUrl to build urls. ??? It also makes the Spyder debugger mad, so omit for now.
## sip.setapi('QUrl', 2)

# The excellent `PyQt4 library <http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/classes.html>`_ provides the GUI for this package.
from PyQt4 import QtGui, QtCore, uic

import os
# A class to keep track of the most recently used files
class MruFiles(object):
    # Initialize the mru list and the File menu's MRU items
    def __init__(self, parent, settings):
        self.mru_list_key = "MRU list"
        self.max_files = 10
        self.settings = settings
        self.parent = parent
        # Create max_files QActions for mru entries and place them (hidden) in the File menu.
        self.mru_action_list = []
        for index in range(self.max_files):
            mru_item = QtGui.QAction(parent)
            mru_item.setVisible(False)
            if (index < 10):
                mru_item.setShortcut(QtGui.QKeySequence('Ctrl+' + str(index)))
            mru_item.triggered.connect(self.mru_triggered)
            parent.menu_File.addAction(mru_item)
            self.mru_action_list.append(mru_item)
        self.update_gui()

    def open_last(self):
        # Open the last file automatically
        mru_list = self.get_mru_list()
        if mru_list:
            file_name = str(mru_list[0])
            if os.path.exists(file_name):
                self.parent.open(file_name)
                return True
        return False

    # Called when an mru file is triggered
    @QtCore.pyqtSlot()
    def mru_triggered(self):
        # Determine which action sent this signal
        mru_action = self.parent.sender()
        if mru_action:
            # Get the file name stored within that action
            file_name = mru_action.data()
            self.parent.open(file_name)

    # Returns the mru list as a list
    def get_mru_list(self):
        return list(self.settings.value(self.mru_list_key, []))

    # Adds a file to the mru list
    def add_file(self, file_name):
        # Add file_name to the mru list, moving it to the top if it's already in the list
        mru_list = self.get_mru_list()
        if file_name in mru_list:
            mru_list.remove(file_name)
        mru_list.insert(0, file_name)
        # Trim the list if it is too long
        if len(mru_list) > self.max_files:
            mru_list.pop()
        # Update the stored mru list
        self.settings.setValue(self.mru_list_key, mru_list)
        # Update the GUI
        self.update_gui()

    def update_gui(self):
        # For each elemnt in the mru list, update the menu item
        mru_list = self.get_mru_list()
        for index in range(len(mru_list)):
            mru_action = self.mru_action_list[index]
            mru_action.setText('&%d %s' % (index, mru_list[index]))
            mru_action.setData(mru_list[index])
            mru_action.setVisible(True)
        # Hide the rest of the actions
        for index in range(len(mru_list), self.max_files):
            self.mru_action_list[index].setVisible(False)

class SphinxObject(QtCore.QObject):
    # run_Sphinx emits this with the results collected from the run as the first parameter.
    signal_Sphinx_done = QtCore.pyqtSignal(str)

    def run_Sphinx(self, html_dir):
        # Redirect Sphinx output to the results window
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        my_stdout = StringIO()
        my_stderr = StringIO()
        sys.stderr = my_stderr
        sphinx.cmdline.main( ('', '-b', 'html', '-d', '_build/doctrees', '-q',  '.', html_dir) )
        sys.stdout = old_stdout
        sys.stderr = old_stderr

        # Send a signal with the result string when Sphinx finishes.
        self.signal_Sphinx_done.emit(my_stdout.getvalue() + '\n' + my_stderr.getvalue())

# A convenience class to add a restart() method to a QTimer.
class RestartableTimer(QtCore.QTimer):
    def restart(self):
        self.stop()
        self.start()

# CodeChatWindow
# --------------
# This class provides the bulk of the functionality. Almost evrything is GUI logic; the text to HTML matching ability is imported.
#
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

# Scintilla_ (wrapped in Python) provides the text editor. However, the `Python documentation`_ for it was poor at best. Here's a `quick tutorial`_ I found helpful.
#
# .. _Scintilla: http://www.scintilla.org/ScintillaDoc.html
# .. _`Python documentation`: http://www.riverbankcomputing.co.uk/static/Docs/QScintilla2/annotated.html
# .. _`quick tutorial`: http://eli.thegreenplace.net/2011/04/01/sample-using-qscintilla-with-pyqt/
from PyQt4.Qsci import QsciScintilla, QsciLexerCPP

# Sphinx_ transforms reST_ to HTML, a core element of this tool.
#
# .. _Sphinx: http://sphinx.pocoo.org/
# .. _reST: http://docutils.sourceforge.net/docs/index.html
import sphinx.cmdline

# TODO: a better way?
# Pygments_ is used to match an extension (such as .cc or .cpp) to a file type (C++ source code).
#
# .. _Pygments: http://pygments.org/
from pygments.lexers import get_lexer_for_filename

from LanguageSpecificOptions import LanguageSpecificOptions

# The ability to match text in source code with text in HTML forms one of the core strengths of this module. See :doc:`FindLongestMatchingString.py` for details.
from FindLongestMatchingString import find_approx_text_in_target

# We need this to open and save text files in Unicode.
import codecs

# Display the version of this program in Htlp | About
import version

# Capture Sphinx's output for display in the GUI
from cStringIO import StringIO
import sys

# Use to copy new project file
import shutil

class CodeChatWindow(QtGui.QMainWindow, form_class):
    # This signal starts a Sphinx background run; the parameter is the HTML directory to use.
    signal_Sphinx_start = QtCore.pyqtSignal(str)

    def __init__(self, app, *args, **kwargs):
        # Let Qt and PyQt run their init first.
        QtGui.QMainWindow.__init__(self, *args, **kwargs)
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
        self.textBrowser.zoomIn(2)
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
        self.timer_sync_code_to_web = RestartableTimer()
        self.timer_sync_code_to_web.setSingleShot(True)
        self.timer_sync_code_to_web.setInterval(250)
        self.timer_sync_code_to_web.timeout.connect(self.code_to_web_sync)
        self.plainTextEdit.cursorPositionChanged.connect(lambda line, pos: self.timer_sync_code_to_web.restart())

        # Prepare for running Sphinx in the background. Getting this right was very difficult for me. My best references: I stole the code from http://stackoverflow.com/questions/6783194/background-thread-with-qthread-in-pyqt and tried to understand the explanation at http://qt-project.org/wiki/ThreadsEventsQObjects#913fb94dd61f1a62fc809f8d842c3afa.
        self.is_building = False
        self.need_to_build = True
        self.ignore_code_modified = False
        self.thread_Sphinx = QtCore.QThread()
        self.obj_sphinx = SphinxObject()
        self.obj_sphinx.moveToThread(self.thread_Sphinx)
        self.obj_sphinx.signal_Sphinx_done.connect(self.after_Sphinx)
        self.signal_Sphinx_start.connect(self.obj_sphinx.run_Sphinx)
        self.thread_Sphinx.start()

        # Set up the file MRU from the registry
        self.mru_files = MruFiles(self, self.settings)
        # Load the last open, or choose a default file name and open it if it exists.
        if not self.mru_files.open_last():
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

        if self.plainTextEdit.isModified():
            self.save()

        self.results_plain_text_edit.setPlainText('Sphinx running...')
        self.signal_Sphinx_start.emit(self.html_dir)

    def after_Sphinx(self, s):
        # Display Sphinx build output
        self.results_plain_text_edit.setPlainText(s)

        # Update the browser with Sphinx's output.
        if os.path.exists(self.get_html_file()):
            self.textBrowser.setSource(self.html_url())
        # If the source URL doesn't change, but the file it points to does, reload it; otherwise, QT won't update itself.
            self.textBrowser.reload()
        else:
            self.textBrowser.setHtml('')

        # Resync web with code -- this also prevents the screen from jumping around (on a reload(), it jump to the top). Since we're syncing now, cancel any future syncs.
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
                                           self.textBrowser.toPlainText())
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
        # Search for text under HTML cursor in plain text.
        textBrowser_cursor_pos = self.textBrowser.textCursor().position()
        found = find_approx_text_in_target(self.textBrowser.toPlainText(),
                                           textBrowser_cursor_pos,
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
    # Make Python think we're running from the parent directory, so Sphinx will find the CodeChat.CodeToRest extension.
    sys.path[0] = os.path.abspath('..')
    main()
