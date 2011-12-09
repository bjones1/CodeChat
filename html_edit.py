# To do:
# - Backspace when at the left edge of a found block removes the wrong char
#   in the other pane
# - Make search more robust
# - Figure out how to make cursor visible when html is changed to read-only
# - Unit testing
# - Get agrepy working with Unicode, use Unicode throughout
# - Figure out how to get symbolic names for Qt::TextInteractionFlags
# - The obvious: translate code to reST, add GUI


from PyQt4 import QtGui, uic
#from docutils.core import publish_string
import sphinx.cmdline
import sys
import os
import agrepy

form_class, base_class = uic.loadUiType("html_edit.ui")

class MyWidget (QtGui.QWidget, form_class):
    def __init__(self, parent = None, selected = [], flag = 0, *args):
        self.ignore_next = True
        QtGui.QWidget.__init__(self, parent, *args)
        self.setupUi(self)
        self.updatePushButton.setShortcut(QtGui.QKeySequence('Ctrl+u'))
#        self.plainTextEdit.setPlainText(rest_text)
#        str = publish_string(rest_text, writer_name='html')
        with open('index.rst', 'r') as f:
            self.plainTextEdit.setPlainText(f.read())
        self.update_html()
        # Ask for notification when the contents of either editor change
        self.textEdit.document().contentsChange.connect(self.on_textEdit_contentsChange)
        self.plainTextEdit.document().contentsChange.connect(self.on_plainTextEdit_contentsChange)
        self.ignore_next = False
        self.textEdit_cursor_pos = self.textEdit.textCursor().position()
        self.plainTextEdit_cursor_pos = self.plainTextEdit.textCursor().position()
        
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
        
    def on_plainTextEdit_contentsChange(self, position, charsRemoved, charsAdded):
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
                    self.on_plainTextEdit_cursorPositionChanged(position)
                    self.ignore_next = True
                    # Signal an error if we can't
                    if self.plainTextEdit.isReadOnly():
                        print 'Oops -- cannot find changed text!'
                        self.plainTextEdit.undo()
                        return
                    # Then delete the char
                    self.textEdit.textCursor().deleteChar()
            self.textEdit.textCursor().insertText(self.plainTextEdit.toPlainText()[position:position + charsAdded])
            self.ignore_next = False
        
    def update_html(self):
        sphinx.cmdline.main( ('', '-b', 'html', '-d', '_build/doctrees', '-q', '.', '_build/html') )
        str = ''
        with open('_build/html/index.html', 'r') as f:
            str = f.read()
        # Temporarily change to the HTML directory to load html, so Qt can access all
        # the HTML resources (style sheets, images, etc.)
        cur = os.getcwd()
        os.chdir('_build/html')
        self.textEdit.setHtml(str)
        os.chdir(cur)
    
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
        
    def on_plainTextEdit_cursorPositionChanged(self, cursor_pos = -1):
        self.plainTextEdit_cursor_pos = self.plainTextEdit.textCursor().position()
#        print "Plain cursor pos now %d." % self.plainTextEdit_cursor_pos
        if not self.ignore_next:
            # A negative pos means use current position
            cursor = self.plainTextEdit.textCursor()
            if cursor_pos < 0:
                cursor_pos = cursor.position()
            source_text = str(self.plainTextEdit.toPlainText())
            search_loc = (cursor_pos, max(0, cursor_pos - 5), min(len(source_text), cursor_pos + 5))
            found = find_approx_text_in_target(source_text,
                                               search_loc,
                                               str(self.textEdit.toPlainText()))
            text = source_text[search_loc[1]:search_loc[2]]
            if found >= 0:
                pos = self.textEdit.textCursor()
                # Grow the selection if necessary; otherwise, just move the cursor.
                pos.setPosition(found,
                                QtGui.QTextCursor.MoveAnchor 
                                if cursor.anchor() == cursor.position()
                                else QtGui.QTextCursor.KeepAnchor)
                print ('Plain fragment "%s" (%d, %d, %d) found at %d.' % 
                      (text, search_loc[0], search_loc[1], search_loc[2], found))
                self.ignore_next = True
                self.textEdit.setTextCursor(pos)
                self.set_html_editable(True)
                self.ignore_next = False
            else:
                print 'Fragment "%s" not found.' % text
                self.ignore_next = True
                self.set_html_editable(False)
                self.ignore_next = False
        
    def on_textEdit_cursorPositionChanged(self, cursor_pos = -1):
        self.textEdit_cursor_pos = self.textEdit.textCursor().position()
        if not self.ignore_next:
            cursor = self.textEdit.textCursor()
            if cursor_pos < 0:
                cursor_pos = cursor.position()
