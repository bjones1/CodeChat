# -*- coding: utf-8 -*-<br />
# <h1>Overview</h1>
# 
# This program attempts to bring to life some of the ideas espoused by
# Donald Knuth:<br />
# <blockquote>I believe that the time is ripe for significantly better
#       documentation of programs, and that we can best achieve this by
#       considering programs to be works of literature. Hence, my title:
#       "Literate Programming."<br /><br />
# 
#       Let us change our traditional attitude to the construction of
#       programs: Instead of imagining that our main task is to instruct a
#       computer what to do, let us concentrate rather on explaining to
#       human beings what we want a computer to do.<br /><br />
# 
#       The practitioner of literate programming can be regarded as an
#       essayist, whose main concern is with exposition and excellence of
#       style. Such an author, with thesaurus in hand, chooses the names
#       of variables carefully and explains what each variable means. He
#       or she strives for a program that is comprehensible because its
#       concepts have been introduced in an order that is best for human
#       understanding, using a mixture of formal and informal methods that
#       reinforce each other.<br /><br />
# 
#       -- Donald Knuth, &#8220;<a href="http://www.literateprogramming.com/knuthweb.pdf">Literate
# 
#         Programming</a> (1984)&#8221; in Literate Programming. CSLI, 1992, pg.
#       99.<br />
# </blockquote>
# 
# I believe that a program must exist simultaneously in two forms: as
# beautifully-formatted document replete with digrams and other
# illustrations and as source code, reflecting two complementary
# approaches to develping a program. A document provides a programmer
# with a means to express and record their design of the program,
# focusing on high-level design. As source code, it captures the
# minute details of an implementation of that idea.<br /><br />
# 
# Therefore, the purpose of this program is to provide a bidirectional
# link between a source file and a corresponding HTML document, so that
# the source can be exactly recreated from the HTML file and vice versa.
# The intention is to enable editing in the most convenient location:
# for code development and debugging, in a text editor / IDE; for design and
# documentation, in a WYSIWYG HTML editor.
# 
# 
# <h2>Getting started</h2>
# 
# Install Python (tested with v 2.6), <a href="http://pygments.org/">Pygments</a>
# (tested with v 1.4), and <a href="http://www.crummy.com/software/BeautifulSoup">Beautiful Soup</a>
# (tested with v3.2.0; the 4.x series was tested and didn't work well
# with the default parser). Then, simply run the program to convert
# between <code>pyg.py</code> and <code>pyg.html</code> (the newer
# file is converted to the other format).<br /><br />TODO: show a short demo video of how it's used.
# 
# 
# <h2>API</h2>
# 
# TODO: document the API.<br />
# 
# 
# <h2>Status</h2>
# 
# Currently, the bidirectional link is functional (though needs lots of
# testing, some bug fixes, and better documentation). I'm using it to write
# this document.
# 
# <h3>Bugs</h3>
# <ol><li>The HTML to code link assumes there's no comments before the
#         pre tag. I need some way to detect this an insert a
#         comment.</li>
#    <li>The code to html link incorrectly merges comments with
#         different amount of leading whitespace. It shouldn't.</li>
#     <li>The code to html link translates ## to # # (However, I don't
#         think there's a workaround for this).</li><li>The program dorks the
#         beginning and ending tags, putting extra
#         lines at the end and eventually moving comments around on the
#         first line.</li>
#     <li>SeaMonkey doesn't like &lt;pre&gt;. It's not that happy with
#         &lt;span&gt;, either. I suspect that only wrapping code lines in
#         a &lt;pre&gt; would help. Or, I could drop the pre entirely and
#         use a &lt;span&gt; on the spaces; I'm not sure which is better.
#         Either way, I need to minimize &lt;pre&gt; in the document.</li>
#     <li>The implementation is fragile -- an unescaped tag in the code 
#         destroys the HTML; likewise, the HTML editor can easily lose all 
#         whitespace and totally destroy the code.</li></ol>
# 
# <h3>To do</h3>
# <ol><li>Implement a <a href="http://packages.python.org/watchdog/">file
#           change monitor</a> to auto-translate on save.</li>
#     <li>Fix line numbering -- have the line numbers skip an empty line
#         on code to HTML; remove line numbers in HTML to code.</li>
#     <li>Offer some sort of cross-reference capability. This will
#         require some significant thought.</li>
#     <li>Much better testing. In particular, test all possible paths
#         through the state machine.</li>
#     <li>The HTML produced by the SeaMonkey composer doesn't read
#         nicely in the code. Establish some sort of pretty-print routine
#         to print code-readable HTML.</li>
#     <li>Come up with a better visual design. Blue text is annoying.
#         Perhaps use Sphinx styles?</li>
#     <li>Use a <a href="http://doc.qt.nokia.com/latest/qtextedit.html">QTextEdit</a>
#         widget to program a GUI editor. It would be really neat to:</li>
#         <ol><li>Open either HTML or source code</li>
#             <li>Have a hotkey toggle between HTML and text views, syncing
#                 cursor position in the toggle.</li>
#             <li>Auto-reload if either file is modified</li></ol>
#     <li>Support C and C++ better. It's untested and doesn't support /* */
#         comment currently.</li><li>Look for unescaped &lt; and &gt;
#         characters. I need a nice regexp to distinguish a true tag from
#         random text.</li>
#     <li>Create a GUI editor so, with a hotkey, the view would switch between
#         HTML and source.</li><li>Use ReST instead of HTML as the underlying
#         language, since that is so much more readable in code. Would need to
#         write / find a good HTML to ReST translator. Or perhaps just
#         translate recognized HTML to ReST and leave anything unrecognized in
#         the source.</li>
#     <li>Incorproate a language parser like Doxygen to auto-crossref function
#         names, variables, etc. Use a plain-text format to pick up on function
#         parameters.</li>
#     <li>Fix formatting: add a width: blah to the style for each comment based
#         on the number of preceeding characters.</li>
#     <li>Use a thinner wrap: get rid of &lt;pre&gt; tags, don't wrap comments
#         in any html. This would, I think, make HTML editors work a bit
#         better.</li>
#     <li>Things that bother me I'd like to fix:</li>
#         <ol><li>I can't see what HTML anchors already exist. This makes it
#                 hard to hyperlink. Just having auto-hyperlinks to global
#                 symbols would help a lot.</li>
#             <li>Many editor annoyances; it's fairly fraglie.</li>
#             <li>The documentation I have feels unwieldly: there's too much
#                 information on one page. Should I factor the code, or factors
#                 the docs into two files?</li></ol></ol>
# 
# <h1>Implementation</h1>
# 
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
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from pygments.formatters.html import _escape_html_table
from pygments.token import Token
import re

