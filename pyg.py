# -*- coding: utf-8 -*-<br />
# <h1>Overview</h1>
# 
# This program, the HTML&lt;-&gt;code bridge, attempts to bring to life some of the ideas espoused by
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
# file is converted to the other format). Edit the converted file and rerun to translate it back; continue this as your standard development cycle.<br /><br />TODO: show a short demo video of how it's used.
# 
# 
# <h2>API</h2>
# 
# TODO: document the API. This would be be achieved with cross-references to API functions and perhaps even their documentation. For now, the API consists of:<br /><br /><a href="#convert">convert</a><br /><a href="#HtmlToCode">HtmlToCode</a><br /><a href="#CodeToHtml">CodeToHtml</a><br /><a href="#CodeToHtmlStyle">CodeToHtmlStyle</a><br />
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
#         comment.</li><li>The code to html link translates ## to # # (However, I don't
#         think there's a workaround for this).</li><li>The HTML editors (SeaMonkey) dork the
#         ending tags, putting extra
#         lines at the end. Find a workaround.<br /></li><li>The implementation is fragile -- an unescaped tag in the code 
#         destroys the HTML; likewise, the HTML editor can easily lose all 
#         whitespace and totally destroy the code.</li></ol>
# 
# <h3>To do</h3>
# <ol><li>Find a good HTML editor. KompoZer seems better than SeaMonkey, but doesn't render a lot of things correctly. Also, any edits in the source tag booger all the whitespace in a severe way.</li><li>Implement a <a href="http://packages.python.org/watchdog/">file
#           change monitor</a> to auto-translate on save.</li>
#     <li>Fix line numbering -- have the line numbers skip an empty line
#         on code to HTML; remove line numbers in HTML to code.</li>
#     <li>Offer some sort of cross-reference capability. This will
# require some significant thought. An idea: used named anchors to specify a line in the source, then use attributes of the <a href="http://www.w3schools.com/tags/tag_a.asp">&lt;a&gt;</a> tag as an indication that a cross-ref should be inserted (perhaps the <a href="http://www.w3schools.com/tags/att_a_rel.asp">rel</a> and <a href="http://www.w3schools.com/tags/att_a_rev.asp">rev</a> attributes).</li>
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
#     <li>Support C and C++ better. Waiting on a lexer fix before working on this any more. It's somewhat untested and probably doesn't support /* */
#         comments.</li><li>Look for unescaped &lt; and &gt;
#         characters. I need a nice regexp to distinguish a true tag from
#         random text.</li><li>Use ReST instead of HTML as the underlying
#         language, since that is so much more readable in code. Would need to
#         write / find a good HTML to ReST translator. Or perhaps just
#         translate recognized HTML to ReST and leave anything unrecognized in
#         the source.</li>
#     <li>Incorproate a language parser like Doxygen to auto-crossref function
#         names, variables, etc. Add a named anchor for each.</li><ol><li>One option: only identify global names.</li><li>Another option: identify all names, but add scoping -- perhaps function::name for local variables. However, dealing with names at a deeper nesting level would get messy (func::second {::blah?)</li></ol>
#     <li>Fix formatting: add a width: blah to the style for each comment based
#         on the number of preceeding characters.</li>
#     <li>Use a thinner wrap: get rid of &lt;pre&gt; tags, don't wrap comments
#         in any html. This would, I think, make HTML editors work a bit
#         better. Don't wrap comment at all; wrap all code (even spaces, crs which become &lt;br&gt; tag).<br /></li><li>Do a better job of matching what HTML shows with the code extracted. There's a lot of ways to shoot yourself in the foot with the present scheme. Examples: &lt;pre&gt;&lt;span class="c"&gt;comment&lt;br&gt;code&lt;/pre&gt; -- Looks right, but parsed as a comment. Parse in a WYSIWYG fashion: pay attention to the innermost tag when converting. Be lienent with whitespace -- ws as a comment followed by code would be marked as all code. One problem: how to show code in a comment?<br /></li><li>Find a way to avoid the font-size: small directive. Code like &lt;h2&gt;&lt;span class="c"&gt;blah&lt;/span&gt;&lt;/h2&gt; produces very small type. If the previous to-do is implemented, then style all code with a font-size: large.</li></ol>
#
# <h3>Next step</h3>
# Planning for the next feature: a thin wrap. This addresses items 14 and 16 above.<br /><ol><li>Change _create_stylesheet to inject a&nbsp;<code>white-space: pre; font-size:large;</code> to all non-comment styles.</li><li>Change DefaultStyle.styles[Text]
# = 'something' so that text (whitespace) will be wrapped. Change
# DefaultStyle.styles[Comment] = '' so comments won't be styled (or
# wrapped) at all.</li><li>In _format_lines, remove the &lt;pre&gt; pre-line wrap</li><li>How do I handle newlines? Begin each line of code with
# a wrapped &lt;br&gt;. If the previous line was code, then we're fine.
# If the previous line was a comment, then that's what we want, too.</li><ol><li>How to implement? I need knowledge of the next line of code. Perhaps as a _format_lines processing step: if the current line begins with code (a&lt;span class="not comment"&gt;), insert a wrapped &lt;br&gt;.</li></ol></ol>
#
# <h1>Code</h1>
# This section provides documentation of the front-end API for the
# HTML&lt;-&gt;Code bridge.<br />
# <h2>See also</h2>
# For additional documentation on the code, see:<br />
# <ul><li>The&nbsp;HTML&lt;-&gt;Code bridge <a href="pyg_module.html">module</a></li>
#     <li>The&nbsp;HTML&lt;-&gt;Code bridge <a href="pyg_test.html">test suite</a></li></ul>
from pygments.styles.default import DefaultStyle
from pygments.token import Generic, Literal, Name, Punctuation, Text, Other

