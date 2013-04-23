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
# ************************************************************************
# CodeChat.py - create the GUI which ties together the entire application.
# ************************************************************************
# .. module:: CodeChat
#
# Imports
# =======
# These are listed in the order prescribed by `PEP 8 <http://www.python.org/dev/peps/pep-0008/#imports>`_.
#
# Standard library
# ----------------
# We need this to open and save text files in Unicode.
import codecs
import sys
# Use to copy a new project file.
import shutil
# Used to search for alt text in generated HTML.
import re
import os
#
# Third-party imports
# -------------------
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

# `Pygments <http://pygments.org/>`_ is used to match an extension (such as .cc or .cpp) to a file type (C++ source code).
from pygments.lexers import get_lexer_for_filename
#
# Local application imports
# -------------------------
from CodeChatUtils import MruFiles, BackgroundSphinx, QRestartableTimer
from LanguageSpecificOptions import LanguageSpecificOptions

# The ability to match text in source code with text in HTML forms one of the core strengths of this module. See :doc:`FindLongestMatchingString.py` for details.
from FindLongestMatchingString import find_approx_text_in_target

# Display the version of this program in Help | About.
import version

# GUI layout import
# -----------------
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

# CodeChatWindow
# ==============
# This class provides four distinct categories of functionality:
#
# .. contents::
#    :local:
#    :depth: 1
class CodeChatWindow(QtGui.QMainWindow, form_class):
    # This signal starts a Sphinx background run; the parameter is the HTML directory to use. See :ref:`Background-Sphinx-execution` for more information.
    signal_Sphinx_start = QtCore.pyqtSignal(unicode)
#
# Initialization / finalization
# -----------------------------
    def __init__(self, app, multiprocessing_Sphinx_manager):
        # Let Qt and PyQt run their init first.
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)

        # Store constructor args.
        self.app = app
        self.multiprocessing_Sphinx_manager = multiprocessing_Sphinx_manager

        self.project_dir_key = 'project directory'
        # A path to the generated HTML files, relative to the project directory
        self.html_dir = '_build/html'
        self.settings = QtCore.QSettings("MSU BJones", "CodeChat")

        # Open the last project directory of we can; otherwise, use the current directory.
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

# Configure QScintilla
# ^^^^^^^^^^^^^^^^^^^^
        # Set the default font.
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

        # Brace matching: enable for a brace immediately before or after the current position.
        self.plainTextEdit.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        # Enable word wrap.
        self.plainTextEdit.setWrapMode(QsciScintilla.WrapWord)

        # Make home go to the beginning of the line, then to the first non-blank character in the paragraph, then to the beginning of the paragraph. Have end go to the end of the line, then to the end of the paragraph. Default behavior is to always go to the beginning/end of the paragraph.
        self.plainTextEdit.SendScintilla(QsciScintilla.SCI_ASSIGNCMDKEY, QsciScintilla.SCK_HOME, QsciScintilla.SCI_VCHOMEWRAP)
        self.plainTextEdit.SendScintilla(QsciScintilla.SCI_ASSIGNCMDKEY, QsciScintilla.SCK_END, QsciScintilla.SCI_LINEENDWRAP)
        # Use this for shift+home/end as well.
        self.plainTextEdit.SendScintilla(QsciScintilla.SCI_ASSIGNCMDKEY, QsciScintilla.SCK_HOME + (QsciScintilla.SCMOD_SHIFT << 16), QsciScintilla.SCI_VCHOMEWRAPEXTEND)
        self.plainTextEdit.SendScintilla(QsciScintilla.SCI_ASSIGNCMDKEY, QsciScintilla.SCK_END + (QsciScintilla.SCMOD_SHIFT << 16), QsciScintilla.SCI_LINEENDWRAPEXTEND)

        # Try at removing ctrl-T key binding (use as toggle views instead). Fails -- just using SCI_CLEARCMDKEY produces no action (i.e. keystroke isn't acted on by Scintilla, but isn't passed to QT either)
        ## self.plainTextEdit.SendScintilla(QsciScintilla.SCI_ASSIGNCMDKEY, ord('T') + (QsciScintilla.SCMOD_CTRL << 16), 0)

        # Show a differenct background for the line the cursor is in.
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

        # This needs to be set, since the timer above will expire before self.textBrowser.plain_text is set by after_Sphinx.
        self.textBrowser.plain_text = ''

        # Use UTF-8.
        self.plainTextEdit.SendScintilla(QsciScintilla.SCI_SETCODEPAGE, QsciScintilla.SC_CP_UTF8)

# TODO: A better title for this section
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        # First, set up state variables used to do invoke a background Sphinx run.
        self.is_building = False
        self.need_to_build = True
        self.ignore_code_modified = False

        # Start up the background Sphinx thread.
        self.background_sphinx = BackgroundSphinx(self)

        # Set up the file MRU from the registry.
        self.mru_files = MruFiles(self, self.settings)
        # Load the last open, or choose a default file name and open it if it exists.
        if not self.mru_files.open_mru():
            self.open_contents()

# Need to categorize / move
# ^^^^^^^^^^^^^^^^^^^^^^^^^
    def on_code_changed(self, modified):
        if not self.ignore_code_modified:
            self.save_then_update_html()

    # Before closing the application, check to see if the user's work should be saved.
    def closeEvent(self, e):
        # If the user cancels, don't close.
        if not self.save_before_close():
            e.ignore()
        else:
            # Save settings.
            self.settings.setValue("splitterSizes", self.splitter.saveState())
            self.settings.setValue("splitter_2Sizes", self.splitter_2.saveState())
            self.settings.setValue("windowState", self.saveState())
            self.settings.setValue("geometry", self.saveGeometry())
            # End the background Sphinx thread by requesting the event loop to shut down, then waiting for it to do so.
            self.multiprocessing_Sphinx_manager.finalize()
            self.background_sphinx.thread.quit()
            self.background_sphinx.thread.wait()

# File operations
# ---------------
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
                with codecs.open(self.source_file, 'w', encoding = 'utf-8'):
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
# ----------------------------
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
# -----------------
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


# main()
# ======
# These routines run the CodeChat GUI.
def main(multiprocessing_Sphinx_manager):
    # Instantiate the app and GUI then run them
    app = QtGui.QApplication(sys.argv)
    window = CodeChatWindow(app, multiprocessing_Sphinx_manager)
    # Install an event filter to catch ApplicationActivate events (see CodeChatWindow.eventFilter)
    app.installEventFilter(window)
    window.show()
    sys.exit(app.exec_())