# The string indicating a comment in the chosen programming language. This must
# end in a space for the regular expression in _format_lines1 to work. The space
# also makes the output a bit prettier.
comment_string = '# '


# This class converts from source to to HTML. As the <a>overview</a>
# states, this uses Pygments to do most of the work, adding only a formatter
# to that library. Therefore, to use this class, simply select this class
# as the formatter for Pygments (see an example 
# <a href="#def_CodeToHtml">below</a>).<br />
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
            # <li> TODO: the test (ttype is Token.Comment) is not robust -- it only catches that particular token. However, many more sub-types <a href="http://pygments.org/docs/tokens/#comments">exist</a>; I don't think this catches them. Would isinstance(ttype, Token.Comment) work better? I'm not sure.</li></ul>
            if ttype is Token.Comment:
                style += 'font-family: sans-serif; white-space: normal; ' + \
                  'font-size: small; display: inline-block; width: 5.5in; '
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
        merged_token_source = self._merge_comments(token_source)
        source = self._format_lines1(merged_token_source)
        for is_code, line in source:
            if is_code and line.endswith('\n'):
                yield is_code, '<pre>' + line[:-1] + '</pre>\n'
            else:
                yield is_code, line
                
    # <h3>Merge multi-line comments</h3>
    # This routine takes tokens as its input, combining multiple lines of single-line comments separated
    # only by a newline into a single comment token. It's structured as a state machine, per the diagram below. Essentially, the machine looks for a multiline comment, which consists of: a newline, optional whitespace, a comment, a newline, optional whitespace, a comment. When this sequence is found such that the two whitespaces are identical, the two comments are combined with any intervening whitespace and the search continues. Additional comments:<br />
    # <ul><li>Transitions away from the sequence must be handled carefully (see the diagram). Each state may be presented with a comment, newline, whitespace, or any other token and must handle each possibility. To do this, <code>token_stack</code> contains a stack of tokens collected while walking through the state machines, which can be produced when the input varies from the multiline-comment path.<br /></li><li>"Whitespace" in this context does <b>not</b> include a newline. See the <code>ws</code> variable.<br /></li></ul><img alt="" src="state_machine.png" height="535" width="519" /><br />The state machine syntax: &lt;condition / action&gt;, so that nl / yield all tokens means that if a newline (\n character) is found, all tokens in token_stack will be yielded before moving to the next state. The additional abbreviation used: "ws" for whitespace (which does not include a newline).<br /><br />Note that the obvious alternative of doing this combining using a regular expression on the source text before tokenization doesn't work (I tried it). In particular, this removes all indications of where lines were broken earlier, making the comment a mess when going from the HTML back to code. It's possible that, with line wrapping implemented, this could be a much simpler and better approach.
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
#            print state, ttype, value
            if state == 0:
                if re.search(ws, value):
                    token_stack.append([ttype, value])
                    state = 1
                elif ttype is Token.Comment:
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
                if ttype is Token.Comment:
                    token_stack.append([ttype, value])
                    state = 2
                else:
                    for t in token_stack:
                        yield t
                    token_stack = []
                    yield ttype, value
                    state = 0 if value == '\n' else 5
            elif state == 2:
                # For now, assume we will never receive whitespace following a comment. TODO: this could happen in C: /*blah*/ <whitespace></whitespace>
                assert(not re.search(ws, value))
                # For now, assume we will never receive two comment tokens back to back. TODO: this could happen in C, perhaps as a /*blah*//*blah*/.
                assert(ttype is not Token.Comment)
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
                elif ttype is Token.Comment:
                    # Combine two comments into a single comment by modifying the value of the first comment token
                    token_stack[-2][1] = (''.join([ts[1] for ts in
                      token_stack[-2:]]) + value)
                    del token_stack[-1]
                    state = 2
                else:
                    for t in token_stack:
                        yield t
                    token_stack = []
                    yield ttype, value                
                    state = 0 if value == '\n' else 5
            elif state == 4:
                # For now, assume we will never receive whitespace following a comment. TODO: this could happen in C: /*blah*/ <whitespace></whitespace>
                assert(not re.search(ws, value))
                if ttype is Token.Comment:
                    # Combine two comments into a single comment by modifying the value of the first comment token<br />
                    # First, determine if we need to merge the previous three or the previous two entries on the stack (state transition 2, 3, 4 vs. 2, 4)
                    if re.search(ws, token_stack[-1][1]):
                        i = -3
                    else:
                        i = -2
                    token_stack[i][1] = (''.join([ts[1] for ts in
                      token_stack[i:]]) + value)
                    del token_stack[i + 1:]
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
            if ttype is Token.Comment:
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
        

