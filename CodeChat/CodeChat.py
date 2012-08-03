# :mod:`CodeChat` -- a conversational coding system
# ==============================================================================
#
# .. module:: CodeChat
#    :synopsis: a conversational coding system
# .. moduleauthor::  Bryan A. Jones <bjones AT ece DOT msstate DOT edu>
# .. sectionauthor:: Bryan A. Jones <bjones AT ece DOT msstate DOT edu>
#
# The :doc:`../README` user manual gives a broad overview of this system. In contrast, this document discusses the implementation specifics of the CodeChat system. The table below shows the overall structure of this package; the to do list reflects changes needed to make this happen.
#
# ==========================   ===================
# Functionality                Module
# ==========================   ===================
# GUI                          :mod:`CodeChat`
# Source code to reST          :mod:`CodeToRest`
# Synchronize code and HTML    :mod:`CodeSync`
# Unit test                    :mod:`CodeChatTest`
# ==========================   ===================
#
# .. contents::
#
# To do
# ==============================================================================
# I've now used my system for a while and I find it very helpful, but also filled with bugs and msising features. Where is the most effective place to begin working? I'll start by listing the problems I'm aware of.
#
# Useability:
#
# - Ask the user to save if necessary
# - An auto-save / auto-build feature.
# - Add a "choose home directory" feature
# - Fix home to go to beginning of line, not beginning of paragraph.
# - Do a better job of restoring the old cursor location after a save and build
# - Synchronize scrolling / position within window
# - Support multiple open docs
# - Fix editor to render better HTML (long term -- probably QWebKit)
# - Fix / improve false positives on inexact matches
# - Fix sync bugs where an update in one pane doesn't update in the other pane
# - Fix broken regexps for comments
#
# Development:
#
# - Make this into an installable package
# - Separate GUI code from core update / match code
# - Unit testing
# - Figure out how to document / explain this program
# - Fix extensions in LanguageSpecificOptions
#
# Old:
#
# - Factor out sync code into CodeSync
# - Document what I've got
# - More unit testing
# - Run Sphinx in the background. This makes the plain text area a more effective word processor.
# - Look at using QWebKit, since the QTextEdit doesn't render Sphinx's HTML well.
#
# Imports
# ==============================================================================

# We begin by importing necessary functionality.
import sys, os

# We need to read and write in Unicode.
import codecs

# The excellent `PyQt4 library`_ provides the GUI for this module.
#
# .. _`PyQt4 library`: http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/classes.html
from PyQt4 import QtGui, QtCore, uic

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

# Pygments_ performs syntax highlighting. Its lexer also enables the code-to-reST process (see :doc:`CodeToRest.py`).
#
# .. _Pygments: http://pygments.org/
from pygments.lexers import get_lexer_for_filename

from LanguageSpecificOptions import LanguageSpecificOptions

# The ability to match text in source code with text in HTML forms one of the core strengths of this module. See :doc:`FindLongestMatchingString.py` for details.
from FindLongestMatchingString import find_approx_text_in_target


# A class to keep track of the most recently used files
class MruFiles(object):
    mru_list_key = "MRU list"
    max_files = 10
    
    # Initialize the mru list and the File menu's MRU items
    def __init__(self, parent):
        self.settings = QtCore.QSettings("MSU BJones", "CodeChat")
        self.parent = parent
        # Create max_files QActions for mru entries and place them (hidden) in the File menu.
        self.mru_action_list = []
        for index in range(self.max_files):
            mru_item = QtGui.QAction(parent)
            mru_item.setVisible(False)
            mru_item.setShortcut(QtGui.QKeySequence('Ctrl+' + str(index)))
            mru_item.triggered.connect(self.mru_triggered)
            parent.menu_File.addAction(mru_item)
            self.mru_action_list.append(mru_item)
            
    def open_last(self):
        # Open the last file automatically
        mru_list = self.get_mru_list()
        if mru_list:
            file_name = str(mru_list[0])
            if os.path.exists(file_name):
                self.parent.open(file_name)

    # Called when an mru file is triggered
    @QtCore.pyqtSlot()
    def mru_triggered(self):
        # Determine which action sent this signal
        mru_action = self.parent.sender()
        if mru_action:
            # Get the file name stored within that action
            file_name = str(mru_action.data().toPyObject())
            self.parent.open(file_name)
        
    # Returns the mru list as a lit
    def get_mru_list(self):
        mru_list = self.settings.value(self.mru_list_key).toPyObject()
        if not mru_list:
            mru_list = []
            self.settings.setValue(self.mru_list_key, mru_list)
            return mru_list
        else:
            return list(mru_list)
            
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


