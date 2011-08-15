# -*- coding: utf-8 -*-<br />

from BeautifulSoup import BeautifulSoup
import unittest

# Test the HTML to code translator
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

    def test_4(self):
#        s = self.xlate('<span class="t">code1<br />\n</span><span class="t"> code1<br />\n</span>  comment\n<span class="t">  code2<br />\n</span>')
        s = self.xlate('''-*- coding: utf-8 -*-<br>
<h1>Overview</h1>

This program, the HTML&lt;-&gt;code bridge, attempts to bring to life some of the ideas espoused by
Donald Knuth:<br>
<blockquote>I believe that the time is ripe for significantly better
      documentation of programs, and that we can best achieve this by
      considering programs to be works of literature. Hence, my title:
      "Literate Programming."<br><br>

      Let us change our traditional attitude to the construction of
      programs: Instead of imagining that our main task is to instruct a
      computer what to do, let us concentrate rather on explaining to
      human beings what we want a computer to do.<br><br>

      The practitioner of literate programming can be regarded as an
      essayist, whose main concern is with exposition and excellence of
      style. Such an author, with thesaurus in hand, chooses the names
      of variables carefully and explains what each variable means. He
      or she strives for a program that is comprehensible because its
      concepts have been introduced in an order that is best for human
      understanding, using a mixture of formal and informal methods that
      reinforce each other.<br><br>

      -- Donald Knuth, &#8220;<a href="http://www.literateprogramming.com/knuthweb.pdf">Literate

        Programming</a> (1984)&#8221; in Literate Programming. CSLI, 1992, pg.
      99.<br>
</blockquote>

I believe that a program must exist simultaneously in two forms: as
beautifully-formatted document replete with digrams and other
illustrations and as source code, reflecting two complementary
approaches to develping a program. A document provides a programmer
with a means to express and record their design of the program,
focusing on high-level design. As source code, it captures the
minute details of an implementation of that idea.<br><br>

Therefore, the purpose of this program is to provide a bidirectional
link between a source file and a corresponding HTML document, so that
the source can be exactly recreated from the HTML file and vice versa.
The intention is to enable editing in the most convenient location:
for code development and debugging, in a text editor / IDE; for design and
documentation, in a WYSIWYG HTML editor.


<h2>Getting started</h2>

Install Python (tested with v 2.6), <a href="http://pygments.org/">Pygments</a>
(tested with v 1.4), and <a href="http://www.crummy.com/software/BeautifulSoup">Beautiful Soup</a>
(tested with v3.2.0; the 4.x series was tested and didn't work well
with the default parser). Then, simply run the program to convert
between <code>pyg.py</code> and <code>pyg.html</code>
(the newer
file is converted to the other format). Edit the converted file and
rerun to translate it back; continue this as your standard development
cycle.<br><br>TODO: show a short demo video of how it's used.


<h2>API</h2>
TODO: document the API. This would be be achieved with cross-references
to API functions and perhaps even their documentation. For now, the API
consists of:<br><br><a href="#convert">convert</a><br><a href="#HtmlToCode">HtmlToCode</a><br><a href="#CodeToHtml">CodeToHtml</a><br><a href="#CodeToHtmlStyle">CodeToHtmlStyle</a><br>


<h2>Status</h2>

Currently, the bidirectional link is functional (though needs lots of
testing, some bug fixes, and better documentation). I'm using it to write
this document.

<h3>Bugs</h3>
<ol><li>The code to html link translates ## to # # (However, I don't
        think there's a workaround for this).</li><li>The HTML editors (SeaMonkey) dork the
        ending tags, putting extra
        lines at the end. Find a workaround.<br></li><li>The implementation is fragile -- an unescaped tag in the code 
        destroys the HTML; likewise, the HTML editor can easily lose all 
        whitespace and totally destroy the code. Need some sort of safey net / check / backup.</li></ol>

<h3>To do</h3>
<ol><li>Find a good HTML editor. KompoZer seems better than SeaMonkey,
but doesn't render a lot of things correctly. Also, any edits in the
source tag booger all the whitespace in a severe way.</li><li>Implement a <a href="http://packages.python.org/watchdog/">file
          change monitor</a> to auto-translate on save.</li>
    <li>Fix line numbering -- have the line numbers skip an empty line
        on code to HTML; remove line numbers in HTML to code.</li>
    <li>Offer some sort of cross-reference capability. This will
require some significant thought. An idea: used named anchors to specify a line in the source, then use attributes of the <a href="http://www.w3schools.com/tags/tag_a.asp">&lt;a&gt;</a> tag as an indication that a cross-ref should be inserted (perhaps the <a href="http://www.w3schools.com/tags/att_a_rel.asp">rel</a> and <a href="http://www.w3schools.com/tags/att_a_rev.asp">rev</a> attributes).</li>
    <li>Much better testing. In particular, test all possible paths
        through the state machine.</li>
    <li>The HTML produced by the SeaMonkey composer doesn't read
        nicely in the code. Establish some sort of pretty-print routine
        to print code-readable HTML.</li>
    <li>Come up with a better visual design. Blue text is annoying.
        Perhaps use Sphinx styles?</li>
    <li>Use a <a href="http://doc.qt.nokia.com/latest/qtextedit.html">QTextEdit</a>
        widget to program a GUI editor. It would be really neat to:</li>
        <ol><li>Open either HTML or source code</li>
            <li>Have a hotkey toggle between HTML and text views, syncing
                cursor position in the toggle.</li>
            <li>Auto-reload if either file is modified</li></ol>
    <li>Support
C and C++ better. Waiting on a lexer fix before working on this any
more. It's somewhat untested and probably doesn't support /* */
comments.</li><li>Look for unescaped &lt; and &gt;
        characters. I need a nice regexp to distinguish a true tag from
        random text. This is particularly bad in commented-out code, since this shouldn't really be escaped at all!</li><li>Commented-out code formats poorly (all glommed together on one line). Is there a workaround?</li><li>Use ReST instead of HTML as the underlying
        language, since that is so much more readable in code. Would need to
        write / find a good HTML to ReST translator. Or perhaps just
        translate recognized HTML to ReST and leave anything unrecognized in
        the source.</li>
    <li>Incorproate a language parser like Doxygen to auto-crossref function
        names, variables, etc. Add a named anchor for each.</li><ol><li>One option: only identify global names.</li><li>Another
option: identify all names, but add scoping -- perhaps function::name
for local variables. However, dealing with names at a deeper nesting
level would get messy (func::second {::blah?)</li></ol>
    <li>Fix formatting: add a width: blah to the style for each comment based
        on the number of preceeding characters.</li><li>Do
a better job of matching what HTML shows with the code extracted.
Probably, this means using a &lt;br&gt; instead of the newlines in the
file. I think the only change is to translate &lt;br&gt; to \n and
remove all \n when converting code.</li><li>Provide a convert() function which accepts source file names and parses out the base file name. Allow it to use wildcards and do automatic backups. Read filenames to convert from argv (do test converts if empty; later, print out usage).</li></ol>

<h3>Next step</h3>
Planning for the next feature:&nbsp;TBD.<h1>Code</h1>
This section provides documentation of the front-end API for the
HTML&lt;-&gt;Code bridge.<br>
<h2>See also</h2>
For additional documentation on the code, see:<br>
<ul><li>The&nbsp;HTML&lt;-&gt;Code bridge <a href="pyg_module.html">module</a></li>
    <li>The&nbsp;HTML&lt;-&gt;Code bridge <a href="pyg_test.html">test suite</a></li></ul><span class="t"><br>
</span><span class="kn">from</span><span class="t"> </span><span class="nn">pygments.styles.default</span><span class="t"> </span><span class="kn">import</span><span class="t"> </span><span class="n">DefaultStyle</span><span class="t"><br>
</span><span class="kn">from</span><span class="t"> </span><span class="nn">pygments.token</span><span class="t"> </span><span class="kn">import</span><span class="t"> </span><span class="n">Generic</span><span class="p">,</span><span class="t"> </span><span class="n">Literal</span><span class="p">,</span><span class="t"> </span><span class="n">Name</span><span class="p">,</span><span class="t"> </span><span class="n">Punctuation</span><span class="p">,</span><span class="t"> </span><span class="n">Text</span><span class="p">,</span><span class="t"> </span><span class="n">Other</span><span class="t"><br>
</span><span class="t"><br>
</span><a name="CodeToHtmlStyle"></a>Define a new style based on the default style, but which
places comments in a non-italic font. Because the base class (Styles) is a metaclass, first
change the desired member, then inherit (so the metaclass
runs on the modified value in the default style).<span class="t"><br>
</span><span class="n">DefaultStyle</span><span class="o">.</span><span class="n">styles</span><span class="p">[</span><span class="n">Generic</span><span class="p">]</span><span class="t"> </span><span class="o">=</span><span class="t"> </span><span class="s">'#000000'</span><span class="t"><br>
</span><span class="n">DefaultStyle</span><span class="o">.</span><span class="n">styles</span><span class="p">[</span><span class="n">Literal</span><span class="p">]</span><span class="t"> </span><span class="o">=</span><span class="t"> </span><span class="s">'#000000'</span><span class="t"><br>
</span><span class="n">DefaultStyle</span><span class="o">.</span><span class="n">styles</span><span class="p">[</span><span class="n">Name</span><span class="p">]</span><span class="t"> </span><span class="o">=</span><span class="t"> </span><span class="s">'#000000'</span><span class="t"><br>
</span><span class="n">DefaultStyle</span><span class="o">.</span><span class="n">styles</span><span class="p">[</span><span class="n">Punctuation</span><span class="p">]</span><span class="t"> </span><span class="o">=</span><span class="t"> </span><span class="s">'#000000'</span><span class="t"><br>
</span><span class="n">DefaultStyle</span><span class="o">.</span><span class="n">styles</span><span class="p">[</span><span class="n">Text</span><span class="p">]</span><span class="t"> </span><span class="o">=</span><span class="t"> </span><span class="s">'#000000'</span><span class="t"><br>
</span><span class="n">DefaultStyle</span><span class="o">.</span><span class="n">styles</span><span class="p">[</span><span class="n">Other</span><span class="p">]</span><span class="t"> </span><span class="o">=</span><span class="t"> </span><span class="s">'#000000'</span><span class="t"><br>
</span><span class="k">class</span><span class="t"> </span><span class="nc">CodeToHtmlStyle</span><span class="p">(</span><span class="n">DefaultStyle</span><span class="p">):</span><span class="t"><br>
</span><span class="t">    </span><span class="k">pass</span><span class="t"><br>
</span><span class="t"><br>
</span><span class="kn">from</span><span class="t"> </span><span class="nn">pygments.lexers</span><span class="t"> </span><span class="kn">import</span><span class="t"> </span><span class="n">get_lexer_for_filename</span><span class="t"><br>
</span><span class="kn">from</span><span class="t"> </span><span class="nn">pyg_module</span><span class="t"> </span><span class="kn">import</span><span class="t"> </span><span class="n">CodeToHtmlFormatter</span><span class="p">,</span><span class="t"> </span><span class="n">HtmlToCodeTranslator</span><span class="p">,</span><span class="t"> </span><span class="n">source_extension</span><span class="t"><br>
</span><span class="kn">from</span><span class="t"> </span><span class="nn">pygments</span><span class="t"> </span><span class="kn">import</span><span class="t"> </span><span class="n">highlight</span><span class="t"><br>
</span><span class="t"><br>
</span><a name="CodeToHtml"></a>Use Pygments with the CodeToHtmlFormatter to translate a source file to an HTML file.<span class="t"><br>
</span><span class="k">def</span><span class="t"> </span><span class="nf">CodeToHtml</span><span class="p">(</span><span class="n">baseFileName</span><span class="p">):</span><span class="t"><br>
</span><span class="t">    </span><span class="n">in_file_name</span><span class="t"> </span><span class="o">=</span><span class="t"> </span><span class="n">baseFileName</span><span class="t"> </span><span class="o">+</span><span class="t"> </span><span class="n">source_extension</span><span class="t"><br>
</span><span class="t">    </span><span class="n">code</span><span class="t"> </span><span class="o">=</span><span class="t"> </span><span class="nb">open</span><span class="p">(</span><span class="n">in_file_name</span><span class="p">,</span><span class="t"> </span><span class="s">'r'</span><span class="p">)</span><span class="o">.</span><span class="n">read</span><span class="p">()</span><span class="t"><br>
</span><span class="t">    </span><span class="n">formatter</span><span class="t"> </span><span class="o">=</span><span class="t"> </span><span class="n">CodeToHtmlFormatter</span><span class="p">(</span><span class="n">full</span><span class="o">=</span><span class="bp">True</span><span class="p">,</span><span class="t"> </span><span class="n">nobackground</span><span class="o">=</span><span class="bp">True</span><span class="p">,</span><span class="t"><br>
</span><span class="t">                                    </span><span class="n">style</span><span class="o">=</span><span class="n">CodeToHtmlStyle</span><span class="p">)</span><span class="t"><br>
</span><span class="t">    </span><span class="n">outfile</span><span class="t"> </span><span class="o">=</span><span class="t"> </span><span class="nb">open</span><span class="p">(</span><span class="n">baseFileName</span><span class="t"> </span><span class="o">+</span><span class="t"> </span><span class="s">'.html'</span><span class="p">,</span><span class="t"> </span><span class="s">'w'</span><span class="p">)</span><span class="t"><br>
</span><span class="t">    </span><span class="n">lexer</span><span class="t"> </span><span class="o">=</span><span class="t"> </span><span class="n">get_lexer_for_filename</span><span class="p">(</span><span class="n">in_file_name</span><span class="p">)</span><span class="t"><br>
</span><span class="t">    </span><span class="n">hi_code</span><span class="t"> </span><span class="o">=</span><span class="t"> </span><span class="n">highlight</span><span class="p">(</span><span class="n">code</span><span class="p">,</span><span class="t"> </span><span class="n">lexer</span><span class="p">,</span><span class="t"> </span><span class="n">formatter</span><span class="p">)</span><span class="t"><br>
</span><span class="t">    </span>Remove a little goop created by the full=True option above<span class="t"><br>
</span><span class="t">    </span><span class="n">hi_code</span><span class="t"> </span><span class="o">=</span><span class="t"> </span><span class="n">hi_code</span><span class="o">.</span><span class="n">replace</span><span class="p">(</span><span class="s">'</span><span class="se">\n</span><span class="s">&lt;h2&gt;'</span><span class="t"> </span><span class="o">+</span><span class="t"> </span><span class="n">formatter</span><span class="o">.</span><span class="n">title</span><span class="t"> </span><span class="o">+</span><span class="t"> </span><span class="s">'&lt;/h2&gt;</span><span class="se">\n\n</span><span class="s">'</span><span class="p">,</span><span class="t"> </span><span class="s">''</span><span class="p">,</span><span class="t"> </span><span class="mi">1</span><span class="p">)</span><span class="t"><br>
</span><span class="t">    </span>Add a body style<span class="t"><br>
</span><span class="t">    </span><span class="n">hi_code</span><span class="t"> </span><span class="o">=</span><span class="t"> </span><span class="n">hi_code</span><span class="o">.</span><span class="n">replace</span><span class="p">(</span><span class="s">'pre { line-height: 125%; }'</span><span class="p">,</span><span class="t"> <br></span>
<span class="t">                              </span><span class="s">'body { font-family: sans-serif; '</span><span class="t"> </span><span class="o">+</span><span class="t"> <br></span>
<span class="t">                              </span><span class="s">'display: inline-block; width: 5.5in; '</span><span class="t"> </span><span class="o">+</span><span class="t"><br>
</span><span class="t">                              </span><span class="s">'color: #408080 }'</span><span class="p">,</span><span class="t"> </span><span class="mi">1</span><span class="p">)</span><span class="t"><br>
</span><span class="t">    </span><span class="n">outfile</span><span class="o">.</span><span class="n">write</span><span class="p">(</span><span class="n">hi_code</span><span class="p">)</span><span class="t"><br>
</span><span class="t">    </span><span class="k">print</span><span class="p">(</span><span class="s">"Wrote "</span><span class="t"> </span><span class="o">+</span><span class="t"> </span><span class="n">baseFileName</span><span class="t"> </span><span class="o">+</span><span class="t"> </span><span class="s">'.html'</span><span class="p">)</span><span class="t"><br>
</span><span class="t"><br>
</span><a name="HtmlToCode"></a>Use the HtmlToCodeTranslator class to translate a specific file.<span class="t"><br>
</span><span class="k">def</span><span class="t"> </span><span class="nf">HtmlToCode</span><span class="p">(</span><span class="n">baseFileName</span><span class="p">):</span><span class="t"><br>
</span><span class="t">    </span><span class="n">code</span><span class="t"> </span><span class="o">=</span><span class="t"> </span><span class="nb">open</span><span class="p">(</span><span class="n">baseFileName</span><span class="t"> </span><span class="o">+</span><span class="t"> </span><span class="s">'.html'</span><span class="p">,</span><span class="t"> </span><span class="s">'r'</span><span class="p">)</span><span class="o">.</span><span class="n">read</span><span class="p">()</span><span class="t"><br>
</span><span class="t">    </span><span class="n">outfile</span><span class="t"> </span><span class="o">=</span><span class="t"> </span><span class="nb">open</span><span class="p">(</span><span class="n">baseFileName</span><span class="t"> </span><span class="o">+</span><span class="t"> </span><span class="n">source_extension</span><span class="p">,</span><span class="t"> </span><span class="s">'w'</span><span class="p">)</span><span class="t"><br>
</span><span class="t">    </span><span class="n">xl</span><span class="t"> </span><span class="o">=</span><span class="t"> </span><span class="n">HtmlToCodeTranslator</span><span class="p">()</span><span class="t"><br>
</span><span class="t">    </span><span class="n">outfile</span><span class="o">.</span><span class="n">write</span><span class="p">(</span><span class="n">xl</span><span class="o">.</span><span class="n">translate</span><span class="p">(</span><span class="n">code</span><span class="p">))</span><span class="t"><br>
</span><span class="t">    </span><span class="k">print</span><span class="p">(</span><span class="s">'Wrote '</span><span class="t"> </span><span class="o">+</span><span class="t"> </span><span class="n">baseFileName</span><span class="t"> </span><span class="o">+</span><span class="t"> </span><span class="n">source_extension</span><span class="p">)</span><span class="t"><br>
</span><span class="t"><br>
</span><span class="kn">import</span><span class="t"> </span><span class="nn">os</span><span class="t"><br>
</span><a name="convert"></a>Convert the newer file to the older file's format, overwriting the older file.<span class="t"><br>
</span><span class="k">def</span><span class="t"> </span><span class="nf">convert</span><span class="p">(</span><span class="n">baseFileName</span><span class="p">):</span><span class="t"><br>
</span><span class="t">    </span><span class="n">source_file_name</span><span class="t"> </span><span class="o">=</span><span class="t"> </span><span class="n">baseFileName</span><span class="t"> </span><span class="o">+</span><span class="t"> </span><span class="n">source_extension</span><span class="t"><br>
</span><span class="t">    </span><span class="n">html_file_name</span><span class="t"> </span><span class="o">=</span><span class="t"> </span><span class="n">baseFileName</span><span class="t"> </span><span class="o">+</span><span class="t"> </span><span class="s">'.html'</span><span class="t"><br>
</span><span class="t">    </span><span class="n">source_time</span><span class="t"> </span><span class="o">=</span><span class="t"> </span><span class="n">os</span><span class="o">.</span><span class="n">stat</span><span class="p">(</span><span class="n">source_file_name</span><span class="p">)</span><span class="o">.</span><span class="n">st_mtime</span><span class="t"> \<br></span>
<span class="t">      </span><span class="k">if</span><span class="t"> </span><span class="n">os</span><span class="o">.</span><span class="n">path</span><span class="o">.</span><span class="n">exists</span><span class="p">(</span><span class="n">source_file_name</span><span class="p">)</span><span class="t"> </span><span class="k">else</span><span class="t"> </span><span class="mi">0</span><span class="t"><br>
</span><span class="t">    </span><span class="n">html_time</span><span class="t"> </span><span class="o">=</span><span class="t"> </span><span class="n">os</span><span class="o">.</span><span class="n">stat</span><span class="p">(</span><span class="n">html_file_name</span><span class="p">)</span><span class="o">.</span><span class="n">st_mtime</span><span class="t"> \<br></span>
<span class="t">      </span><span class="k">if</span><span class="t"> </span><span class="n">os</span><span class="o">.</span><span class="n">path</span><span class="o">.</span><span class="n">exists</span><span class="p">(</span><span class="n">html_file_name</span><span class="p">)</span><span class="t"> </span><span class="k">else</span><span class="t"> </span><span class="mi">0</span><span class="t"><br>
</span><span class="t">    </span><span class="n">html_time</span><span class="t"> </span><span class="o">=</span><span class="t"> </span><span class="mi">0</span><span class="t"><br>
</span><span class="t">    </span><span class="k">if</span><span class="t"> </span><span class="n">source_time</span><span class="t"> </span><span class="o">&gt;</span><span class="t"> </span><span class="n">html_time</span><span class="p">:</span><span class="t"><br>
</span><span class="t">        </span><span class="k">print</span><span class="p">(</span><span class="s">'Source newer'</span><span class="p">)</span><span class="t"><br>
</span><span class="t">        </span><span class="n">CodeToHtml</span><span class="p">(</span><span class="n">baseFileName</span><span class="p">)</span><span class="t"><br>
</span><span class="t">    </span><span class="k">elif</span><span class="t"> </span><span class="n">source_time</span><span class="t"> </span><span class="o">&lt;</span><span class="t"> </span><span class="n">html_time</span><span class="p">:</span><span class="t"><br>
</span><span class="t">        </span><span class="k">print</span><span class="p">(</span><span class="s">'HTML newer'</span><span class="p">)</span><span class="t"><br>
</span><span class="t">        </span><span class="n">HtmlToCode</span><span class="p">(</span><span class="n">baseFileName</span><span class="p">)</span><span class="t"><br>
</span><span class="t">    </span><span class="k">else</span><span class="p">:</span><span class="t"><br>
</span><span class="t">        </span><span class="k">print</span><span class="p">(</span><span class="s">'Time is identical -- giving up'</span><span class="p">)</span><span class="t"><br>
</span><span class="t"><br>
</span>Run interface<span class="t"><br>
</span><span class="k">if</span><span class="t"> </span><span class="n">__name__</span><span class="t"> </span><span class="o">==</span><span class="t"> </span><span class="s">'__main__'</span><span class="p">:</span><span class="t"><br>
</span><span class="t">    </span><span class="n">convert</span><span class="p">(</span><span class="s">'pyg'</span><span class="p">)</span><span class="t"><br>
</span>   convert('pyg_module')
   convert('pyg_test')
   convert('winclient')<span class="t"><br>
</span>''')
#        s = self.xlate('<span class="t">  </span><span class="t">code</span>')
        print '\n'*10
        s = self.xlate('<span class="t">  </span>Remove a little goop created by the full=True option above')
        print s