# <h3>Supporting code</h3>
# Define a new style based on the default style, but which
# places comments in a non-italic font.<br />
# Because the base class (Styles) is a metaclass, first
# change the desired member, then inherit (so the metaclass
# runs on the modified value in the default style).
from pygments.styles.default import DefaultStyle
from pygments.token import Comment
DefaultStyle.styles[Comment] = "#408080"
class CodeToHtmlStyle(DefaultStyle):
    pass

# <a name="def_CodeToHtml"></a>Use Pygments with the CodeToHtmlFormatter to translate a source file to an HTML file.
def CodeToHtml(baseFileName):
    code = open(baseFileName + '.py', 'r').read()
    formatter = CodeToHtmlFormatter(full=True, nobackground=True,
                                    style=CodeToHtmlStyle)
    outfile = open(baseFileName + '.html', 'w')
    hi_code = highlight(code, PythonLexer(), formatter)
    # Remove a little goop created by the full=True option above
    hi_code = hi_code.replace('\n<h2>' + formatter.title + '</h2>\n\n', '', 1)
    # Force an &lt;pre&gt; tag to occupy one line, instead of collapsing to an empty element, with <code>min-height: 1em</code>. Make it single spaced instead of the default double spacing with <code>margin: 0px</code>.<br />
    hi_code = hi_code.replace('pre { line-height: 125%; }', 
                              'pre { line-height: 125%; margin: 0px; min-height: 1em }', 1)
    outfile.write(hi_code)
    print("Wrote " + baseFileName + '.html')

