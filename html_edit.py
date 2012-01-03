# To do:
#
# * Figure out how to get the SCN_MODIFIED signal to connect, rewrite the
#   on_plainTextEdit_modified routine
# * Unit testing


from PyQt4 import QtGui, QtCore, uic
import sphinx.cmdline
import sys, os
# Found some docs on QScintilla on Python with Qt at
# http://eli.thegreenplace.net/2011/04/01/sample-using-qscintilla-with-pyqt/
from PyQt4.Qsci import QsciScintilla, QsciLexerCPP, QsciLexerPython
import codecs
from pygments.lexers.compiled import CLexer, CppLexer
from pygments.lexers.agile import PythonLexer

from FindLongestMatchingString import find_approx_text_in_target

# A unique string to mark lines for removal in HTML
unique_remove_str = 'wokifvzohtdlm'

# A tuple of language-specific options, indexed by the parser which Pygments
# selects.
language_specific_options = {
 CLexer      : ('// ', '// ' + unique_remove_str,       QsciLexerCPP),
 CppLexer    : ('// ', '// ' + unique_remove_str,       QsciLexerCPP),
 PythonLexer : ('# ' , 'if ' + unique_remove_str + ':', QsciLexerPython)
}

language = PythonLexer

# The string indicating a comment in the chosen programming language. This must
# end in a space for the regular expression in format to work. The space
# also makes the output a bit prettier.
comment_string = language_specific_options[language][0]

form_class, base_class = uic.loadUiType("html_edit.ui")
class MyQMainWindow(QtGui.QMainWindow, form_class):
    def __init__(self, source_file):
        self.ignore_next = True
        QtGui.QMainWindow.__init__(self)
        # Split the source file into a path, base name, and extension
        head, tail = os.path.split(source_file)
        name, ext = os.path.splitext(tail)
        self.source_file = source_file
        self.rst_file = os.path.join(head, name) + '.rst'
        self.html_file = os.path.join('_build/html/', name) + '.html'
        # Save current dir: HTML loading requires a change to the HTML direcotry,
        # while Sphinx needs current dir.
        self.current_dir = os.getcwd()
        self.setupUi(self)
        # Configure QScintilla
        # --------------------
        # Set the default font
        font = QtGui.QFont()
        font.setFamily('Courier New')
        font.setFixedPitch(True)
        font.setPointSize(10)        
        # Margin 0 is used for line numbers
        fontmetrics = QtGui.QFontMetrics(font)
        self.plainTextEdit.setMarginsFont(font)
        self.plainTextEdit.setMarginWidth(0, fontmetrics.width("00000") + 6)
        self.plainTextEdit.setMarginLineNumbers(0, True)
        self.plainTextEdit.setMarginsBackgroundColor(QtGui.QColor("#cccccc"))
        # Brace matching: enable for a brace immediately before or after
        # the current position
        self.plainTextEdit.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        # Use the C++ lexer.
        # Set style for comments to a fixed-width courier font.
        lexer = language_specific_options[language][2]()
        lexer.setDefaultFont(font)
        self.plainTextEdit.setLexer(lexer)
        self.plainTextEdit.SendScintilla(QsciScintilla.SCI_STYLESETFONT, QsciLexerCPP.Comment, 'Courier New')
        self.plainTextEdit.SendScintilla(QsciScintilla.SCI_STYLESETFONT, QsciLexerCPP.CommentLine, 'Courier New')
        self.plainTextEdit.SendScintilla(QsciScintilla.SCI_STYLESETFONT, QsciLexerCPP.CommentDoc, 'Courier New')
        
        with codecs.open(self.source_file, 'r', encoding = 'utf-8') as f:
            self.plainTextEdit.setText(f.read())
        self.update_html()
        # Ask for notification when the contents of either editor change
        self.textEdit.document().contentsChange.connect(self.on_textEdit_contentsChange)
        # Fails, but I don't know why.