# If imported, find the path to the .ui file; if run directly, assume it's in the current directory.
try:
    ui_path = os.path.dirname(__file__)
except NameError:
    ui_path = '.'
form_class, base_class = uic.loadUiType(ui_path + "/CodeChat.ui")
# CodeChatWindow
# ==============================================================================
class CodeChatWindow(QtGui.QMainWindow, form_class):
    def __init__(self, app, *args, **kwargs):
        # Store a reference to this window's containing application
        self.app = app
        self.ignore_next = True
        QtGui.QMainWindow.__init__(self, *args, **kwargs)
        # For debug ease, change to project directory
        #os.chdir('C:\\Users\\bjones\\Documents\\modbus\\snort')
#        os.chdir('C:\\Users\\bjones\\Documents\\micro_book')
        os.chdir('C:\\Users\\bjones\\Documents\\documentation')
#        os.chdir('C:\\Users\\bjones\\Documents\\ece3724\\ece3724-private\\test_solutions')
#        os.chdir('C:\\Users\\bjones\\Documents\\robotics_research\moisture_meter')
#        os.chdir('C:\\robotics_research\\rc_car\\GPIOToggle')
        # Temporary hack: assume the project directory is the startup directory
        # Save project dir: HTML loading requires a change to the HTML direcotry,
        # while all else is relative to the project directory.
        self.project_dir = os.getcwd()
        # A path to the generated HTML files, relative to the project directory
        self.html_dir = '_build/html'
        self.setupUi(self)
        # Select a larger font for the HTML editor
        self.textEdit.zoomIn(2)
# Configure QScintilla
# --------------------
        # Set the default font
        self.font = QtGui.QFont()
        self.font.setFamily('Courier New')
        self.font.setFixedPitch(True)
        self.font.setPointSize(10)        
        # Margin 0 is used for line numbers
        fontmetrics = QtGui.QFontMetrics(self.font)
        self.plainTextEdit.setMarginsFont(self.font)
        self.plainTextEdit.setMarginWidth(0, fontmetrics.width("00000") + 6)
        self.plainTextEdit.setMarginLineNumbers(0, True)
        self.plainTextEdit.setMarginsBackgroundColor(QtGui.QColor("#cccccc"))
        # Brace matching: enable for a brace immediately before or after
        # the current position
        self.plainTextEdit.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        # Enable word wrap
        self.plainTextEdit.setWrapMode(QsciScintilla.WrapWord)
        
        # Ask for notification when the contents of either editor change
        self.textEdit.document().contentsChange.connect(self.on_textEdit_contentsChange)
        self.plainTextEdit.SCN_MODIFIED.connect(self.on_plainTextEdit_modified)
        # However, send only inserts and deletes for plain text. See
        # http://www.scintilla.org/ScintillaDoc.html#SCI_SETMODEVENTMASK.
        self.plainTextEdit.SendScintilla(QsciScintilla.SCI_SETMODEVENTMASK, 
                                         QsciScintilla.SC_MOD_INSERTTEXT |
                                         QsciScintilla.SC_MOD_DELETETEXT)
        # Enable/disable the update button when the plain text modification
        # state changes.
        self.plainTextEdit.modificationChanged.connect(
            lambda changed: self.action_Save_and_update.setEnabled(changed))
        self.ignore_next = False
        # Save initial cursor positions
        self.textEdit_cursor_pos = self.textEdit.textCursor().position()
        self.plainTextEdit_cursor_pos = self.plainTextEdit.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS)
        # Set up the file MRU from the registry
        self.mru_files = MruFiles(self)
        self.mru_files.open_last()
        
    def on_textEdit_contentsChange(self, position, charsRemoved, charsAdded):
        if not self.ignore_next:
