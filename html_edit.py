# To do:
#
# * Bug in the Pygments parser boogers us #macros. How to fix?
# * Figure out how to get the SCN_MODIFIED signal to connect, rewrite the
#   on_plainTextEdit_modified routine
# * Backspace when at the left edge of a found block removes the wrong char
#   in the other pane
# * Make search more robust
# * Figure out how to make cursor visible when html is changed to read-only
# * Unit testing
# * Figure out how to get symbolic names for Qt::TextInteractionFlags
# * The obvious: add GUI, test lots and lots


from PyQt4 import QtGui, uic
import sphinx.cmdline
import sys, os
# For approximate pattern matching, use the Python port of TRE. See
# http://hackerboss.com/approximate-regex-matching-in-python/ for more details.
# I modified the Python wrapper code to allow Unicode strings.
import tre
# Found some docs on QScintilla on Python with Qt at
# http://eli.thegreenplace.net/2011/04/01/sample-using-qscintilla-with-pyqt/
from PyQt4.Qsci import QsciScintilla, QsciLexerCPP
import codecs

# A unique string to mark lines for removal in HTML
unique_remove_str = '//wokifvzohtdlm'

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
        lexer = QsciLexerCPP()
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
            str = str.replace('<span class="c1">' + unique_remove_str + '</span>', '')\
                .replace('<p>' + unique_remove_str + '</p>', '')
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
        # Note: I don't know a Python name for
        # Qt::TextInteractionFlags. Use the values from
        # http://doc.qt.nokia.com/latest/qt.html#TextInteractionFlag-enum
        # instead.
        old_flags = int(self.textEdit.textInteractionFlags())
        new_flags = old_flags | 16 if can_edit else old_flags & ~16
        self.textEdit.pyqtConfigure(textInteractionFlags=new_flags)
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


# Search for a string
def find_approx_text(search_text, target_text, cost = None):
    print("Searching for '%s'" % search_text)
    # tre.LITERAL specifies that search_str is a literal search string, not
    # a regex.
    pat = tre.compile(search_text, tre.LITERAL)
    fz = tre.Fuzzyness(maxerr = cost) if cost else tre.Fuzzyness()
    match = pat.search(target_text, fz)
    # match.group()[0][0] contains the the index into the target string of the
    # first matched char
    begin_in_target, end_in_target = match.groups()[0]
    print("found '" + target_text[begin_in_target:end_in_target] + "'")
    
    # TRE picks the first match it finds, even if there is
    # more than one matck with identical error. So,
    # manually call it again with a substring to check.
    match_again = pat.search(target_text[end_in_target:], fz)
    if match_again and (match_again.cost <= match.cost):
        print('Multiple matches ' + str(match_again.groups()))
        return None, 0, 0
    else:
        return match, begin_in_target, end_in_target
            
# Given a location in the text of one document (the source), finds the corresponding
# location in a target document.
#   search_text - The text composing the entire source document in which the search
#                 string resides
#   search_loc - A location in the source document which should be found in the
#                target document
#   target_text - The target document
#   search_range - Range of characters about the search_loc in which to search.
#   returns - A location in the target document, or -1 if not found
#
#   Bugs: Sometimes spaces get replaced by \u00a0, a no-break space.
def find_approx_text_in_target(search_text, search_loc, target_text):
    search_range = 40
    # Choose a +/- search_range of chars to search in.
    begin = max(0, search_loc - search_range)
    end = min(len(search_text), search_loc + search_range)
    match, begin_in_target, end_in_target = find_approx_text(search_text[begin:end], target_text)
    # Shrink the string being matched until we get an exact match, run
    # out of chars, get a multiple match, or have no match
    while (match and search_range and match.cost > 0):        
        # Search by removing chars from left side of search string
        left_begin = begin + (search_loc - begin)/2
        if left_begin > begin:
            left_match, left_begin_in_target, left_end_in_target = \
              find_approx_text(search_text[left_begin:end], target_text, match.cost)
        else:
            left_match = None
            
        # Search by removing chars from right side of search string
        right_end = search_loc + (end - search_loc)/2
        if right_end < end:
            right_match, right_begin_in_target, right_end_in_target = \
              find_approx_text(search_text[begin:right_end], target_text, match.cost)
        else:
            right_match = None
            
        # Choose the best
        if left_match:
            if right_match and right_match.cost < left_match.cost:
                match, begin_in_target, end_in_target = \
                  right_match, right_begin_in_target, right_end_in_target
                end = right_end
            else:
                match, begin_in_target, end_in_target = \
                  left_match, left_begin_in_target, left_end_in_target
                begin = left_begin
        else:
            match, begin_in_target, end_in_target = \
              right_match, right_begin_in_target, right_end_in_target
            end = right_end
            
    # Fail on no matches
    if not match:
        print('No matches.\n')
        return -1
    # A zero-cost match is an exact match
    if (match.cost == 0):
        # offset from that to pinpoint where in this string we want.
        match_len = search_loc - begin
        print('succeeded.\n')
        return begin_in_target + match_len



from pygments.formatter import Formatter
from pygments.token import Token
import re

# The string indicating a comment in the chosen programming language. This must
# end in a space for the regular expression in format to work. The space
# also makes the output a bit prettier.
# comment_string = '# '
comment_string = '// '

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
                        current_line_list.insert(0, '\n\n::\n\n ' + unique_remove_str + '\n')
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
                            blockquote_indent.append('\n\n' + ' '*i + unique_remove_str)
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
    window = MyQMainWindow('./practicum2Summer2011.c')
    window.show()
    sys.exit(app.exec_())