# <br />
# <h2><a name="CodeToHtml_overview"></a>HTML to Code<br />
# </h2>
# 
# 
# 
#     The HTML to code link relies on <a href="http://www.crummy.com/software/BeautifulSoup">Beautiful Soup</a>.
#     Some simplifying assumptions about the structure of the HTML
#     document:<br />
# <ul>
# <li>All code must be wrapped in a &lt;pre&gt;.<br />
# </li><li>All comments are wrapped in &lt;span class="c"&gt; or appear
#         as body text. Comments contain HTML.<br />
# </li><li>On a line, all code must come first, optionally followed by a
#         comment. Code may never follow a comment on a single line
#         (C-style /* */ in a line.</li><li>All header information (everything not inside the &lt;body&gt;
#         tag) is discarded, to be regenerated when code is translated
#         back to HTML.<br />
# </li>
# </ul>
# 
# 
# 
#     With this, body text is comment; &lt;pre&gt; begins discarding all
#     tags and emits only text until a comment tag, which outputs its
#     entire subtree as a comment (including any code-tagged text).
#     Newlines can be echoed without modification whether in code or
#     comment mode.<br />
# <h3>The implementation</h3>
# <ol>
# <li>The HTML document is parsed, then only the &lt;body&gt; tag
#         contents <a>translated</a>.</li><li><a>All comments</a> (body text or
#         anything in a &lt;span class="c"&gt; tag) are prepended with a
#         comment character and output verbatim (no HTML unescaping)</li><li><a>All code</a> (everything in a
#         &lt;pre&gt; tag from the beginning of the line to the first
#         &lt;span class="c") tag) is stripped of HTML tags, HTML
#         unescaped, then written.</li>
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
            # See if this tag will cause a transition
            # Beautiful Soup stores attrs as a list. Convert to a dict to search easily.
            attrs = dict(soup.attrs)
            if ((state == self.State.outsidePre) and
                (soup.name == 'pre')):
                state = self.State.inPre
            elif ((state == self.State.inPre) and
                  ('class' in attrs) and
                  (attrs['class'] == 'c')):
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


# Removes HTML or XML character references and entities from a text string.
# 
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.
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


# Test the HTML to code translator
import unittest

class TestHtmlToCode(unittest.TestCase):
    # Wrap a string in a body tag then translate it
    def xlate(self, s):
        tp = HtmlToCodeTranslator()
        return tp.translate("<body>" + s + "</body>")
        
    def test_strTag(self):
        soup = BeautifulSoup('<html>boink</html>')
        # contents[0] is the tag parsed by BeautifulSoup
        tp = HtmlToCodeTranslator()
        L = tp.strTag(soup.contents[0])
        self.assertEquals(L, ['<html>', '</html>'])
        
    def atest_xlComment(self):
        s = self.xlate("comment")
        self.assertEquals(s, "# comment")
    
    # Kinda finshy results here...
    def test_xlCode(self):
        s = self.xlate("<pre>\ncode</pre>")
        self.assertEquals(s, "\ncode")
        
    def test_xlCodeComment(self):
        s = self.xlate("<pre>\ncode <span class=c id=1>comment</span></pre>")
        self.assertEquals(s, "\ncode # comment")

    def test_xlTaglessCode1(self):
        s = self.xlate("<pre>\n<span style=n>code</span></pre>")
        self.assertEquals(s, "\ncode")

    def test_xlTaglessCode2(self):
        s = self.xlate('<pre>\n  <span class="n">code</span></pre>')
        self.assertEquals(s, "\n  code")

    def atest_xlCommentCodeComment(self):
        s = self.xlate("comment1<pre>\ncode <span class=c id=1>" +
          "comment2</span></pre>")
        self.assertEquals(s, "# comment1\ncode # comment2")

    def atest_xlWhitespace1(self):
        s = self.xlate("  comment")
        self.assertEquals(s, "#   comment")

    def test_xlWhitespace2(self):
        s = self.xlate("<pre>\n    code1\n    code2</pre>")
        self.assertEquals(s, "\n    code1\n    code2")
        
    # TODO: can't find a text case whose whitespace isn't eaten. Blah.
    def atest_MultiLineTag(self):
        s = self.xlate('<span\n  style="c">comment</span>')
        self.assertEquals(s, '# <span\n#  style="c">comment</span>\n')

    def test_xlWhitespace4(self):
        s = self.xlate('<pre>\n  <span class="c">comment1\n' +
          '  comment2</span></pre>')
        self.assertEquals(s, '\n  # comment1\n  # comment2')

    def test_xlWhitespace5(self):
        s = self.xlate('<pre>\n\n  <span class="c">comment1\n' +
          '  comment2</span></pre>')
        self.assertEquals(s, '\n\n  # comment1\n  # comment2')

    def test_0(self):
        s = self.xlate('<pre>  code <span class="c">comment</span>')
        self.assertEquals(s, '  code # comment')

    def test_1(self):
        s = self.xlate('<pre>  <span class="n">code</span> <span class="c">comment</span>')
        self.assertEquals(s, '  code # comment')

    def test_2(self):
        s = self.xlate('<pre><span class="c">comment1</span></pre>\n<pre>code2</pre>')
        self.assertEquals(s, '# comment1\ncode2')

    def test_3(self):
        s = self.xlate('<pre>  <span class="c">comment1\n  comment2</span></pre>')
        self.assertEquals(s, '  # comment1\n  # comment2')