#            print 'HTML position %d change: %d chars removed, %d chars added.' % (position, charsRemoved, charsAdded)
            self.ignore_next = True
            # To make the inactive "cursor" visible when no selection is made in the html window, the plain text pane cursor is replaced by a two-character selection, which will confuse any edits made. Go back to a cursor if there's no selection in the html window.
            old_text_cursor_pos = self.textEdit_cursor_pos
            cursor = self.textEdit.textCursor()
            self.textEdit_cursor_pos = cursor.position()
            if cursor.anchor() == self.textEdit_cursor_pos:
                self.plainTextEdit.SendScintilla(QsciScintilla.SCI_SETSEL, -1, self.plainTextEdit_cursor_pos)
            # If there are deletions, find out where in the plain text document
            # we must delete from
            if charsRemoved > 0:
                # A range - delete the entire range
                if self.plainTextEdit.SendScintilla(QsciScintilla.SCI_GETANCHOR) != \
                    self.plainTextEdit.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS):
                    self.plainTextEdit.SendScintilla(QsciScintilla.SCI_CLEAR)
                # The delete key - just delete from the current position
                elif position == old_text_cursor_pos:
                    assert charsRemoved == 1
                    self.plainTextEdit.SendScintilla(QsciScintilla.SCI_CLEAR)
                # The backspace key - move back 1 char (if possible) and delete
                elif position == (old_text_cursor_pos - 1):
                    assert charsRemoved == 1
                    # Try to move the cursor back
                    self.ignore_next = False
                    self.on_textEdit_cursorPositionChanged(False)
                    self.ignore_next = True
                    # Signal an error if we can't
                    if self.textEdit.isReadOnly():
                        print 'Oops -- cannot find changed text!'
                        self.textEdit.undo()
                        return
                    # Then delete the char
                    self.plainTextEdit.SendScintilla(QsciScintilla.SCI_CLEAR)
            self.plainTextEdit.insert(self.textEdit.toPlainText()[position:position + charsAdded])
            self.ignore_next = False
        
    def on_plainTextEdit_modified(self, position, modificationType, text,
                                  length, linesAdded, line, foldLevelNow,
                                  foldLevelPrev, token, annotationLinesAdded):
        # See the SCN_MODIFIED_ message for a description of the above 
        # parameters; the notifications_ section contains more info. We're
        # primarily interested in translating the modificationType into
        # QTextEdit-like charAdded and charRemoved (for now)
        #
        # .. _SCN_MODIFIED: http://www.scintilla.org/ScintillaDoc.html#SCN_MODIFIED
        # .. _notifications: http://www.scintilla.org/ScintillaDoc.html#Notifications
        (charsAdded, charsRemoved) = (0, 0)
        if modificationType & QsciScintilla.SC_MOD_INSERTTEXT:
            charsAdded = length
        if modificationType & QsciScintilla.SC_MOD_DELETETEXT:
            charsRemoved = length
        # Shouldn't have both chars added and deleted at the same time.
        assert (charsAdded == 0) or (charsRemoved == 0)
        if (not self.ignore_next) and (not self.textEdit.isReadOnly()):
