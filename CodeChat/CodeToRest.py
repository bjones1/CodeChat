# .. Copyright (C) 2012-2017 Bryan A. Jones.
#
#    This file is part of CodeChat.
#
#    CodeChat is free software: you can redistribute it and/or modify it under
#    the terms of the GNU General Public License as published by the Free
#    Software Foundation, either version 3 of the License, or (at your option)
#    any later version.
#
#    CodeChat is distributed in the hope that it will be useful, but WITHOUT ANY
#    WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#    FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#    details.
#
#    You should have received a copy of the GNU General Public License along
#    with CodeChat.  If not, see <http://www.gnu.org/licenses/>.
#
# *****************************************************
# |docname| - a module to translate source code to reST
# *****************************************************
# The API_ lists four functions which convert source code into either reST or
# HTML. It relies on `source_lexer` to classify the source as code or comment, then `_generate_rest`_ to convert this to reST. `Supporting reST directives and roles`_ define CodeChat-specific syntax used in this conversion.
#
# .. contents::
#
# Imports
# =======
# These are listed in the order prescribed by `PEP 8
# <http://www.python.org/dev/peps/pep-0008/#imports>`_.
#
# Standard library
# ----------------
from io import StringIO
import os.path
from pathlib import Path

# Third-party imports
# -------------------
# Used to open files with unknown encodings and to run docutils itself.
from docutils import io, core, nodes
# Import CodeBlock as a base class for FencedCodeBlock.
from docutils.parsers.rst.directives.body import CodeBlock
# Import directives to register the new FencedCodeBlock and SetLine directives.
from docutils.parsers.rst import directives, Directive, roles
# For the docutils default style sheet and template
from docutils.writers.html4css1 import Writer

# Local application imports
# -------------------------
from .SourceClassifier import source_lexer, get_lexer, _debug_print, \
    codechat_style


# API
# ===
# The following routines provide easy access to the core functionality of this
# module: code_to_rest_string_, code_to_rest_file_, code_to_html_string_, and
# code_to_html_file_.
#
# .. _code_to_rest_string:
#
# This function converts a string containing source code to reST, preserving all indentations of both source code and comments. To do so, the comment characters are stripped from reST-formatted comments and all code is placed inside code blocks.
def code_to_rest_string(
    # _`code_str`: the code to translate to reST.
    code_str,
    # See `options <options>`.
    **options):

    # Use a StringIO to capture writes into a string.
    output_rst = StringIO()
    # Include a header containing some `CodeChat style`. Don't put this in a separate ``.js`` file, since docutils doesn't have an easy way to include it.
    output_rst.write(rest_codechat_style)
    ast_syntax_error, classified_lines = source_lexer(code_str, get_lexer(code=code_str, **options))
    if ast_syntax_error:
        output_rst.write('.. error:: {}\n\n'.format(ast_syntax_error))
    _generate_rest(classified_lines, output_rst)
    return output_rst.getvalue()


# .. _code_to_rest_file:
#
# Convert a source file to a reST file.
def code_to_rest_file(
    # .. _source_path:
    #
    # Path to a source code file to process.
    source_path,
    # Path to a destination reST file to create. It will be overwritten if it
    # already exists. If not specified, it is ``source_path.rst``.
    rst_path,
    # .. _input_encoding:
    #
    # Encoding to use for the input file. The default of None detects the
    # encoding of the input file.
    input_encoding=None,
    # .. _output_encoding:
    #
    # Encoding to use for the output file.
    output_encoding='utf-8',
    # See `options <options>`.
    **options):

    # Provide a default ``rst_path``.
    if not rst_path:
        rst_path = source_path + '.rst'
    # Use docutil's I/O classes to better handle and sniff encodings.
    #
    # Note: both these classes automatically close themselves after a
    # read or write.
    fi = io.FileInput(source_path=source_path, encoding=input_encoding)
    fo = io.FileOutput(destination_path=rst_path, encoding=output_encoding)
    code_str = fi.read()
    lexer = get_lexer(filename=source_path, code=code_str, **options)
    rst = code_to_rest_string(code_str, lexer=lexer)
    fo.write(rst)