#        self.plainTextEdit.SCN_MODIFIED.connect(self.on_plainTextEdit_modified)
        # This works fine, so the bug doesn't seem to be in the way I'm connecting.
        self.plainTextEdit.SCEN_CHANGE.connect(self.on_plainTextEdit_modified)
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
            print 'HTML position %d change: %d chars removed, %d chars added.' % (position, charsRemoved, charsAdded)
            self.ignore_next = True
            # If there are deletions, find out where in the plain text document
            # we must delete from
            if charsRemoved > 0:
                # A range - delete the entire range
                plainText_cursor = self.plainTextEdit.textCursor()
                if plainText_cursor.anchor() != plainText_cursor.position():
                    self.plainTextEdit.textCursor().removeSelectedText()
                # The delete key - just delete from the current position
                elif position == self.textEdit_cursor_pos:
                    assert charsRemoved == 1
                    self.plainTextEdit.textCursor().deleteChar()
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
                    self.plainTextEdit.textCursor().deleteChar()
            self.plainTextEdit.textCursor().insertText(self.textEdit.toPlainText()[position:position + charsAdded])
            self.ignore_next = False
        
    def on_plainTextEdit_modified(self):
        position, charsRemoved, charsAdded = (0, 0, 0)
        # Bug: broken for now.
        return
        if (not self.ignore_next) and (not self.textEdit.isReadOnly()):
            print 'Plain position %d change: %d chars removed, %d chars added.' % (position, charsRemoved, charsAdded)
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
        CodeToRest(self.source_file, self.rst_file)
        sphinx.cmdline.main( ('', '-b', 'html', '-d', '_build/doctrees', '-q', 
                              '.', '_build/html') )
        # Clean up code by removing deletion tags
        with codecs.open(self.html_file, 'r+', encoding = 'utf-8') as f:
            str = f.read()
            unique_remove_comment = language_specific_options[language][1]
            str = str.replace('<span class="c1">' + unique_remove_comment + '</span>', '') \
                     .replace('<span class="k">if</span> <span class="n">wokifvzohtdlm</span><span class="p">:</span>', '') \
                     .replace('<p>' + unique_remove_comment + '</p>', '')
            f.seek(0)
            f.write(str)
            f.truncate()
        # Temporarily change to the HTML directory to load html, so Qt can access all
        # the HTML resources (style sheets, images, etc.)
        os.chdir('_build/html')
        self.textEdit.setHtml(str)
    
    def set_html_editable(self, can_edit):
        # Calling self.textEdit.setReadOnly(False) disables
        # keyboard navigation. Use this to retain key nav.
        old_flags = int(self.textEdit.textInteractionFlags())
        new_flags = old_flags | QtCore.Qt.TextEditable if can_edit else old_flags & ~QtCore.Qt.TextEditable
        self.textEdit.pyqtConfigure(textInteractionFlags = new_flags)
        # BUG: the cursor is hidden when this is made uneditable. I'm not
        # sure how to show it. The line below doesn't help.
#        self.textEdit.setTextCursor(self.textEdit.textCursor())
        # This causes a infinite loop.
#        self.textEdit.moveCursor(QtGui.QTextCursor.NoMove)
        
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
                # Grow the selection if necessary; otherwise, just move the cursor.
                pos.setPosition(found,
                                QtGui.QTextCursor.MoveAnchor 
                                if self.plainTextEdit.SendScintilla(QsciScintilla.SCI_GETANCHOR) == self.plainTextEdit_cursor_pos
                                else QtGui.QTextCursor.KeepAnchor)
                self.ignore_next = True
                self.textEdit.setTextCursor(pos)
                self.set_html_editable(True)
                self.ignore_next = False
            else:
                self.ignore_next = True
                self.set_html_editable(False)
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
                # Grow the selection if necessary; otherwise, just move the cursor.
                # Note: I tried to use SCI_SETEMPTYSELECTION per
                # http://www.scintilla.org/ScintillaDoc.html#SCI_SETEMPTYSELECTION,
                # but got AttributeError: type object 'QsciScintilla' has
                # no attribute 'SCI_SETEMPTYSELECTION'.
                self.plainTextEdit.SendScintilla(QsciScintilla.SCI_SETCURRENTPOS, found)
                if cursor.anchor() == cursor.position():
                    self.plainTextEdit.SendScintilla(QsciScintilla.SCI_SETANCHOR, found)
                # Scroll cursor into view
                self.plainTextEdit.SendScintilla(QsciScintilla.SCI_SCROLLCARET)
                self.ignore_next = True
                self.set_html_editable(True)
                self.ignore_next = False
            else:
                self.ignore_next = True
                self.set_html_editable(False)
                self.ignore_next = False
                
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




from pygments.formatter import Formatter
from pygments.token import Token
import re

