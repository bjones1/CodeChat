# To do:
# - Allow selections, not just cursor movement
# - Figure out how to make cursor visible when html is changed to read-only
# - Unit testing
# - Figure out why searches initially don't work
# - Get agrepy working with Unicode, use Unicode throughout
# - Figure out how to get symbolic names for Qt::TextInteractionFlags
# - Verify that agrep-found string cursor index is accurate
# - Backsapce in HTML causes wrong char in plain text to be deleted
# - What to do when a backspace in HTML deletes context not in the plain text?
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
        
    def on_textEdit_contentsChange(self, position, charsRemoved, charsAdded):
        if not self.ignore_next:
            print 'HTML position %d change: %d chars removed, %d chars added.' % (position, charsRemoved, charsAdded)
            self.ignore_next = True
            for i in range(charsRemoved):
                self.plainTextEdit.textCursor().deleteChar()
            self.plainTextEdit.textCursor().insertText(self.textEdit.toPlainText()[position:position + charsAdded])
            self.ignore_next = False
        
    def on_plainTextEdit_contentsChange(self, position, charsRemoved, charsAdded):
        if (not self.ignore_next) and (not self.textEdit.isReadOnly()):
            print 'Plain position %d change: %d chars removed, %d chars added.' % (position, charsRemoved, charsAdded)
            self.ignore_next = True
            for i in range(charsRemoved):
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
        
    def on_plainTextEdit_cursorPositionChanged(self):
        if not self.ignore_next:
            pos = self.plainTextEdit.textCursor().position()
            source_text = str(self.plainTextEdit.toPlainText())
            search_loc = (pos, max(0, pos - 5), min(len(source_text), pos + 5))
            found = find_approx_text_in_target(source_text,
                                               search_loc,
                                               str(self.textEdit.toPlainText()))
            text = source_text[search_loc[1]:search_loc[2]]
            if found >= 0:
                pos = self.textEdit.textCursor()
                pos.setPosition(found) #, QtGui.QTextCursor.KeepAnchor)
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
        
    def on_textEdit_cursorPositionChanged(self):
        if not self.ignore_next:
            cursor = self.textEdit.textCursor()
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
                search_loc = (cursor.position(), current_fragment.position(), 
                              current_fragment.position() + len(text))
                found = find_approx_text_in_target(str(self.textEdit.toPlainText()),
                                                   search_loc,
                                                   str(self.plainTextEdit.toPlainText()))
                # Because the find operation looks forward from the current location,
                # move to the beginning of the document.
                # To do: set the highlight based on indexes from Python, to work
                # around the a0 space thing.
                if found >= 0:
                    pos = self.plainTextEdit.textCursor()
                    pos.setPosition(found) #, QtGui.QTextCursor.KeepAnchor)
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
def find_approx_text_in_target(search_text, search_loc, target_text):
    (loc, start_loc, end_loc) = search_loc
    assert start_loc <= end_loc
    search_str = search_text[start_loc:end_loc]
    # A zero-length string can't be matched.
    if start_loc == end_loc: return -1
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
    # Return success only when there's exactly one match
    if (match is None) or (len(match) > 1):
        return -1
    else:
        # match[0][0] contains the index of the entire search string.
        # offset from that to pinpoint where in this string we want.
        # BUG: if there's not an exact match, this may go to the wrong
        # char!
        return match[0][0] + loc - start_loc


if __name__ == '__main__':
    # Instantiate the app and GUI then run them
    app = QtGui.QApplication(sys.argv)
    form = MyWidget(None)
    form.show()
    app.exec_()
