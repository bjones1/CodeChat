# :mod:`CodeChat` -- a conversational coding system
# ==============================================================================
#
# .. module:: CodeChat
#    :synopsis: a conversational coding system
# .. moduleauthor::  Bryan A. Jones <bjones AT ece DOT msstate DOT edu>
# .. sectionauthor:: Bryan A. Jones <bjones AT ece DOT msstate DOT edu>
#
# The :doc:`README` user manual gives a broad overview of this system. In contrast, this document discusses the implementation specifics of the CodeChat system. The table below shows the overall structure of this package; the to do list reflects changes needed to make this happen.
#
# ==========================   ===================
# Functionality                Module
# ==========================   ===================
# GUI                          :mod:`CodeChat`
# Source code to HTML          :mod:`CodeToHtml`
# Synchronize code and HTML    :mod:`CodeSync`
# Unit test                    :mod:`CodeChatTest`
# ==========================   ===================
#
# .. contents::
#
# To do
# ==============================================================================
#
# - Factor out update_html and rename CodeToRest
# - Factor out sync code into CodeSync
# - Document what I've got
# - More unit testing
# - Run Sphinx in the background. This makes the plain text area a more effective word processor.
# - Look at using QWebKit, since the QTextEdit doesn't render Sphinx's HTML well.
#
# .. includes:: CodeChat.rst
#    :start-after: LanguageSpecificOptions
#    :end-before: CodeChatWindow
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
from PyQt4.Qsci import QsciScintilla, QsciLexerCPP, QsciLexerPython

# Sphinx_ transforms reST_ to HTML, a core element of this tool.
#
# .. _Sphinx: http://sphinx.pocoo.org/
# .. _reST: http://docutils.sourceforge.net/docs/index.html
import sphinx.cmdline

# Pygments_ performs syntax highlighting. Its lexer also enables the code-to-reST process (see :doc:`CodeToRest`).
#
# .. _Pygments: http://pygments.org/
from pygments.lexers.compiled import CLexer, CppLexer
from pygments.lexers.agile import PythonLexer
from pygments.lexers.text import RstLexer
from pygments.lexers.asm import NasmLexer

# The ability to match text in source code with text in HTML forms one of the core strengths of this module. See :doc:`FindLongestMatchingString` for details.
from FindLongestMatchingString import find_approx_text_in_target

# The ability to transform source code directly to HTML represents another core strength. See :doc:`CodeToRest`.
from CodeToRest import CodeToRest, get_lexer_for_filename

import re

# Language Specific Options
# ==============================================================================
# For each programming language supported, :meth:`set_language` specifies:
#
# .. attribute:: comment_string
#
#    The string indicating the beginning of a comment in the chosen programming language, or None if the CodeToRest process isn't supported. This must end in a space for the regular expression in format to work. The space also makes the output a bit prettier.
#
# .. attribute:: unique_remove_comment
#
#    A unique comment used to mark a line which will be removed later, or None if the CodeToRest process isn't supported. This is used to trick reST / Sphinx into generating the correct indention.
#
# .. attribute:: lexer
#
#    The QScintilla lexer to use, or None to disable syntax highlighting in the text pane
#
# .. class:: LanguageSpecificOptions()
class LanguageSpecificOptions(object):
    # .. attribute:: unique_remove_str
    #
    #    A unique string to mark lines for removal in HTML.
    unique_remove_str = 'wokifvzohtdlm'
    
    # .. attribute:: language_specific_options
    #
    #    A tuple of language-specific options, indexed by the class of the parser which Pygments selects.
    language_specific_options = {
    # ::
    # 
    #  Pygments  lexer
    #  |                            Comment string
    #  |                            |        Removal string (should be a comment)
    #  |                            |        |                              QScintilla lexer
      CLexer().__class__      : ('//', '// ' + unique_remove_str, QsciLexerCPP),
      CppLexer().__class__    : ('// ', '// ' + unique_remove_str, QsciLexerCPP),
      PythonLexer().__class__ : ('# ' , '# '  + unique_remove_str, QsciLexerPython),
      RstLexer().__class__    : (None ,  None                    , None),
      NasmLexer().__class__   : ('; ' , '; '  + unique_remove_str, None),
    }

    # .. method:: set_language(language_)
    #
    #    Sets the :class:`LanguageSpecificOptions` offered, where *language_* gives the Pygments lexer for the desired language.
    def set_language(self, language_):
        language = language_.__class__
        self.comment_string = self.language_specific_options[language][0]        
        self.unique_remove_comment = self.language_specific_options[language][1]
        self.lexer = self.language_specific_options[language][2]