#        self.assertEquals(s, '')

from pygments.lexers import PythonLexer, CLexer
from pygments import highlight
from pyg_module import CodeToHtmlFormatter, HtmlToCodeTranslator
import pyg_module

class TestCodeToHtml(unittest.TestCase):
    def hilight(self, s):
        pyg_module.comment_string = '# '
        formatter = CodeToHtmlFormatter(nobackground=True)
        html = highlight(s, PythonLexer(), formatter)
        return html.replace("<pre>", "").replace("</pre>", "")
        
    def c_hilight(self, s):
        pyg_module.comment_string = '// '
        formatter = CodeToHtmlFormatter(nobackground=True)
        html = highlight(s, CLexer(), formatter)
        return html
        
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
        
    def test_0(self):
        s = self.c_hilight('// Comment')
        self.assertEqual(s, '<pre><span class="c1">Comment</span></pre>\n')

    # TODO: Not parsed correctly: it comes across as a Token.Comment.Preproc        
    def atest_1(self):
        s = self.c_hilight('// comment\n#define blah 1')
        self.assertEqual(s, '<pre><span class="cp">// comment</span></pre>\n<pre><span class="c1">#define blah 1</span></pre>\n')
        
    def test_2(self):
        s = self.c_hilight('// comment1\n// comment2\n')
        self.assertEqual(s, '<pre><span class="c1">comment1\ncomment2</span></pre>\n')

    def test_3(self):
        s = self.hilight('  code\n# comment')
        print s
        self.assertEqual(s, '')
        

one_test = True
def runAll():
    if one_test:
        ts = unittest.TestSuite()
#        ts.addTest(TestCodeToHtml('test_3'))
        ts.addTest(TestHtmlToCode('test_4'))
        unittest.TextTestRunner().run(ts)
    else:
        unittest.main()

if __name__ == '__main__':
    runAll()