class TestCodeToHtml(unittest.TestCase):
    def hilight(self, s):
        formatter = CodeToHtmlFormatter(nobackground=True)
        html = highlight(s, PythonLexer(), formatter)
        return html.replace("<pre>", "").replace("</pre>", "")
        
    # State machine test: transition from state 0 to 5
    def test_sm1(self):
        s = self.hilight("code")
        self.assertEqual(s, '<span class="n">code</span>\n')
    
    # State machine test: 0, 1, 5
    def test_sm2(self):
        s = self.hilight(" code")
        self.assertEqual(s, ' <span class="n">code</span>\n')

    # State machine test: 0, 1, 2, 5
    def test_sm3(self):
        s = self.hilight(" # comment\ncode")
        self.assertEqual(s, ' <span class="c">comment</span>\n' + 
          '<span class="n">code</span>\n')
                
    # State machine test: 0, 2, 5
    def test_sm4(self):
        s = self.hilight("# comment\ncode")
        self.assertEqual(s, '<span class="c">comment</span>\n' + 
          '<span class="n">code</span>\n')
                
    def test_mlComment1(self):
        s = self.hilight("# comment1\n# comment2")
        self.assertEqual(s, '<span class="c">comment1\ncomment2</span>\n')
        
    def test_mlComment2(self):
        s = self.hilight("# comment1\n\n# comment2")
        self.assertEqual(s, '<span class="c">comment1</span>\n\n' + 
          '<span class="c">comment2</span>\n')

    def test_mlComment3(self):
        s = self.hilight("# comment1\ncode # comment2")
        self.assertEqual(s, '<span class="c">comment1</span>\n' + 
          '<span class="n">code</span> <span class="c">comment2</span>\n')

    def test_mlComment4(self):
        s = self.hilight("  # comment1\n  # comment2")
        self.assertEqual(s, '  <span class="c">comment1\n  comment2</span>\n')

    def test_mlComment5(self):
        s = self.hilight("code\n\n# comment1\n# comment2")
        self.assertEqual(s, '<span class="n">code</span>\n\n' + 
          '<span class="c">comment1\ncomment2</span>\n')

    def test_mlComment6(self):
        s = self.hilight("code1\n\ncode2")
        self.assertEqual(s, '<span class="n">code1</span>\n\n' + 
          '<span class="n">code2</span>\n')

    def test_mlComment7(self):
        s = self.hilight(" \n # comment1\n # comment2")
        self.assertEqual(s, ' \n <span class="c">comment1\n comment2</span>\n')
        
def test(one_test):
    if one_test:
        ts = unittest.TestSuite()
#        ts.addTest(TestCodeToHtml('test_mlComment8'))
        ts.addTest(TestHtmlToCode('test_3'))
        unittest.TextTestRunner().run(ts)
    else:
        unittest.main()
        

# Use the HtmlToCodeTranslator class to translate a specific file.
def HtmlToCode(baseFileName):
    code = open(baseFileName + '.html', 'r').read()
    outfile = open(baseFileName + '.py', 'w')
    xl = HtmlToCodeTranslator()
    outfile.write(xl.translate(code))
    print('Wrote ' + baseFileName + '.py')


def convert(baseFileName):
    st_py =   os.stat(baseFileName + '.py')
    st_html = os.stat(baseFileName + '.html')
    if   st_py.st_mtime > st_html.st_mtime:
        print('Py newer')
        CodeToHtml(baseFileName)
    elif st_py.st_mtime < st_html.st_mtime:
        print('HTML newer')
        HtmlToCode(baseFileName)
    else:
        print('Time is identical -- giving up')

# Run interface
import os
if __name__ == '__main__':
#    test(one_test = False)
    convert('pyg')