# .. _code_to_html_string:
#
# This converts a string containing source code to HTML, which it returns as a
# string.
def code_to_html_string(
    # See code_str_.
    code_str,
    # A file-like object where warnings and errors will be written, or None to
    # send them to stderr.
    warning_stream=None,
    # See `options <options>`.
    **options):

    rest = code_to_rest_string(code_str, **options)
    # `docutils
    # <http://docutils.sourceforge.net/docs/user/tools.html#rst2html-py>`_
    # converts reST to HTML.
    html = core.publish_string(rest, writer_name='html',
      settings_overrides={
        # Include our custom css file: provide the path to the default css and
        # then to our css. The style sheet dirs must include docutils defaults.
        'stylesheet_path': ','.join(Writer.default_stylesheets + ['CodeChat.css']),
        'stylesheet_dirs': Writer.default_stylesheet_dirs +
            [os.path.join(os.path.dirname(__file__), 'template')],
        # Make sure to use Unicode everywhere.
        'output_encoding': 'unicode',
        'input_encoding' : 'unicode',
        # Don't stop processing, no matter what.
        'halt_level'     : 5,
        # Capture errors to a string and return it.
        'warning_stream' : warning_stream})
    return html


# .. _code_to_html_file:
#
# Convert source code stored in a file to HTML, which is saved in another file.
def code_to_html_file(
    # See source_path_.
    source_path,
    # Destination file name to hold the generated HTML. This file will be
    # overwritten. If not supplied, ``source_path.html`` will be assumed.
    html_path=None,
    # See input_encoding_.
    input_encoding=None,
    # See output_encoding_.
    output_encoding='utf-8'):

    html_path = html_path or source_path + '.html'
    fi = io.FileInput(source_path=source_path, encoding=input_encoding)
    fo = io.FileOutput(destination_path=html_path, encoding=output_encoding)

    code_str = fi.read()
    lexer = get_lexer(filename=source_path, code=code_str)
    html = code_to_html_string(code_str, lexer=lexer)

    fo.write(html)


# Provide correct formatting of CodeChat-produced documents in reST based on the `CodeChat style`.
rest_codechat_style = (
    '.. raw:: html\n'
    '\n'
    ' ' + codechat_style
)