# This class converts from source to to reST. As the <a>overview</a>
# states, this uses Pygments to do most of the work, adding only a formatter
# to that library. Therefore, to use this class, simply select this class
# as the formatter for Pygments (see an example 
# <a href="#def_CodeToHtml">below</a>).
class CodeToRestFormatter(Formatter):
    # Pygments <a href="http://pygments.org/docs/formatters/#formatter-classes">calls this routine</a> (see the HtmlFormatter) to transform tokens to first-pass formatted lines. We need a two-pass process: first, merge comments; second, transform tokens to lines. This wrapper creates that pipeline, yielding its results as a generator must. It also wraps each line in a &lt;pre&gt; tag.<br />
    def format_unencoded(self, token_source, out_file):
        nl_token_source = self._expand_nl(token_source)
        self._format_body(nl_token_source, out_file)

    def _expand_nl(self, token_source):
        # Break any comments ending in a newline into two separate tokens
        for ttype, value in token_source:
            if (ttype == Token.Comment.Single) and value.endswith('\n'):
                yield ttype, value[:-1]
                yield Token.Text, u'\n'
            else:
                yield ttype, value

    def _format_body(self, token_source, out_file):  
        # Store up a series of string which will compose the current line
        current_line_list = []
        # Keep track of the type of the last line.
        last_is_code = False
        # Determine the type of the current line
        is_code, is_comment, is_ws = range(3)
        line_type = is_comment
        # Keep track of the indentation of comment
        comment_indent = ''
        # A regular expression for whitespace not containing a newline
        ws = re.compile(r'^[ \t\r\f\v]+$')
        # A regular expression to remove comment chars
        regexp = re.compile(r'(^[ \t]*)' + comment_string + '?', re.MULTILINE)
        # A comment which can be removed later, used to trick reST / Sphinx into
        # generating the correct indention        
        unique_remove_comment = language_specific_options[language][1]

        # Iterate through all tokens in the input file        
        for ttype, value in token_source:
            # Check for whitespace
            if re.search(ws, value):
                # If so, add it to the stack of tokens on this line
                current_line_list.append(value)
            # Check for a comment
            elif (ttype is Token.Comment) or (ttype is Token.Comment.Single):
                if line_type != is_code:
                    line_type = is_comment
                # If so, add it to the stack of tokens on this line
                current_line_list.append(value)
            # On a newline, process the line
            elif value == '\n':
                # Convert to a string
                line_str = ''.join(current_line_list)
                current_line_list = [line_str]
                # If the line is whitespace, inherit the type of the previous
                # line.
                if line_type == is_ws:
                    line_type = is_code if last_is_code else is_comment
                if line_type == is_code:
                    # Each line of code needs a space at the beginning
                    current_line_list.insert(0, ' ')
                    if not last_is_code:
                        # When transitioning from comment to code, prepend a ::
                        # to the last line.
                        # Hack: put a . at the beginning of the line so reST
                        # will preserve all indentation of the block.
                        current_line_list.insert(0, '\n\n::\n\n ' + unique_remove_comment + '\n')
                    else:
                        # Otherwise, just prepend a newline
                        current_line_list.insert(0, '\n')
                else:
                    # Save the number of spaces in this comment
                    match = re.search(regexp, line_str)
                    if match:
                        comment_indent = match.group(1)
                    # Remove the comment character (and one space, if it's there)
                    current_line_list = [re.sub(regexp, r'\1', line_str)]
                    # Prepend a newline
                    current_line_list.insert(0, '\n')
                    # Add in left margin adjustments for a code to comment transition
                    if last_is_code:
                        # Get left margin correct by inserting a series of blockquotes
                        blockquote_indent = []
                        for i in range(len(comment_indent)):
                            blockquote_indent.append('\n\n' + ' '*i + unique_remove_comment)
                        blockquote_indent.append('\n\n')
                        current_line_list.insert(0, ''.join(blockquote_indent))
                    
                # Convert to a string
                line_str = ''.join(current_line_list)
                current_line_list = []
                # For debug:
                # line_str += str(line_type) + str(last_is_code)
                # We're done!
                out_file.write(line_str)
                last_is_code = line_type == is_code
                line_type = is_ws
            # Not a newline, whitespace, or comment char: must be code.
            else:
                line_type = is_code
                current_line_list.append(value)


from pygments.lexers import get_lexer_for_filename
from pygments import highlight

# <a name="CodeToHtml"></a>Use Pygments with the CodeToHtmlFormatter to translate a source file to an HTML file.
def CodeToRest(source_path, rst_path):
    code = codecs.open(source_path, 'r', encoding = 'utf-8').read()
    formatter = CodeToRestFormatter()
    outfile = codecs.open(rst_path, mode = 'w', encoding = 'utf-8')
    lexer = get_lexer_for_filename(source_path)
    hi_code = highlight(code, lexer, formatter)
    outfile.write(hi_code)
    
if __name__ == '__main__':
    # Instantiate the app and GUI then run them
    app = QtGui.QApplication(sys.argv)
    window = MyQMainWindow('FindLongestMatchingString.py')
    window.setWindowState(QtCore.Qt.WindowMaximized)
    window.show()
    sys.exit(app.exec_())