form_class, base_class = uic.loadUiType("CodeChat.ui")
# CodeChatWindow
# ==============================================================================
class CodeChatWindow(QtGui.QMainWindow, form_class):
    def __init__(self, app, *args, **kwargs):
        # Store a reference to this window's containing application
        self.app = app
        self.ignore_next = True
        QtGui.QMainWindow.__init__(self, *args, **kwargs)
        # Save current dir: HTML loading requires a change to the HTML direcotry,
        # while Sphinx needs current dir.
        self.current_dir = os.getcwd()
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
        
    def on_textEdit_contentsChange(self, position, charsRemoved, charsAdded):
        if not self.ignore_next:
#            print 'HTML position %d change: %d chars removed, %d chars added.' % (position, charsRemoved, charsAdded)
            self.ignore_next = True
            # If there are deletions, find out where in the plain text document
            # we must delete from
            if charsRemoved > 0:
                # A range - delete the entire range
                if self.plainTextEdit.SendScintilla(QsciScintilla.SCI_GETANCHOR) != \
                    self.plainTextEdit.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS):
                    self.plainTextEdit.SendScintilla(QsciScintilla.SCI_CLEAR)
                # The delete key - just delete from the current position
                elif position == self.textEdit_cursor_pos:
                    assert charsRemoved == 1
                    self.plainTextEdit.SendScintilla(QsciScintilla.SCI_CLEAR)
                # The backspace key - move back 1 char (if possible) and delete
                elif position == (self.textEdit_cursor_pos - 1):
                    assert charsRemoved == 1
                    # Try to move the cursor back
                    self.ignore_next = False
                    self.on_textEdit_cursorPositionChanged(position)
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
            # If there are deletions, find out where in the html document
            # we must delete from
            if charsRemoved > 0:
                # A range - delete the entire range
                text_cursor = self.textEdit.textCursor()
                if text_cursor.anchor() != text_cursor.position():
                    self.textEdit.textCursor().removeSelectedText()
                # The delete key - just delete from the current position
                elif position == self.plainTextEdit_cursor_pos:
                    assert charsRemoved == 1
                    self.textEdit.textCursor().deleteChar()
                # The backspace key - move back 1 char (if possible) and delete
                elif position == (self.plainTextEdit_cursor_pos - 1):
                    assert charsRemoved == 1
                    # Try to move the cursor back
                    self.ignore_next = False
                    self.on_plainTextEdit_cursorPositionChanged(0, 0, position)
                    self.ignore_next = True
                    # Signal an error if we can't
                    if self.plainTextEdit.isReadOnly():
                        print 'Oops -- cannot find changed text!'
                        self.plainTextEdit.undo()
                        return
                    # Then delete the char
                    self.textEdit.textCursor().deleteChar()
            self.textEdit.textCursor().insertText(self.plainTextEdit.text()[position:position + charsAdded])
            self.ignore_next = False
        
    def update_html(self):
        # Restore current dir
        os.chdir(self.current_dir)
        # Only translate from code to rest if we should
        if self.language_specific_options.comment_string is not None:
            CodeToRest(self.source_file, self.rst_file, self.language_specific_options)
        sphinx.cmdline.main( ('', '-b', 'html', '-d', '_build/doctrees', '-q', 
                              '.', '_build/html') )
        # Load in the updated html
        with codecs.open(self.html_file, 'r+', encoding = 'utf-8') as f:
            str = f.read()
            # Clean up code from any code to reST goo
            str = re.sub('<span class="c1?">.?.?\s*' + LanguageSpecificOptions.unique_remove_str + '</span>', '', str, re.MULTILINE)
            str = re.sub('<p>.?.?\s*' + LanguageSpecificOptions.unique_remove_str + '</p>', '', str, re.MULTILINE)
            f.seek(0)
            f.write(str)
            f.truncate()
        # Temporarily change to the HTML directory to load html, so Qt can access all
        # the HTML resources (style sheets, images, etc.)
        os.chdir('_build/html')
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
        
    def on_plainTextEdit_cursorPositionChanged(self, line, index, cursor_pos = -1):
        self.plainTextEdit_cursor_pos = self.plainTextEdit.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS)
