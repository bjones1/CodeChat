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
if __name__ == '__main__':
    if one_test:
        ts = unittest.TestSuite()
        ts.addTest(TestCodeToHtml('test_3'))
#        ts.addTest(TestHtmlToCode('test_3'))
        unittest.TextTestRunner().run(ts)
    else:
        unittest.main()