#            print "Cursor position %d, block %d" % (cursor.position(),
#                                                    cursor.blockNumber())
            # Search for the current fragment in the block.
            block = cursor.block()
            iterator = block.begin()
            current_fragment = None
            while not iterator.atEnd():
                current_fragment = iterator.fragment()
                if current_fragment.contains(cursor.position()):
                    break
                iterator += 1
            # When the cursor is at the end of a line, it's not in any fragment.
            # In that case, use the last fragment instead.
            if current_fragment is not None:
                text = current_fragment.text()
                search_loc = (cursor_pos, current_fragment.position(), 
                              current_fragment.position() + len(text))
                found = find_approx_text_in_target(str(self.textEdit.toPlainText()),
                                                   search_loc,
                                                   str(self.plainTextEdit.toPlainText()))
                # Update position in source doc if text was found
                if found >= 0:
                    pos = self.plainTextEdit.textCursor()
                    # Grow the selection if necessary; otherwise, just move the cursor.
                    pos.setPosition(found,
                                    QtGui.QTextCursor.MoveAnchor 
                                    if cursor.anchor() == cursor.position()
                                    else QtGui.QTextCursor.KeepAnchor)
                    self.ignore_next = True
                    self.plainTextEdit.setTextCursor(pos)
                    self.set_html_editable(True)
                    self.ignore_next = False
                    print ('HTML fragment "%s" (%d, %d, %d) found at %d.' % 
                        (text, search_loc[0], search_loc[1], search_loc[2], found))
                else:
                    print 'Fragment "%s" not found.' % text
                    self.ignore_next = True
                    self.set_html_editable(False)
                    self.ignore_next = False
                
    def on_updatePushButton_pressed(self):
        if self.plainTextEdit.document().isModified():
            with open('index.rst', 'w') as f:
                f.write(unicode(self.plainTextEdit.toPlainText()))
            self.ignore_next = True
            self.update_html()
            self.ignore_next = False
            # Resync panes. But causes a crash sometimes!
            self.on_plainTextEdit_cursorPositionChanged()

            
# Given a location in the text of one document (the source), finds the corresponding
# location in a target document.
#   search_text - The text composing the entire source document in which the search
#                 string resides
#   search_loc - A tuple of (loc, start_loc, end_loc) giving the desired
#                location in the source document, followed by a range of text
#                that is probably easy to match which contains loc.
#   target_text - The target document
#   returns - A location in the target document, or -1 if not found
#
#   Bugs: Sometimes spaces get replaced by \u00a0, a no-break space.
def find_approx_text_in_target(search_text, search_loc, target_text, mismatches = -1):
    (loc, start_loc, end_loc) = search_loc
    assert start_loc <= end_loc
    search_str = search_text[start_loc:end_loc]
    # A zero-length string can't be matched.
    if start_loc == end_loc: return -1
    if mismatches < 1:
        # Note: going too high on the last value (allowed number of mimatches) 
        # with (I think) a short search string makes this take forever to run.
        # So, pick a number between 1 and 8, such at at least 1/5th of the chars
        # match.
        mismatches = max(1, min(8, len(search_str)/5))
#    print "Searching for %s..." % search_str
    pat = agrepy.compile(search_str, len(search_str), mismatches)
#    print "pattern compiled...",
    match = agrepy.agrepy(search_str, len(search_str), target_text, 
                          len(target_text), True, pat)
    # Fail on no matches
    if match is None:
        return -1
    elif len(match) > 1:
        # On multiple matches with mismatch > 1, try reducing the mismatch
        # to see if we can get a single match. Otherwise, fail.
        return -1 if mismatches < 2 else \
            find_approx_text_in_target(search_text, search_loc, target_text, mismatches - 1)
    else:
        # match[0][0] contains the the index into the target string of the
        # first matched char
        pos_in_target = match[0][0]
        match_len = loc - start_loc
        # Given that we did an approximate match, make sure the needed
        # prefix of the string is an exact match.
        if (target_text[pos_in_target:pos_in_target + match_len] ==
            search_str[0:match_len]):
            # offset from that to pinpoint where in this string we want.
            return pos_in_target + match_len
        else:
            return -1


if __name__ == '__main__':
    # Instantiate the app and GUI then run them
    app = QtGui.QApplication(sys.argv)
    form = MyWidget(None)
    form.show()
    app.exec_()