#            print 'Plain position %d change: %d chars removed, %d chars added.' % (position, charsRemoved, charsAdded)
            self.ignore_next = True
            # To make the inactive "cursor" visible when no selection is made in the plain text window, the html pane cursor is replaced by a two-character selection, which will confuse any edits made. Go back to a cursor if there's no selection in the plain text window.
            old_plain_text_cursor_pos = self.plainTextEdit_cursor_pos
            self.plainTextEdit_cursor_pos = self.plainTextEdit.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS)
            plainTextEdit_sel_pos = self.plainTextEdit.SendScintilla(QsciScintilla.SCI_GETANCHOR)
            if self.plainTextEdit_cursor_pos == plainTextEdit_sel_pos:
                text_cursor = self.textEdit.textCursor()
                text_cursor.setPosition(self.textEdit_cursor_pos)
                self.textEdit.setTextCursor(text_cursor)
            # If there are deletions, find out where in the html document
            # we must delete from
            if charsRemoved > 0:
                # A range - delete the entire range
                text_cursor = self.textEdit.textCursor()
                if text_cursor.anchor() != text_cursor.position():
                    self.textEdit.textCursor().removeSelectedText()
                # The delete key - just delete from the current position
                elif position == old_plain_text_cursor_pos:
                    assert charsRemoved == 1
                    self.textEdit.textCursor().deleteChar()
                # The backspace key - move back 1 char (if possible) and delete
                elif position == (old_plain_text_cursor_pos - 1):
                    assert charsRemoved == 1
                    # Resync the cursor in the other pane, but don't place a highlight there.
                    self.ignore_next = False
                    self.on_plainTextEdit_cursorPositionChanged(0, 0, False)
                    self.ignore_next = True
                    # Then delete the char
                    self.textEdit.textCursor().deleteChar()
            # Insert text in html pane added to the plain text pane
            self.textEdit.textCursor().insertText(self.plainTextEdit.text()[position:position + charsAdded])
            self.ignore_next = False
        
    def update_html(self):
        # Restore current dir
        os.chdir(self.project_dir)
        print('\n\n')
        sphinx.cmdline.main( ('', '-b', 'html', '-d', '_build/doctrees', '-q', 
                              '.', self.html_dir) )
        # Load in the updated html, if we can
        try:
            with codecs.open(self.html_file, 'r', encoding = 'utf-8') as f:
                str = f.read()
            # Temporarily change to the HTML directory to load html, so Qt can access all
            # the HTML resources (style sheets, images, etc.)
            head, tail = os.path.split(self.html_file)
            os.chdir(head)
        except IOError:
            # If we can't open the file, make it empty
            str = ''
        self.ignore_next = True
        self.textEdit.setHtml(str)
        self.ignore_next = False
    
    def set_html_editable(self, can_edit):
        # Calling self.textEdit.setReadOnly(False) disables
        # keyboard navigation. Use this to retain key nav.
        old_flags = int(self.textEdit.textInteractionFlags())
        new_flags = old_flags | QtCore.Qt.TextEditable if can_edit \
               else old_flags & ~QtCore.Qt.TextEditable
        self.textEdit.pyqtConfigure(textInteractionFlags = new_flags)
        
    def on_plainTextEdit_cursorPositionChanged(self, line, index, select_html_pane = True):