# Converting classified code to reST
# ==================================
# Approach
# --------
# When creating reST block containing code or comments, two difficulties
# arise: preserving the indentation
# of both source code and comments; and preserving empty lines of code at the
# beginning or end of a block of code. In the following examples, examine both
# the source code and the resulting HTML to get the full picture, since the text
# below is (after all) in reST, and will be therefore be transformed to HTML.
#
# First, consider a method to preserve empty lines of code. Consider, for
# example, the following:
#
# +--------------------------+-------------------------+-----------------------------------+
# + Python source            + Translated to reST      + Translated to (simplified) HTML   |
# +==========================+=========================+===================================+
# | .. code-block:: Python3  | Do something ::         | .. code-block:: html              |
# |                          |                         |                                   |
# |  # Do something          |  foo = 1                |  <p>Do something:</p>             |
# |  foo = 1                 |                         |  <pre>foo = 1                     |
# |                          | Do something else ::    |  </pre>                           |
# |  # Do something else     |                         |  <p>Do something else:</p>        |
# |  bar = 2                 |  bar = 2                |  <pre>bar = 2                     |
# |                          |                         |  </pre>                           |
# +--------------------------+-------------------------+-----------------------------------+
#
# In this example, the blank line is lost, since reST allows the literal bock
# containing ``foo = 1`` to end with multiple blank lines; the resulting HTML
# contains only one newline between each of these lines. To solve this, some CSS
# hackery helps tighten up spacing between lines. In addition, this routine adds
# a one-line fence, removed during processing, at the beginning and end of each
# code block to preserve blank lines. The new translation becomes:
#
# +--------------------------+-------------------------+-----------------------------------+
# + Python source            + Translated to reST      + Translated to (simplified) HTML   |
# +==========================+=========================+===================================+
# | .. code-block:: Python3  | Do something            | .. code-block:: html              |
# |                          |                         |                                   |
# |  # Do something          | .. fenced-code::        |  <p>Do something:</p>             |
# |  foo = 1                 |                         |  <pre>foo = 1                     |
# |                          |    Beginning fence      |                                   |
# |  # Do something else     |    foo = 1              |  </pre>                           |
# |  bar = 2                 |                         |  <p>Do something else:</p>        |
# |                          |    Ending fence         |  <pre>bar = 2                     |
# |                          |                         |  </pre>                           |
# |                          | Do something else       |                                   |
# |                          |                         |                                   |
# |                          | .. fenced-code::        |                                   |
# |                          |                         |                                   |
# |                          |    Beginning fence      |                                   |
# |                          |    bar = 2              |                                   |
# |                          |    Ending fence         |                                   |
# |                          |                         |                                   |
# |                          |                         |                                   |
# +--------------------------+-------------------------+-----------------------------------+
#
# Preserving indentation
# ^^^^^^^^^^^^^^^^^^^^^^
# The same fence approach also preserves indentation. Without the fences,
# indentation is consumed by the reST parser:
#
# +--------------------------+-------------------------+-----------------------------------+
# + Python source            + Translated to reST      + Translated to (simplified) HTML   |
# +==========================+=========================+===================================+
# | .. code-block:: Python3  | One space indent ::     | .. code-block:: html              |
# |                          |                         |                                   |
# |  # One space indent      |   foo = 1               |  <p>One space indent</p>          |
# |   foo = 1                |                         |  <pre>foo = 1                     |
# |  # No indent             | No indent ::            |  </pre>                           |
# |  bar = 2                 |                         |  <p>No indent</p>                 |
# |                          |  bar = 2                |  <pre>bar = 1                     |
# |                          |                         |  </pre>                           |
# +--------------------------+-------------------------+-----------------------------------+
#
# With fences added:
#
# +--------------------------+-------------------------+-----------------------------------+
# + Python source            + Translated to reST      + Translated to (simplified) HTML   |
# +==========================+=========================+===================================+
# | .. code-block:: Python3  | One space indent        | .. code-block:: html              |
# |                          |                         |                                   |
# |  # One space indent      | .. fenced-code::        |  <p>One space indent</p>          |
# |   foo = 1                |                         |  <pre> foo = 1                    |
# |  # No indent             |    Beginning fence      |  </pre>                           |
# |  bar = 2                 |     foo = 1             |  <p>No indent</p>                 |
# |                          |    Ending fence         |  <pre>bar = 1                     |
# |                          |                         |  </pre>                           |
# |                          | No indent               |                                   |
# |                          |                         |                                   |
# |                          | .. fenced-code::        |                                   |
# |                          |                         |                                   |
# |                          |    Beginning fence      |                                   |
# |                          |    bar = 1              |                                   |
# |                          |    Ending fence         |                                   |
# +--------------------------+-------------------------+-----------------------------------+
#
# Preserving indentation for comments is more difficult. Blockquotes in reST are
# defined by common indentation, so that any number of (common) spaces define a
# blockquote. So, the distance between a zero and two-space indent is the same
# as the distance between a two-space and a three-space indent; we need the
# second indent to be half the size of the first.
#
# +--------------------------+-------------------------+-----------------------------------+
# + Python source            + Translated to reST      + Translated to (simplified) HTML   |
# +==========================+=========================+===================================+
# | .. code-block:: Python3  | No indent               | .. code-block:: html              |
# |                          |                         |                                   |
# |  # No indent             |   Two space indent      |  <p>No indent</p>                 |
# |    # Two space indent    |                         |  <blockquote>Two space indent     |
# |     # Three space indent |    Three space indent   |   <blockquote>Three space         |
# |                          |                         |     indent                        |
# |                          |                         |   </blockquote>                   |
# |                          |                         |  </blockquote>                    |
# +--------------------------+-------------------------+-----------------------------------+
#
# To fix this, the `raw directive
# <http://docutils.sourceforge.net/docs/ref/rst/directives.html#raw-data-pass-through>`_
# is used to insert a pair of ``<div>`` and ``<div>`` HTML elements which set
# the left margin of indented text based on how many spaces (0.5 em = 1 space).
#
# +--------------------------+-------------------------+-----------------------------------+
# + Python source            + Translated to reST      | Translated to (simplified) HTML   |
# +==========================+=========================+===================================+
# | .. code-block:: Python3  |  No indent              | .. code-block:: html              |
# |                          |                         |                                   |
# |  # No indent             |  .. raw:: html          |  <p>No indent</p>                 |
# |    # Two space indent    |                         |  <div style="margin-left:1.0em">  |
# |     # Three space indent |   <div style=           |    <p>Two space indent</p>        |
# |                          |   "margin-left:1.0em;"> |  </div>                           |
# |                          |                         |  <div style="margin-left:1.5em;"> |
# |                          |  Two space indent       |    <p>Three space indent</p>      |
# |                          |                         |  </div>                           |
# |                          |  .. raw:: html          |                                   |
# |                          |                         |                                   |
# |                          |   </div><div style=     |                                   |
# |                          |   "margin-left:1.5em;"> |                                   |
# |                          |                         |                                   |
# |                          |  Three space indent     |                                   |
# |                          |                         |                                   |
# |                          |  .. raw:: html          |                                   |
# |                          |                         |                                   |
# |                          |   </div>                |                                   |
# +--------------------------+-------------------------+-----------------------------------+

