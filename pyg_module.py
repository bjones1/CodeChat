# -*- coding: utf-8 -*-<br />
# <h1>Implementation</h1>
# 
# The program consists of two separate portions (code to HTML and HTML
# to code) with a bit of glue code, supplemented with tests.
# 
# <h2><a name="Code_to_HTML"></a>Code to HTML</h2>
# 
# The code to HTML link consists of modifications to
# <a href="http://pygments.org/">Pygments</a>, a wonderful source
# hilighter. Pygments already provides a lexer to break the input code into
# tokens and an HTML formatter to transform those tokens to HTML, based upon a
# variety of styles. These modification therefore change a bit of functionality
# in the HTML formatter. In particular:
# <ol><li>Comments are indented and typeset in a proportional font in 
#         <a href="#typeset_comments_in_a_proportional_font">_create_stylesheet</a>.</li>
#     <li>Multi-line comments are <a>merged</a> in
#         <a href="#merge_comments">_merge_comments</a>.</li>
#     <li><a href="#_format_lines1">_format_lines1</a> carries out special
#          processing for comments. In particular, comments are assumed to
#          contain HTML, so that <a>no escaping</a> is done on them. In
#          addition, comment #, //, or /* characters are automatically
#          removed during translation to preserve the visual appearance of
#          the document.</li>
#      <li>Each line is wrapped in a &lt;pre&gt; tag in
#          <a href="#_format_lines">_format_lines</a>, after being passed
#          through the formatting pipeline in the two preceeding
#          steps.</li></ol>
from pygments.formatters import HtmlFormatter
from pygments.formatters.html import _escape_html_table
from pygments.token import Token, Text, Comment
import pygments.token
import re

# Put all text (whitespace, newlines) in a span
pygments.token.STANDARD_TYPES[Text] = 't'
# Keep all comments out of a span when empty (easier editing); use the value 'c' to put comment in a span (typesets nicely)
pygments.token.STANDARD_TYPES[Comment] = ''

# The string indicating a comment in the chosen programming language. This must
# end in a space for the regular expression in _format_lines1 to work. The space
# also makes the output a bit prettier.
comment_string = '# '
# comment_string = '// '


# File extension for the source file
source_extension = '.py'
# source_extension = '.cpp'


