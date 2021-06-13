.. Copyright (C) 2012-2020 Bryan A. Jones.

   This file is part of CodeChat.

   CodeChat is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

   CodeChat is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

   You should have received a copy of the GNU General Public License along with CodeChat.  If not, see <http://www.gnu.org/licenses/>.

********
Tutorial
********
This tutorial shows how the `Visual Studio Code <https://code.visualstudio.com/>`_ text editor, integrated with the `CodeChat extension <https://marketplace.visualstudio.com/items?itemName=CodeChat.codechat>`_, provides a powerful environment for creating expressive programs.

.. contents:: Contents
    :local:


Basic restructuredText
======================
CodeChat relies on `reStructuredText <http://docutils.sourceforge.net/rst.html>`_ (`reST <http://docutils.sourceforge.net/rst.html>`_) in comments to provide human-readable markup. "ReStructuredText is an easy-to-read, what-you-see-is-what-you-get plaintext markup syntax" [#]_. So, this tutorial begins by exploring reST_ using the CodeChat System.

First, `install and run <https://codechat-system.readthedocs.io/en/latest/CodeChat_Server/contents.html#installation>`_ the CodeChat Server and install the `Visual Studio Code`_ `CodeChat extension`_. Next, download the `the CodeChat reST tutorial <https://raw.githubusercontent.com/bjones1/CodeChat/master/docs/rest-primer.rst>`_. Open this file in Visual Studio Code, then `open CodeChat <use codechat>`. Edit the text -- your changes are visible immediately.

Now, explore creating your own reST_ file: create a new file, then save it with an extension of ``.rst``. Based on the very helpful `reST primer <http://sphinx-doc.org/rest.html>`_, try out some syntax: create headings, include a hyperlink, add an image, use inline markup. When errors occur, they are reported in the log window and in-line in the resulting web page.

.. [#] http://docutils.sourceforge.net/rst.html


Basic CodeChat
==============
Based on your familiarity with reST_, we'll now explore embedding reST_ in the comments of a program. To do this, download and open `CodeChat's setup.py <https://raw.githubusercontent.com/bjones1/CodeChat/master/setup.py>`_. Note the format used for comments that will be rendered using reST_:

#.  A comment must be placed on a line containing only comments or whitespace, but no code, preprocessor directives, etc.
#.  One space must follow the opening comment delimiter.

The :doc:`style_guide.cpp` gives more details; see :doc:`/CodeChat/CommentDelimiterInfo.py` for a full list of supported languages.

Now, open one of your source files. Modify your comments to add reST_ markup; add in titles, hyperlinks, and other useful markup.

While basic CodeChat usage shown here provides a quick way to begin experimenting with literate programming, it's limited in several ways. First, because it uses basic reST_, CodeChat lacks the ability to create a web of documentation over multiple source files in a project. Second, the web page produced by CodeChat must be manually saved to disk for others to view, an inefficient process when providing documentation to others. Finally, the results are rather plain. We therefore turn to Sphinx to remedy all these problems.


Sphinx_
========
"`Sphinx <http://sphinx-doc.org/index.html>`_ is a tool that makes it easy to create intelligent and beautiful documentation" [#]_. It provides additional features lacking basic reStructuredText_, including the ability to link together many documents (such as all the files in a program's source code).

To use Sphinx with the CodeChat system, first download and unzip the `source code for CodeChat <https://github.com/bjones1/CodeChat/archive/master.zip>`_, which provides a example Sphinx project. Open ``README.rst`` from the unzipped files; the CodeChat system will render the project. Most of the files in this project will render. Make a few edits; note that you must save the file before the render takes place. Open a source file and make a few edits, again saving to render the edits.

In addition to providing a number of beautiful themes for rendering reST_ files, Sphinx creates a set of linked documents. To see this in action, open :file:`{location of unzipped CodeChat files}/index.rst`. This file determines the hierarchical `document structure <http://sphinx-doc.org/markup/toctree.html>`_. For example, the following markup includes headings from ``README.rst`` into ``index.rst``::

    .. toctree::
        :maxdepth: 2

        README.rst

One important note: when referring to files in subdirectories, a forward slash **MUST** be used, even on Windows. That is, use ``CodeChat/filename``, not ``CodeChat\filename``. Sphinx supports many other `markup constructs <http://sphinx-doc.org/markup/index.html>`_ as well.

Creating a new Sphinx project
=============================
To create a new Sphinx project, copy the files in the `Sphinx template directory <https://github.com/bjones1/CodeChat/tree/master/CodeChat/sphinx_template>`_, available from :file:`{location of unzipped CodeChat files}/CodeChat/sphinx_template`, to a new directory. Open the file ``index.rst`` in this new directory; the new project is ready and will render.

Next, create a new file and save it with the ``.rst`` extension in the empty directory you created. Add some content to this file, including at least one heading, but notice that it generates a warning in the log window. To fix this, include it in your Sphinx project: in ``index.rst`` add it to your ``toctree`` directive. Assuming the name of the file you created was ``demo.rst``, the syntax is::

    .. toctree::
        :maxdepth: 2

        demo.rst

When you switch back to ``demo.rst``, it will now be included in your project.

.. [#] http://sphinx-doc.org/index.html


Reference
=========
With a basic knowledge of this literate programming system, the following pages provide helpful reference information.

*   The :doc:`style guide <style_guide.cpp>` for literate programming. Read this first.
*   For basic reST_ syntax, see the `reST primer`_.
*   For additional Sphinx-specific commands, refer to `markup constructs`_.

Also, refer to the :ref:`tutorial-examples` to see some of the ways in which CodeChat helps create beautiful programs.