# Following either a fenced code block or a raw block, care must be taken to
# separate these blocks' content from indented comments which follow them. For
# example, the following code:
#
# +--------------------------+-------------------------+-----------------------------------+
# + Python source            + Translated to reST      | Translated to (simplified) HTML   |
# +==========================+=========================+===================================+
# | .. code-block:: Python3  |  .. fenced-code::       | .. code-block:: html              |
# |                          |                         |                                   |
# |  def foo():              |     Beginning fence     |  <pre>def foo():                  |
# |  #      Indented comment |     def foo():          |  Ending fence                     |
# |                          |     Ending fence        |                                   |
# |                          |                         |                                   |
# |                          |        Indented comment |                                   |
# +--------------------------+-------------------------+-----------------------------------+
#
# Notice that the ``Ending fence`` ends up in the resulting HTML! To fix this,
# simply add an unindented `reST comment
# <http://sphinx-doc.org/rest.html#comments>`_ after a block.
#
# +--------------------------+-------------------------+-----------------------------------+
# + Python source            + Translated to reST      | Translated to (simplified) HTML   |
# +==========================+=========================+===================================+
# | .. code-block:: Python3  |  .. fenced-code::       | .. code-block:: html              |
# |                          |                         |                                   |
# |  def foo():              |     Beginning fence     |  <pre>def foo():                  |
# |  #      Indented comment |     def foo():          |  </pre>                           |
# |                          |     Ending fence        |  <blockquote>                     |
# |                          |                         |    Indented comment               |
# |                          |  ..                     |  </blockquote>                    |
# |                          |                         |                                   |
# |                          |        Indented comment |                                   |
# +--------------------------+-------------------------+-----------------------------------+
#
# Mixed code and comments
# ^^^^^^^^^^^^^^^^^^^^^^^
# Note that mixing code and comments is hard: reST will still apply some of
# its parsing rules to an inline code block or inline literal, meaning
# that leading or trailing spaces and backticks will not be preserved,
# instead parsing incorrectly. For example ::
#
#    :code:` Testing `
#
# renders incorrectly. So, mixed lines are simply translated as code, meaning
# reST markup can't be applied to the comments.
#
# .. _summary_and_implementation:
#
# Summary and implementation
# ^^^^^^^^^^^^^^^^^^^^^^^^^^
# This boils down to the following basic rules:
#
# #. Code blocks must be preceded and followed by a removed marker (fences).
#
# #. Comments must be preceded and followed by reST which sets the left
#    margin based on the number of spaces before the comment.
#
# #. Both must be followed by an empty, unindented `reST comment`_.
#
# _generate_rest
# --------------
# Generate reST from the classified code. To do this, create a state machine,
# where current_type defines the state. When the state changes, exit the
# previous state (output a closing fence or closing ``</div>``, then enter the
# new state (output a fenced code block or an opening ``<div style=...>``.
def _generate_rest(
    # An iterable of (type, string) pairs, one per line.
    classified_lines,
    # .. _out_file:
    #
    # A file-like output to which the reST text is written.
    out_file):

    # Keep track of the current type. Begin with a 0-indent comment.
    current_type = -2

    # Keep track of the current line number.
    line = 1

    for type_, string in classified_lines:
        _debug_print('type_ = {}, line = {}, string = {}\n'.format(type_, line, [string]))

        # See if there's a change in state.
        if current_type != type_:
            # Exit the current state.
            _exit_state(current_type, out_file)

            # Enter the new state.
            #
            # Code state: emit the beginning of a fenced block.
            if type_ == -1:
                out_file.write('\n.. fenced-code::\n\n Beginning fence\n')
            # Comment state: emit an opening indent for non-zero indents.
            else:
                # Add an indent if needed.
                if type_ > 0:
                    out_file.write('\n.. raw:: html\n\n'
                      ' <div class="CodeChat-indent" style="margin-left:{}em;">\n\n'.format(0.5*type_))
                # Specify the line number in the source, so that errors will be
                # accurately reported. This isn't necessary in code blocks,
                # since errors can't occur.
                #
                # After this directive, the following text may be indented,
                # which would make it a part of the ``set-line`` directive! So,
                # include an empty comment to terminate the ``set-line``, making
                # any following indents a separate syntactical element. See the
                # end of `reST comment syntax <http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#comments>`_
                # for more discussion.
                out_file.write('\n.. set-line:: {}\n\n..\n\n'.format(line - 4))

        # Output string based on state. All code needs an initial space to
        # place it inside the fenced-code block.
        if type_ == -1:
            out_file.write(' ')
        out_file.write(string)

        # Update the state.
        current_type = type_
        line += 1

    # When done, exit the last state.
    _exit_state(current_type, out_file)