# This class converts from source to to HTML. As the <a>overview</a>
# states, this uses Pygments to do most of the work, adding only a formatter
# to that library. Therefore, to use this class, simply select this class
# as the formatter for Pygments (see an example 
# <a href="#def_CodeToHtml">below</a>).
class CodeToHtmlFormatter(HtmlFormatter):
    # <a name="typeset_comments_in_a_proportional_font"></a><h3>Typeset comments</h3>
    # The first element of the class introduces a proportional font to the formatter. This sort of change really belongs in a <a href="http://pygments.org/docs/styles/">style</a>, but the current style <a href="http://pygments.org/docs/styles/#style-rules">framework</a> don't provide a way to specify this. Rather than introduce this change, I instead modified the way that the Pygments style was used by the formatter. Specifially, I copied the <code>_create_stylesheet</code>  routine verbatim from Pygments then added <a href="#insertedCode">code</a> to typeset comments in a proportional font. 
    def _create_stylesheet(self):
        t2c = self.ttype2class = {Token: ''}
        c2s = self.class2style = {}
        for ttype, ndef in self.style:
            name = self._get_css_class(ttype)
            style = ''
            # <a name="insertedCode"></a><b>BAJ modification</b>: typeset comments nicely. In particular:<br />
            # <ul><li>Because comments are embedded in &lt;pre&gt; text, the <a href="http://www.w3schools.com/cssref/pr_text_white-space.asp">white-space property</a> must be returned to normal to allow line wrapping, consuming of additional space, etc. One concern: now, whitespace in the code will no longer match whitespace in the HTML document.</li>
            # <li>On Chrome and SeaMonkey, the proportional 
            # font is much larger than its corresponding monospaced font used for the 
            # code. Using <code>font-size: small</code> helps. Specifying the font as a percentags 
            # is bad, because if the &lt;span&gt; tags get nested, all fonts in the 
            # nest get smaller!</li><li>By adding the <tt><a href="http://www.w3.org/TR/CSS2/visuren.html#display-prop">display</a>: inline-block</tt> attribute, the entire comment will be indented by whatever spaces preceed it. However, this either grows the right margin by the indent or causes the entire comment to fall on to the next line, making it hard to read. The addition of <code><span class="s">width: 5.5in</span></code> avoid this problem by limiting the max width of a comment. An ideal solution would be to dynamically set this so the width extends to the edge of the screen, but this would require JavaScript (I think).<br /></li>
            # <li> TODO: No multi-line comment support yet.</li></ul>
            if (ttype is Token.Comment) or (ttype is Token.Comment.Single):
                style += 'font-family: sans-serif; ' + \
                         'display: inline-block; width: 5.5in; '
            else:
                style += 'font-family: monospace; white-space: pre; font-size:large; '
	    # End of modification.
            if ndef['color']:
                style += 'color: #%s; ' % ndef['color']
            if ndef['bold']:
                style += 'font-weight: bold; '
            if ndef['italic']:
                style += 'font-style: italic; '
            if ndef['underline']:
                style += 'text-decoration: underline; '
            if ndef['bgcolor']:
                style += 'background-color: #%s; ' % ndef['bgcolor']
            if ndef['border']:
                style += 'border: 1px solid #%s; ' % ndef['border']
            if style:
                t2c[ttype] = name
                # save len(ttype) to enable ordering the styles by
                # hierarchy (necessary for CSS cascading rules!)
                c2s[name] = (style[:-2], ttype, len(ttype))

    # Pygments <a href="http://pygments.org/docs/formatters/#formatter-classes">calls this routine</a> (see the HtmlFormatter) to transform tokens to first-pass formatted lines. We need a two-pass process: first, merge comments; second, transform tokens to lines. This wrapper creates that pipeline, yielding its results as a generator must. It also wraps each line in a &lt;pre&gt; tag.<br />
    def _format_lines(self, token_source):
        nl_token_source = self._expand_nl(token_source)
        merged_token_source = self._merge_comments(nl_token_source)
        source = self._format_lines1(merged_token_source)
        return source
                
    def _expand_nl(self, token_source):
        # Break any comments ending in a newline into two separate tokens
        for ttype, value in token_source:
            if (ttype == Token.Comment.Single) and value.endswith('\n'):
                yield ttype, value[:-1]
                yield Token.Text, u'\n'
            else:
                yield ttype, value
                
    # <h3>Merge multi-line comments</h3>
    # This routine takes tokens as its input, combining multiple lines of
    # single-line comments separated only by a newline into a single comment
    # token. It's structured as a state machine, per the diagram below.
    # Essentially, the machine looks for a multiline comment, which consists
    # of: a newline, optional whitespace, a comment, newline, optional
    # whitespace, a comment. When this sequence is found such that the two whitespaces are identical, the two comments are combined with any intervening whitespace and the search continues. Additional comments:<br />
    # <ul><li>Transitions away from the sequence must be handled carefully (see the diagram). Each state may be presented with a comment, newline, whitespace, or any other token and must handle each possibility. To do this, <code>token_stack</code> contains a stack of tokens collected while walking through the state machines, which can be produced when the input varies from the multiline-comment path.<br /></li><li>"Whitespace" in this context does <b>not</b> include a newline. See the <code>ws</code> variable.<br /></li></ul><img src="state_machine.png" /><br />The state machine syntax: &lt;condition / action&gt;, so that nl / yield all tokens means that if a newline (\n character) is found, all tokens in token_stack will be yielded before moving to the next state. The additional abbreviation used: "ws" for whitespace (which does not include a newline).<br /><br />Note that the obvious alternative of doing this combining using a regular expression on the source text before tokenization doesn't work (I tried it). In particular, this removes all indications of where lines were broken earlier, making the comment a mess when going from the HTML back to code. It's possible that, with line wrapping implemented, this could be a much simpler and better approach.
    def _merge_comments(self, token_source):
        # Keep a history of tokens; if we can't combine then, then yield a
        # bunch of these.
        token_stack = []
        # A regular expression for whitespace not containing a newline
        ws = re.compile(r'^[ \t\r\f\v]+$')
        # The sequence (a state machine) needed to combine comments.<br />
        # 0 - at the beginning of a line, now waiting for whitespace (initial state)<br />
        # 1 - waiting for a comment
        # <br />2 - waiting for a newline
        # <br />3 - waiting for whitespace or a comment
        # <br />4 - waiting for a comment
        # <br />5 - waiting for a newline
        state = 0
        for ttype, value in token_source:
#            print state, ttype, '"%s"' % value, token_stack
            if state == 0:
                if re.search(ws, value):
                    token_stack.append([ttype, value])
                    state = 1
                elif ((ttype is Token.Comment) or 
                  (ttype is Token.Comment.Single)):
                    token_stack.append([ttype, value])
                    state = 2
                else:
                    # While the code sequence to yield all tokens is repeated frequently and hence an excellent candidate for a function, the requirement of a yield keeps it from being easily placed in a function. So, I've just used a copy and paste approach instead.
                    for t in token_stack:
                        yield t
                    token_stack = []
                    yield ttype, value
                    state = 0 if value == '\n' else 5
            elif state == 1:
                # Assume we will never receive two whitespace tokens back to back.
                assert(not re.search(ws, value))
                if ((ttype is Token.Comment) or 
                  (ttype is Token.Comment.Single)):
                    token_stack.append([ttype, value])
                    state = 2
                else:
                    for t in token_stack:
                        yield t
                    token_stack = []
                    yield ttype, value
                    state = 0 if value == '\n' else 5
            elif state == 2:
                # For now, assume we will never receive whitespace following a comment. TODO: this could happen in C: /*blah*/ whitespace
                assert(not re.search(ws, value))
                # For now, assume we will never receive two comment tokens back to back. TODO: this could happen in C, perhaps as a /*blah*//*blah*/.
                assert( (ttype is not Token.Comment) and
                  (ttype is not Token.Comment.Single) )
                if value == '\n':
                    token_stack.append([ttype, value])
                    state = 3
                else:
                    for t in token_stack:
                        yield t
                    token_stack = []
                    yield ttype, value
                    state = 5
            elif state == 3:
                if re.search(ws, value):
                    token_stack.append([ttype, value])
                    state = 4
                elif ((ttype is Token.Comment) or 
                  (ttype is Token.Comment.Single)):
                    # See if two comments can be combined. The second comment (in value) has no whitespace, so the first comment shouldn't either. In this case, the token_stack should have 2 elements: comment, newline. If it has 3 elements (ws, comment, newline), don't combine.
                    if len(token_stack) == 2:
                        token_stack[0][1] += '\n' + value
                        del token_stack[1]
                        state = 2
                    else:
                        assert(len(token_stack) == 3)
                        # Can't merge, so yield first comment
                        for i in range(3):
                            yield token_stack[0]
                            del token_stack[0]
                        # and save the second comment on the stack
                        token_stack.append([ttype, value])
                        state = 2
                else:
                    for t in token_stack:
                        yield t
                    token_stack = []
                    yield ttype, value                
                    state = 0 if value == '\n' else 5
            elif state == 4:
                # We should never receive whitespace following whitespace.
                assert(not re.search(ws, value))
                if ((ttype is Token.Comment) or 
                  (ttype is Token.Comment.Single)):
                    # See if two comments can be combined. The second comment has whitespace; the first comment must have the same anount of whitespace. In this case, token_stack should have 4 elemements: ws, comment, nl, ws.
                    if (len(token_stack) == 4 and 
                       (token_stack[0][1] == token_stack[3][1])):
                        token_stack[1][1] += '\n' + token_stack[3][1] + value
                        del token_stack[2]
                        del token_stack[2]
                        state = 2
                    else:
                        # Can't merge, so yield first comment
                        for i in range(len(token_stack) - 1):
                            yield token_stack[0]
                            del token_stack[0]
                        # and save the second comment on the stack
                        token_stack.append([ttype, value])
                        state = 2
                else:
                    for t in token_stack:
                        yield t
                    token_stack = []
                    yield ttype, value
                    state = 0 if value == '\n' else 5
            elif state == 5:
                yield ttype, value
                if value == '\n':
                    state = 0
            else:
                assert(False)
                
        # When out of tokens, pull any remaining from the stack
        for t in token_stack:
            yield t
        
    # <h3>Special processing for comments</h3>
    # Copied verbatim from Pygments' _format_lines, then modified to
    # not escape comments and remove inital comment chars
    def _format_lines1(self, tokensource):
        """
        Just format the tokens, without any wrapping tags.
        Yield individual lines.
        """
        # BAJ: regular expression to remove comment chars
        regexp = re.compile(r'(^[ \t]*)' + comment_string + '?', re.MULTILINE)        
        
        nocls = self.noclasses
        lsep = self.lineseparator
        # for &lt;span style=""&gt; lookup only
        getcls = self.ttype2class.get
        c2s = self.class2style
        escape_table = _escape_html_table
        escape_table[ord('\n')] = u'<br />\n'

        lspan = ''
        line = ''
        for ttype, value in tokensource:
            if nocls:
                cclass = getcls(ttype)
                while cclass is None:
                    ttype = ttype.parent
                    cclass = getcls(ttype)
                cspan = cclass and '<span style="%s">' % c2s[cclass][0] or ''
            else:
                cls = self._get_css_class(ttype)
                cspan = cls and '<span class="%s">' % cls or ''

            # <a name="no_escape"></a>BAJ: If this is a comment, assume we're already using HTML and
            # don't need to escape characters.
            if ((ttype is Token.Comment) or 
              (ttype is Token.Comment.Single)):
                # Remove the comment character (and one space, if it's there)
                value = re.sub(regexp, r'\1', value)
                # Don't split, since we merge multi-line comments
                parts = [value]
                # Kludge to get line numbers to be correct, though annoying.
                for i in range(value.count('\n')):
                    yield 0, ''
            else:
                parts = value.translate(escape_table).split('\n')

            # for all but the last line
            for part in parts[:-1]:
                if line:
                    if lspan != cspan:
                        line += (lspan and '</span>') + cspan + part + \
                                (cspan and '</span>') + lsep
                    else: # both are the same
                        line += part + (lspan and '</span>') + lsep
                    yield 1, line
                    line = ''
                elif part:
                    yield 1, cspan + part + (cspan and '</span>') + lsep
                else:
                    yield 1, lsep
            # for the last line
            if line and parts[-1]:
                if lspan != cspan:
                    line += (lspan and '</span>') + cspan + parts[-1]
                    lspan = cspan
                else:
                    line += parts[-1]
            elif parts[-1]:
                line = cspan + parts[-1]
                lspan = cspan
            # else we neither have to open a new span nor set lspan

        if line:
            yield 1, line + (lspan and '</span>') + lsep

    # By default, the html formatter wraps the code in a div and a pre.
    # Don't wrap it at all.
    def wrap(self, source, outfile):
        return source
        

