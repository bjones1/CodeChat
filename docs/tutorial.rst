.. Copyright (C) 2012-2015 Bryan A. Jones.

   This file is part of CodeChat.

   CodeChat is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

   CodeChat is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

   You should have received a copy of the GNU General Public License along with CodeChat.  If not, see <http://www.gnu.org/licenses/>.

********
Tutorial
********
This tutorial shows how the `Enki <http://enki-editor.org/>`_ text editor, integrated with the CodeChat literate programming plug-in, provides a powerful environment for creating expressive programs.

.. contents:: Contents
   :local:

The following playlist covers all the topics in this tutorial.

.. raw:: html

   <iframe width="853" height="480" src="https://www.youtube.com/embed/videoseries?list=PLOJAqFa3UI2EmpUOy7PhAJ7adRnBZkC6U" frameborder="0" allowfullscreen></iframe>

This tutorial employs the following typography:

* :file:`This font` for the name of a file or directory;
* :guilabel:`This font` for labels in the GUI; and
* :menuselection:`This font` for menu selections.

Basic restructuredText
======================
CodeChat relies on `reStructuredText <http://docutils.sourceforge.net/rst.html>`_ (`reST <http://docutils.sourceforge.net/rst.html>`_) in comments to provide human-readable markup. "ReStructuredText is an easy-to-read, what-you-see-is-what-you-get plaintext markup syntax" [#]_. So, this tutorial begins by exploring reST_ using Enki.

First, install Enki_, which hosts the CodeChat system. Next, download the `source code for CodeChat <https://github.com/bjones1/CodeChat/archive/master.zip>`_, which also contains a :doc:`rest-primer` needed in this tutorial. Unzip this file in a directory of your choice. Now, open :file:`{location of unzipped CodeChat files}/docs/rest-primer.rst` in Enki. Move around the document, noticing that the text and web views are automatically synchronized [#]_. Click on any element of the web view to show the corresponding text view. Edit -- your changes are visible immediately. Note that the syncronization ability applies to any file Enki can preview, such as HTML files (try :file:`{location of unzipped CodeChat files}/CodeChat/LICENSE.html`, for exampe, or Enki's `README.md <https://raw.githubusercontent.com/hlamer/enki/master/README.md>`_).

Now, explore creating your own reST_ file: create a new file, then save it with an extension of ``.rst``. Based on the very helpful `reST primer <http://sphinx-doc.org/rest.html>`_, try out some syntax: create headings, include a hyperlink, add an image, use inline markup. When errors occur, they are reported in the log window and typically in-line in the resulting web page. When a page is complete, the save icon in the preview window stores the resulting HTML to disk.

By design, reST_ operates on one file at a time. To create a web site consisting of multiple, interlinked documents, we turn to Sphinx, wihch adds this ability to reStructuredText_.

.. [#] http://docutils.sourceforge.net/rst.html

.. [#] Assuming TRE is installed. Follow the `TRE build instructions <https://github.com/bjones1/tre/blob/master/INSTALL.rst>`_ if not.

Basic Sphinx_
=============
"`Sphinx <http://sphinx-doc.org/index.html>`_ is a tool that makes it easy to create intelligent and beautiful documentation" [#]_. It provides additional features lacking basic reStructuredText_, including the ability to link together many documents (such as all the files in a program's source code).

To use Sphinx with Enki_, first go to :menuselection:`Settings --> Settings --> Sphinx`. Then enable Sphinx and select :file:`{location of unzipped CodeChat files}` as the project directory. Click OK. Then, open :file:`{location of unzipped CodeChat files}/README.rst`. The resulting web page will be displayed in the Preview dock.

In addition to providing a number of beautiful themes for rendering reST_ files, Sphinx creates a set of linked documents. To see this in action, open :file:`{location of unzipped CodeChat files}/index.rst`. This file determines the hierarchical `document structure <http://sphinx-doc.org/markup/toctree.html>`_. For example, the following markup includes headings from ``README.rst`` into ``index.rst``::

   .. toctree::
      :maxdepth: 2

      README.rst

One important note: when refering to files in subdirectories, a forward slash **MUST** be used, even on Windows. That is, use ``CodeChat/filename``, not ``CodeChat\filename``. Sphinx supports many other `markup constructs <http://sphinx-doc.org/markup/index.html>`_ as well.

Creating a new project
----------------------
To create a new Sphinx project, first create an empty directory to hold your project's files. In :menuselection:`Settings --> Settings --> Sphinx`, select this directory as the project directory then click OK. In :menuselection:`Settings --> Settings --> Literate programming`, **uncheck** :guilabel:`Enable CodeChat`; otherwise, Enki will create not just a Sphinx project, but a CodeChat-enabled Sphinx project. Next, create a new file and save it with the ``.rst`` extension in the empty directory you created. A dialog box will pop up, asking if you'd like some default files copied. Click yes. Open the generated ``index.rst`` file. Add some content to this file, including at least one heading, but notice that it generates a warning in the log window. To fix this, include it in your Sphinx project: in ``index.rst`` add it to your ``toctree`` directive. Assuming the name of the file you created was ``demo.rst``, the syntax is::

   .. toctree::
      :maxdepth: 2

      demo.rst

When you switch back to ``demo.rst``, it will now be included in your project.

.. [#] http://sphinx-doc.org/index.html

Basic CodeChat
==============
Based on your familiarity with reST_, we'll now explore embedding reST_ in the comments of a program. First, enable CodeChat in Enki's :menuselection:`Settings --> Settings --> Literate Programming` dialog by checking the "Enable CodeChat" checkbox. In :menuselection:`Settings --> Settings --> Sphinx`, uncheck the :guilabel:`Enable Sphinx` checkbox. Now, open :file:`{location of unzipped CodeChat files}/setup.py`. Notice that reST_ markup, when correctly embedded in comments, renders properly. Specifically, to be rendered using reST_:

#. A comment must be placed on a line containing only comments or whitespace, but no code, preprocessor directives, etc.
#. One space must follow the opening comment delimiter.

The :doc:`style_guide.cpp` gives more details; also, see :doc:`/CodeChat/CommentDelimiterInfo.py` for a full list of supported languages.

Now, open one of your source files. Modify your comments to add reST_ markup; add in titles, hyperlinks, and other useful markup.

While basic CodeChat usage shown here provides a quick way to begin experimenting with literate programming, it's limited in several ways. First, because it uses basic reST_, CodeChat lacks the ability to create a web of documentation over multiple source files in a project. Second, the web page produced by CodeChat must be manually saved to disk for others to view, an inefficient process when providing documentation to others. Finally, the results are rather plain. We therefore turn to Sphinx to remedy all these problems.

Basic Sphinx with CodeChat
==========================
Now, combining Sphinx with CodeChat enables the use of the literate programming paradigm applied to all source and accompanying documentation in a project. To see this in action, in :menuselection:`Settings --> Settings --> Sphinx` enable Sphinx; make sure the project directory is :file:`{location of unzipped CodeChat files}/`. Now, open or switch to :file:`{location of unzipped CodeChat files}/setup.py`. Note that the source code is rendered to HTML for this file and for all source and documentation files in the CodeChat project.

Now, create a new Sphinx with CodeChat project. First, choose a directory in which source files you'd like to document reside. In :menuselection:`Settings --> Settings --> Sphinx`, select this direectory. After pressing OK, Enki will ask if you'd like to add the necessary template files; click OK. These files are different than the Sphinx-only template files from earlier, since both Sphinx and CodeChat are enabled. Now, transform your program into a document by adding titles, hyperlinks, etc. Explore the ``conf.py`` file, added as a template, to customize the output for your needs.

Reference
=========
With a basic knowledge of this literate programming system, the following pages provide helpful reference information.

* The :doc:`style guide <style_guide.cpp>` for literate programming. Read this first.
* For basic reST_ syntax, see the `reST primer`_.
* For additional Sphinx-specific commands, refer to `markup constructs`_.

Also, refer to the :ref:`tutorial-examples` to see some of the ways in which CodeChat helps create beautiful programs.