# _exit_state
# ^^^^^^^^^^^
# Output text produced when exiting a state. Supports `_generate_rest`_.
def _exit_state(
    # The type (classification) of the last line.
    type_,
    # See out_file_.
    out_file):

    # Code state: emit an ending fence.
    if type_ == -1:
        out_file.write(' Ending fence\n\n..\n\n')
    # Comment state: emit a closing indent.
    elif type_ > 0:
        out_file.write('\n.. raw:: html\n\n </div>\n\n..\n\n')
    # Initial state. Nothing needed.
    else:
        pass


# Supporting reST directives and roles
# ------------------------------------
# Create a fenced code block: the first and last lines are presumed to be
# fences, which keep the parser from discarding whitespace. Drop these, then
# treat everything else as code.
#
# See the `directive docs
# <http://docutils.sourceforge.net/docs/howto/rst-directives.html>`_ for more
# information.
class _FencedCodeBlock(CodeBlock):
    def run(self):
        # The content must contain at least two lines (the fences).
        if len(self.content) < 2:
            raise self.error('Fenced code block must contain at least two lines.')
        # Remove the fences.
        self.content = self.content[1:-1]
        #
        # By default, the Pygments `stripnl
        # <http://pygments.org/docs/lexers/>`_ option is True, causing Pygments
        # to drop any empty lines. The reST parser converts a line containing
        # only spaces to an empty line, which  will then be stripped by Pygments
        # if these are leading or trailing newlines. So, add a space back in to
        # keep these lines from being dropped.
        #
        # So, first add spaces from the beginning of the lines until we reach
        # the first non-blank line.
        processedAllContent = True
        for i, content in enumerate(self.content):
            if content:
                processedAllContent = False
                break
            self.content[i] = ' '
        # If we've seen all the content, then don't do it again -- we'd be
        # adding unnecessary spaces. Otherwise, walk from the end of the content
        # backwards, adding spaces until the first non-blank line.
        if not processedAllContent:
            for i, _ in enumerate(self.content):
                # Recall Python indexing: while 0 is the first element in a
                # list, -1 is the last element, so offset all indices by -1.
                if self.content[-i - 1]:
                    break
                self.content[-i - 1] = ' '

        # Mark all fenced code with a specific class, for styling.
        self.options['classes'] = ['fenced-code']

        # Now, process the resulting contents as a code block.
        nodeList = CodeBlock.run(self)

        # Sphinx fix: if the current `highlight
        # <http://sphinx-doc.org/markup/code.html>`_ language is ``python``,
        # "Normal Python code is only highlighted if it is parseable" (quoted
        # from the previous link). This means code snippets, such as
        # ``def foo():`` won't be highlighted: Python wants ``def foo(): pass``,
        # for example. To get around this, setting the ``highlight_args`` option
        # "force"=True skips the parsing. I found this in
        # ``Sphinx.highlighting.highlight_block`` (see the ``force`` argument)
        # and in ``Sphinx.writers.html.HTMLWriter.visit_literal_block``, where
        # the ``code-block`` directive (which supports fragments of code, not
        # just parseable code) has ``highlight_args['force'] = True`` set. This
        # should be ignored by docutils, so it's done for both Sphinx and
        # docutils. **Note:** This is based on examining Sphinx 1.3.1 source
        # code.
        #
        # Note that the nodeList returned by the CodeBlock directive contains
        # only a single ``literal_block`` node. The setting should be applied to
        # it.
        nodeList[0]['highlight_args'] = {'force' : True}

        return nodeList