# <br />
# <h2><a name="CodeToHtml_overview"></a>HTML to Code<br />
# </h2>
# 
# 
# 
# The HTML to code link relies on <a href="http://www.crummy.com/software/BeautifulSoup">Beautiful Soup</a>.
# Some simplifying assumptions about the structure of the HTML
# document:<br />
# <ul>
# <li>All code must be wrapped in a &lt;pre&gt;.<br />
# </li><li>All comments are wrapped in &lt;span class="c"&gt; or appear
# as body text. Comments contain HTML.<br />
# </li><li>On a line, all code must come first, optionally followed by a
# comment. Code may never follow a comment on a single line
# (C-style /* */ in a line.</li><li>All header information (everything not inside the &lt;body&gt;
# tag) is discarded, to be regenerated when code is translated
# back to HTML.<br />
# </li>
# </ul>
# 
# With this, body text is comment; &lt;pre&gt; begins discarding all
# tags and emits only text until a comment tag, which outputs its
# entire subtree as a comment (including any code-tagged text).
# Newlines can be echoed without modification whether in code or
# comment mode.<br />
# <h3>The implementation</h3>
# <ol>
# <li>The HTML document is parsed, then only the &lt;body&gt; tag
# contents <a>translated</a>.</li><li><a>All comments</a> (body text or
# anything in a &lt;span class="c"&gt; tag) are prepended with a
# comment character and output verbatim (no HTML unescaping)</li><li><a>All code</a> (everything in a
# &lt;pre&gt; tag from the beginning of the line to the first
# &lt;span class="c") tag) is stripped of HTML tags, HTML
# unescaped, then written.</li>
# </ol>
# Beautiful Soup v3.x version
from BeautifulSoup import BeautifulSoup, Tag, NavigableString
# Beautiful Soup v4.x version
# from bs4 import BeautifulSoup, Tag, NavigableString
# from bs4.builder import HTMLTreeBuilder