#        print "Plain cursor pos now %d." % self.plainTextEdit_cursor_pos
        if not self.ignore_next:
            # A negative pos means use current position
            if cursor_pos < 0:
                cursor_pos = self.plainTextEdit_cursor_pos
            found = find_approx_text_in_target(unicode(self.plainTextEdit.text()),
                                               cursor_pos,
                                               unicode(self.textEdit.toPlainText()))
            if found >= 0:
                pos = self.textEdit.textCursor()
                # Is there a selection in the text pane?
                if (self.plainTextEdit.SendScintilla(QsciScintilla.SCI_GETANCHOR) ==
                    self.plainTextEdit_cursor_pos):
                    # There's no selection, so create a two-character selection around the cursor so that it's visible, because a cursor with no selection is hidden in widgets without focus.
                    pos.setPosition(found - 1,
                        QtGui.QTextCursor.MoveAnchor)
                    pos.setPosition(found + 1,
                        QtGui.QTextCursor.KeepAnchor)
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
        
    def on_textEdit_cursorPositionChanged(self, cursor_pos = -1):
        self.textEdit_cursor_pos = self.textEdit.textCursor().position()
        if not self.ignore_next:
            cursor = self.textEdit.textCursor()
            if cursor_pos < 0:
                cursor_pos = self.textEdit_cursor_pos
            found = find_approx_text_in_target(unicode(self.textEdit.toPlainText()),
                                               cursor_pos,
                                               unicode(self.plainTextEdit.text()))
            # Update position in source doc if text was found
            if found >= 0:
                self.ignore_next = True
                # Is there a selection in the HTML pane?
                if cursor.anchor() == cursor.position():
                    self.plainTextEdit.SendScintilla(QsciScintilla.SCI_SETCURRENTPOS, found - 1)
                    # There's no selection, so create a two-character selection around the cursor so that it's visible, because a cursor with no selection is hidden in widgets without focus.
                    self.plainTextEdit.SendScintilla(QsciScintilla.SCI_SETANCHOR, found + 1)
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
        # Split the source file into a path, base name, and extension
        head, tail = os.path.split(source_file)
        name, ext = os.path.splitext(tail)
        self.source_file = source_file
        self.rst_file = os.path.join(head, name) + '.rst'
        self.html_file = os.path.join('_build/html/', name) + '.html'
        # Choose a language
        self.language_specific_options = LanguageSpecificOptions()
        self.language_specific_options.set_language(get_lexer_for_filename(source_file))
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
        os.chdir(self.current_dir)
        with codecs.open(self.source_file, 'r', encoding = 'utf-8') as f:
            self.plainTextEdit.setText(f.read())
        self.update_html()
        self.plainTextEdit.setModified(False)
        
    # The decorator below prevents this method from being called twice, per
    # http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/new_style_signals_slots.html#connecting-slots-by-name
    @QtCore.pyqtSlot()
    def on_action_Reopen_triggered(self):
        self.reopen()
        
    @QtCore.pyqtSlot()
    def on_action_Open_triggered(self):
        # Restore current dir
        os.chdir(self.current_dir)
        source_file = QtGui.QFileDialog.getOpenFileName()
        if source_file:
            self.open(unicode(source_file))
               
    @QtCore.pyqtSlot()
    def on_action_Save_and_update_triggered(self):
        # Restore current dir
        os.chdir(self.current_dir)
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
#    window.open('README.rst')
#    window.open('CodeChat.py')
#    window.open('mptst_word.s')
    window.open('index.rst')
#    window.open('FindLongestMatchingString.py')
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