# This directive allows changing the line number at which errors will be
# reported. ``.. set-line:: 10`` makes the current line report as line 10,
# regardless of its actual location in the file.
class _SetLine(Directive):

    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {}
    has_content = False

    def run(self):
        line = int(self.arguments[0])

        # The ``input_lines`` class (see docutils.statemachine.ViewList)
        # maintains two lists, ``data`` and ``items``. ``data`` is a list of
        # strings, one per line, of reST to process. ``items`` is a list of
        # ``(source, offset)`` giving the source of each line and the offset of
        # each line from the beginning of its source. Modifying the offset will
        # change the reported error location.
        il = self.state_machine.input_lines
        # Line renumbering should begin at this offset in ``il.items``, which is
        # the line currently being processed.
        line_offset = self.state_machine.line_offset
        current_source = il.items[line_offset][0]

        # Walk through the current ``input_lines`` up through all its parents.
        while il:
            # Walk from the current line to the end of the current file, rewriting the
            # offset (that is, the effective line number).
            line_ = line
            for index in range(line_offset, len(il.items)):
                source, old_offset = il.items[index]
                # If the source file changes, stop renumbering. The
                # ``current_source`` must have been included; only renumber
                # this, not lines from another source which included
                # ``current_source``.
                if source != current_source:
                    break
                il.items[index] = (source, line_)
                line_ += 1

            # Adjust the offset when moving up to the parent.
            if il.parent:
                line_offset += il.parent_offset
            il = il.parent

        # This directive create no nodes.
        return []


# .. _`_docname_role`:
#
# _docname_role
# ^^^^^^^^^^^^^
# Create a role which returns a specified part of the `docname <http://www.sphinx-doc.org/en/stable/extdev/envapi.html#sphinx.environment.BuildEnvironment.docname>`_ (the path to the current document). Syntax: ``:docname:`attr``` returns the ``attr`` method of the docname as a `Path <https://docs.python.org/3/library/pathlib.html#methods-and-properties>`_. For example, ``:docname:`name``` would return the name of the current docname_.
#
# This function returns a tuple of two values:
#
# 0. A list of nodes which will be inserted into the document tree at the point where the interpreted role was encountered (can be an empty list).
# #. A list of system messages, which will be inserted into the document tree immediately after the end of the current block (can also be empty).
def _docname_role(
    # The local name of the interpreted role, the role name actually used in the document.
    roleName,
    # A string containing the entire interpreted text input, including the role and markup. Return it as a problematic node linked to a system message if a problem is encountered.
    rawtext,
    # The interpreted text content.
    text,
    # The line number where the interpreted text begins.
    lineno,
    # The ``docutils.parsers.rst.states.Inliner`` object that called this function. It contains the several attributes useful for error reporting and document tree access.
    inliner,
    # A dictionary of directive options for customization (from the "role" directive), to be interpreted by this function. Used for additional attributes for the generated elements and other functionality.
    options={},
    # A list of strings, the directive content for customization (from the "role" directive). To be interpreted by the role function.
    content=[]):

    # See https://doughellmann.com/blog/2010/05/09/defining-custom-roles-in-sphinx/.
    env = inliner.document.settings.env
    try:
        # Invoke
        p = Path(env.docname)
        # Return p.<text> using `getattr <https://docs.python.org/3/library/functions.html#getattr>`_.
        path_component = str(getattr(p, text, p))
    except Exception as e:
        # Report an error.
        msg = inliner.reporter.error(
            'Invalid path component {}: {}'.format(text, e), line=lineno
        )
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]
    # Return the path component as text.
    return [nodes.Text(path_component, rawtext, **options)], []


# Register the new directives and role with docutils.
directives.register_directive('fenced-code', _FencedCodeBlock)
directives.register_directive('set-line', _SetLine)
roles.register_local_role('docname', _docname_role)