#        print "Plain cursor pos now %d." % self.plainTextEdit_cursor_pos
        if not self.ignore_next:
            self.plainTextEdit_cursor_pos = self.plainTextEdit.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS)
            found = find_approx_text_in_target(unicode(self.plainTextEdit.text()),
                                               self.plainTextEdit_cursor_pos,
                                               unicode(self.textEdit.toPlainText()))
            if found >= 0:
                pos = self.textEdit.textCursor()
                # Is there a selection in the text pane?
                if (self.plainTextEdit.SendScintilla(QsciScintilla.SCI_GETANCHOR) ==
                    self.plainTextEdit_cursor_pos):
                    if select_html_pane == True:
                        # There's no selection, so create a two-character selection around the cursor so that it's visible, because a cursor with no selection is hidden in widgets without focus.
                        pos.setPosition(found - 1,
                            QtGui.QTextCursor.MoveAnchor)
                        pos.setPosition(found + 1,
                            QtGui.QTextCursor.KeepAnchor)
                    else:
                        # Just place the cursor at the found location
                        pos.setPosition(found,
                            QtGui.QTextCursor.MoveAnchor)
                    # Save the original cursor location
                    self.textEdit_cursor_pos = found
                else:
                    # Yes, so change the HTML pane selection to match the text pane selection.
                    pos.setPosition(found, QtGui.QTextCursor.MoveAnchor)
                self.ignore_next = True
                self.textEdit.setTextCursor(pos)
                self.set_html_editable(True)
                self.ignore_next = False
            else:
                self.ignore_next = True
                # There's no matching location in the HTML pane, so mark that pane as uneditable.
                self.set_html_editable(False)
                # If there's a selection, clear it, since we can't determine the cursor location of at least one side of the selection.
                cursor = self.textEdit.textCursor()
                if cursor.hasSelection():
                    cursor.clearSelection()
                    self.textEdit.setTextCursor(cursor)
                self.ignore_next = False
        
    def on_textEdit_cursorPositionChanged(self, select_plain_text = True):
        if not self.ignore_next:
            cursor = self.textEdit.textCursor()
            self.textEdit_cursor_pos = cursor.position()
            found = find_approx_text_in_target(unicode(self.textEdit.toPlainText()),
                                               self.textEdit_cursor_pos,
                                               unicode(self.plainTextEdit.text()))
            # Update position in source doc if text was found
            if found >= 0:
                self.ignore_next = True
                # Is there a selection in the HTML pane?
                if (cursor.anchor() == cursor.position()):
                    if select_plain_text:
                        # There's no selection, so create a two-character selection around the cursor so that it's visible, because a cursor with no selection is hidden in widgets without focus.
                        self.plainTextEdit.SendScintilla(QsciScintilla.SCI_SETSEL, found - 1, found + 1)
                    else:
                        # Just place the cursor at the found location
                        self.plainTextEdit.SendScintilla(QsciScintilla.SCI_SETSEL, -1, found)
                    # Save the original cursor location
                    self.plainTextEdit_cursor_pos = found
                else:
                    # Yes, so change the HTML pane selection to match the text pane selection.
                    self.plainTextEdit.SendScintilla(QsciScintilla.SCI_SETCURRENTPOS, found)
                # Scroll cursor into view
                self.plainTextEdit.SendScintilla(QsciScintilla.SCI_SCROLLCARET)
                # The above messages won't be process now, so the self.ignore_next fails to prevent the text pane from attempting to process these cursor changes. Therefore, we must process all messages (particuarly these just sent to the text pane) now, while self.ignore_next is still False.
                self.app.processEvents()
                self.set_html_editable(True)
                self.ignore_next = False
            else:
                # If there's a selection, clear it, since we can't determine the cursor location of at least one side of the selection.
                self.ignore_next = True
                plain_cursor_pos = self.plainTextEdit.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS)
                self.plainTextEdit.SendScintilla(QsciScintilla.SCI_SETANCHOR, plain_cursor_pos)
                self.set_html_editable(False)
                self.ignore_next = False

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
        self.plainTextEdit.SendScintilla(QsciScintilla.SCI_STYLESETFONT, 
                                         QsciLexerCPP.Comment, 'Courier New')
        self.plainTextEdit.SendScintilla(QsciScintilla.SCI_STYLESETFONT, 
                                         QsciLexerCPP.CommentLine, 'Courier New')
        self.plainTextEdit.SendScintilla(QsciScintilla.SCI_STYLESETFONT, 
                                         QsciLexerCPP.CommentDoc, 'Courier New')
        self.reopen()
         
    # Reload the source file then regenerate the HTML file from it.
    def reopen(self):
        # Restore current dir
        os.chdir(self.project_dir)
        with codecs.open(self.source_file, 'r', encoding = 'utf-8') as f:
            self.ignore_next = True
            self.plainTextEdit.setText(f.read())
            self.ignore_next = False
        self.update_html()
        self.plainTextEdit.setModified(False)
        self.mru_files.add_file(self.source_file)
        
    # The decorator below prevents this method from being called twice, per
    # http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/new_style_signals_slots.html#connecting-slots-by-name
    @QtCore.pyqtSlot()
    def on_action_Reopen_triggered(self):
        self.reopen()
        
    @QtCore.pyqtSlot()
    def on_action_Open_triggered(self):
        # Restore current dir
        os.chdir(self.project_dir)
        source_file = QtGui.QFileDialog.getOpenFileName()
        if source_file:
            self.open(unicode(source_file))
               
    @QtCore.pyqtSlot()
    def on_action_Save_and_update_triggered(self):
        # Restore current dir
        os.chdir(self.project_dir)
        with codecs.open(self.source_file, 'w', encoding = 'utf-8') as f:
            f.write(unicode(self.plainTextEdit.text()))
        self.plainTextEdit.setModified(False)
        self.ignore_next = True
        self.update_html()
        self.ignore_next = False
        # Resync panes.
        self.on_plainTextEdit_cursorPositionChanged(0, 0)


def main():
    # Instantiate the app and GUI then run them
    app = QtGui.QApplication(sys.argv)
    window = CodeChatWindow(app)
    window.setWindowState(QtCore.Qt.WindowMaximized)
    window.show()
    sys.exit(app.exec_())
    
def profile():
    import cProfile
    import pstats
    cProfile.run('main()', 'mainprof')
    p = pstats.Stats('mainprof')
    p.strip_dirs().sort_stats('time').print_stats(10)

if __name__ == '__main__':
    main()
#    profile()