class HtmlToCodeTranslator(object):
    # Dumb enum. Might want to use the smart one at http://code.activestate.com/recipes/413486/ instead.
    class State: outsidePre, inPre, inComment = range(3)
    
    def __init__(self):
        self.State = HtmlToCodeTranslator.State
        self.indent = ''
        self.indent_re = re.compile(r'([ \t\r\f\v]*)$')
        self.at_newline = True
        
    # <a name="body_translate"></a>Parse then translate 
    # the body of the given HTML document. Uses a state machine, which really 
    # should be better documented, but here's what I have now.<br />
    # 
    # <ul>
    # <li>As a three-state machine: outsidePre (initial state), inPre,
    #     inComment.</li><ul><li>outsidePre state:</li><ul><li>If a string, "\n" -&gt; "\n# "</li><li>If a tag, check name: pre causes transition to inPre
    #     state, dump contents, transition back to outsidePre<br />
    # </li></ul><li>inPre state: output only text, skip all tags.</li><ul><li>If a string, dump raw text</li><li>If a tag, check name: comment tag causes transition to
    #     inComment state, insert #, dump contents, transition back<br />
    # </li></ul><li>inComment state: "\n" -&gt; "\n# " for string, recur on
    #   contents.</li><ul><li>If a string, "\n" -&gt; "\n# "</li><li>Dump contents</li></ul></ul>
    # </ul>
    def translate(self, HtmlString):
        soup = BeautifulSoup(HtmlString)
#        print soup

        # For the contents, enter the loop!
        L = [self.translateBody(c, self.State.outsidePre) for c in soup.body]
        return ''.join(L)

    # Translate a chunk of html
    def translateBody(self, soup, state):
#        print state, soup, ('"%s"' % self.indent), self.at_newline
        if isinstance(soup, NavigableString):
            if state == self.State.inPre:
                # Update indent -- empty unless this is a newline followed by spaces
                s = str(soup)
                m = re.search(self.indent_re, s)
                self.indent = m.group(1) if (m and self.at_newline) else ''
                s = unescape(s)
                self.at_newline = True if s.endswith('\n') else False
                # Translate entities in code (but not in comments)
                return s
                # BeautifulSoup 3.x does this, but it eats any leading whitespace. Ouch.<br />
                # return str(BeautifulSoup(s, convertEntities=BeautifulStoneSoup.HTML_ENTITIES))
            else:
                # For each line, try to guess an indent before the # character.
                # If an indent isn't found, just put it at the beginning of the line.
                s = str(soup)
                # Only add comment chars to lines 2 and following. The first line is already taken care of when entering the inComment state.
                lines = s.split('\n')
                L = [lines.pop(0)]
                for line in lines:
                    if self.indent and line.startswith(self.indent):
                        # If the line begins with an indent, insert the comment char after the indent
                        (indent, comment) = line.split(self.indent, 1)
                        L.append(self.indent + comment_string + comment)
                    else:
                        # Put a comment char at the beginning of the line, unless the next tag is a pre
                        if isinstance(soup.next, Tag) and (soup.next.name == 'pre'):
                            L.append(line)
                        else:
                            L.append(comment_string + line)
                # Now, glue each line together
                s = '\n'.join(L)
                self.at_newline = True if s.endswith('\n') else False                
                return s
        else:
            # We hae a tag.
            assert(isinstance(soup, Tag))
            L = []
            tags = []
            # See if this tag will cause a transition.<br />
            # Beautiful Soup stores attrs as a list. Convert to a dict to search easily.
            attrs = dict(soup.attrs)
            if ((state == self.State.outsidePre) and
                (soup.name == 'span') and
                ('class' in attrs) and
                ((attrs['class'] != 'c') and (attrs['class'] != 'c1'))):
                state = self.State.inPre
            elif ((state == self.State.inPre) and
                  (soup.name == 'span') and
                  ('class' in attrs) and
                  ((attrs['class'] == 'c') or (attrs['class'] == 'c1'))):
                state = self.State.inComment
                L.append(comment_string)
            elif state != self.State.inPre:
            # Output the tag only if we're still outsidePre or if we're still inComment.
                tags = self.strTag(soup)
                L.insert(0, tags[0])
            for c in soup.contents:
                L.append(self.translateBody(c, state))
            if tags and (len(tags) > 1):
                L.append(tags[1])
            return ''.join(L)
            
    # Output a tag, divided into opening and closing strings.
    def strTag(self, soup):
        assert(isinstance(soup, Tag))
        # Beautiful Soup v4.x version
#        dupSoup = Tag(BeautifulSoup(), HTMLTreeBuilder(), soup.name, soup.attrs)
        dupSoup = Tag(BeautifulSoup(), soup.name, soup.attrs)
        dupSoup.insert(0, "!")
        s = dupSoup.__str__(prettyPrint = False)
        return s.replace('\n', '\n' + comment_string).rsplit('!', 1)


# From http://effbot.org/zone/re-sub.htm#unescape-html:
import htmlentitydefs


# Removes HTML or XML character references and entities from a text string.<br /><br />@param text The HTML (or XML) source text.<br />@return The plain text, as a Unicode string, if necessary.
def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)
# 