# <a name="CodeToHtmlStyle"></a>Define a new style based on the default style, but which
# places comments in a non-italic font. Because the base class (Styles) is a metaclass, first
# change the desired member, then inherit (so the metaclass
# runs on the modified value in the default style).
DefaultStyle.styles[Generic] = '#000000'
DefaultStyle.styles[Literal] = '#000000'
DefaultStyle.styles[Name] = '#000000'
DefaultStyle.styles[Punctuation] = '#000000'
DefaultStyle.styles[Text] = '#000000'
DefaultStyle.styles[Other] = '#000000'
class CodeToHtmlStyle(DefaultStyle):
    pass

from pygments.lexers import get_lexer_for_filename
from pyg_module import CodeToHtmlFormatter, HtmlToCodeTranslator, source_extension
from pygments import highlight

# <a name="CodeToHtml"></a>Use Pygments with the CodeToHtmlFormatter to translate a source file to an HTML file.
def CodeToHtml(baseFileName):
    in_file_name = baseFileName + source_extension
    code = open(in_file_name, 'r').read()
    formatter = CodeToHtmlFormatter(full=True, nobackground=True,
                                    style=CodeToHtmlStyle)
    outfile = open(baseFileName + '.html', 'w')
    lexer = get_lexer_for_filename(in_file_name)
    hi_code = highlight(code, lexer, formatter)
    # Remove a little goop created by the full=True option above
    hi_code = hi_code.replace('\n<h2>' + formatter.title + '</h2>\n\n', '', 1)
    # Add a body style
    hi_code = hi_code.replace('pre { line-height: 125%; }', 
                              'body { font-family: sans-serif; ' + 
                              'display: inline-block; width: 5.5in; ' +
                              'color: #408080 }', 1)
    outfile.write(hi_code)
    print("Wrote " + baseFileName + '.html')

# <a name="HtmlToCode"></a>Use the HtmlToCodeTranslator class to translate a specific file.
def HtmlToCode(baseFileName):
    code = open(baseFileName + '.html', 'r').read()
    outfile = open(baseFileName + source_extension, 'w')
    xl = HtmlToCodeTranslator()
    outfile.write(xl.translate(code))
    print('Wrote ' + baseFileName + source_extension)

import os
# <a name="convert"></a>Convert the newer file to the older file's format, overwriting the older file.
def convert(baseFileName):
    source_file_name = baseFileName + source_extension
    html_file_name = baseFileName + '.html'
    source_time = os.stat(source_file_name).st_mtime \
      if os.path.exists(source_file_name) else 0
    html_time = os.stat(html_file_name).st_mtime \
      if os.path.exists(html_file_name) else 0
    html_time = 0
    if source_time > html_time:
        print('Source newer')
        CodeToHtml(baseFileName)
    elif source_time < html_time:
        print('HTML newer')
        HtmlToCode(baseFileName)
    else:
        print('Time is identical -- giving up')

# Run interface
if __name__ == '__main__':
    convert('pyg')
#    convert('pyg_module')
#    convert('pyg_test')
#    convert('winclient')
