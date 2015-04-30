*****************************
A programmer's word processor
*****************************

`CodeChat <https://bitbucket.org/bjones/documentation/overview>`_ transforms source code into a web page, allowing developers to view their program as a beautiful and descriptive document by adding headings, formatting, hyperlinks, diagrams, images, and other forms of rich content to capture the ideas and insights that naturally flow from the process of writing a program. It also provides a blank slate in which to plan ahead, by sketching out an algorithm before committing it to code or laying out a design document which can evolve as the code does. This `literate programming <http://www.literateprogramming.com/>`_ paradigm changes the way developers think by intermingling ideas with their implementation as code, dramatically improving a programmer’s abilities.

.. contents::
   :local:

Tutorial
========
This tutorial shows how the `Enki <http://enki-editor.org/>`_ text editor, integrated with the CodeChat_ literate programming plug-in, provides a powerful environment for creating expressive programs.

Basic restructuredText
----------------------
CodeChat relies on `reStructuredText <http://docutils.sourceforge.net/rst.html>`_ (`reST <http://docutils.sourceforge.net/rst.html>`_) in comments to provide human-readable markup. "ReStructuredText is an easy-to-read, what-you-see-is-what-you-get plaintext markup syntax" [#]_. So, this tutorial beings by exploring reST using Enki.

First, install Enki_, which hosts the CodeChat_ system. Next, download the `source code for CodeChat <https://bitbucket.org/bjones/documentation/downloads>`_, then unzip this in a directory of your choice. Now, open the source for this document, ``<location of unzipped CodeChat files>/README.rst``, in Enki. Move around the document, noticing that the text and web view are automatically synchronized. Click on any element of the web view to show the corresponding text view. Edit -- your changes are visible immediately. Note that the syncronization ability applies to any file Enki can preview, such as HTML files (try ``<location of unzipped CodeChat files>/CodeChat/LICENSE.html``, for exampe, or Enki's `README.md <https://raw.githubusercontent.com/hlamer/enki/master/README.md>`_).

Now, explore creating your own reST file: create a new file, then save it with an extension of ``.rst``. Based on the very helpful `reST primer <http://sphinx-doc.org/rest.html>`_, try out some syntax: create headings, include a hyperlink, add an image, use inline markup. When errors occur, they are reported in the log window and typically in-line in the resulting web page. When a page is complete, the save icon in the preview window stores the results to disk.

.. [#] http://docutils.sourceforge.net/rst.html

Basic CodeChat
--------------
Based on your familiarity with reST, we'll now explore embedding reST in the comments of a program. First, enable CodeChat in Enki's Settings | Settings | Literate Programming dialog by checking the "Enable CodeChat" checkbox. Now, open ``<location of unzipped CodeChat files>/setup.py``. Notice that reST constructs when correctly embedded in comments render properly. Specifically, to be rendered using reST, a comment must:

#. Be a single-line comment; in C, ``/*`` and ``*/`` cannot be used.
#. Be the only non-whitespace characters on the line -- code cannot preceed the comment.
#. Have at least one space following the comment character(s) -- tabs don't work.

For example, in *C* or *C++*:

+-----------------------------------------------------------+-----------------------------------------------------------+
+ Source code                                               + CodeChat results                                          +
+===========================================================+===========================================================+
| .. code:: c                                               | ReST_ works *here*.                                       |
|                                                           |                                                           |
|    // ReST_ works *here*.                                 | .. code:: c                                               |
|    //But not here -- a space must follow the comment.     |                                                           |
|    /* Not here either. Only single-line comments work. */ |    //But not here -- a space must follow the comment.     |
|    a = 1; // Not here either. Comments must be on a       |    /* Not here either. Only single-line comments work. */ |
|    b = 2; // separate line, not following code.           |    a = 1; // Not here either. Comments must be on a       |
|                                                           |    b = 2; // separate line, not following code.           |
+-----------------------------------------------------------+-----------------------------------------------------------+

Currently, only single-line comments in C/C++, Python, reST, assembly (.s), BASH scripts, PHP, MATLAB scripts, DOS batch (.bat) files, .ini, and .iss files are supported.

Basic Sphinx_
-------------
"`Sphinx <http://sphinx-doc.org/index.html>`_ is a tool that makes it easy to create intelligent and beautiful documentation" [#]_. It provides additional features, including the ability to link together many documents (such as all the files in a program's source code).

To use Sphinx with Enki_, first go to ``Settings | Settings | Documentation generators``. Then enable Sphinx and select ``<location of unzipped CodeChat files>`` as the project directory. Click OK. Then, open ``<location of unzipped CodeChat files>/README.rst``, or switch to it if it's still open. The resulting web page will be displayed in the Preview dock.

In addition to providing a number of beautiful themes for rendering reST files, Sphinx creates a set of linked documents. To see this in action, open ``<location of unzipped CodeChat files>/index.rst``. This file determines the hierarchical `document structure <http://sphinx-doc.org/markup/toctree.html>`_. For example, the following markup includes headings from ``README.rst`` into ``index.rst``::

   .. toctree::
      :maxdepth: 2

      README


One important note: when refering to files in subdirectories, a forward slash **MUST** be used, even on Windows. That is, use ``CodeChat/filename``, not ``CodeChat\filename``. Sphinx supports many other `markup constructs <http://sphinx-doc.org/markup/index.html>`_ as well.

Creating a new project
^^^^^^^^^^^^^^^^^^^^^^
To create a new Sphinx project, first create an empty directory to hold your project's files. In ``Settings | Settings | Documentation generators``, select this directory as the project directory then click OK. A dialog box will pop up, asking if you'd like some default files copied. Click yes. Open the generated ``index.rst`` file. To add a file to your project, use ``File | New`` in Enki to create a new file, then save it as ``README.rst``. Generate some content in README.rst, including at least one heading, but notice that it isn't being rendered. To fix this, include it in your Sphinx project: in ``index.rst``, add it to your ``toctree`` directive::

   .. toctree::
      :maxdepth: 2

      README

When you switch back to ``README.rst``, it will now be rendered and included in your project.

.. [#] http://sphinx-doc.org/index.html

Basic Sphinx with CodeChat
--------------------------
Now, combining Sphinx with CodeChat enables the use of the literate programming paradigm applied to all source and accompanying documentation in a file.

Contributing
============
This is a fairly basic implementation; much improvement is needed! Please use the `issue tracker <http://bitbucket.org/bjones/documentation/issues?status=new&status=open>`_ to report bugs or request features; even better, or contribute to the code at the CodeChat_ homepage!

Recent changes
==============
- Development version:

   - Update setup.py based on modern usage.
   - Update docs.
   - Add support for Sphinx v1.3.
   - Creation of a tutorial.

- 0.0.18, 11-Feb-2015:

   - Remove unused PyQt dependencies.
   - Modernize documentation style in ``LanguageSpecificOptions.py``.

- 0.0.17, 17-Nov-2014:

   - Support Sphinx versions before 1.2.
   - Move non-CodeChat templates to Enki.

- 0.0.16 - 0.0.13, 11-Nov-2014:

   - Improved Sphinx template: doesn't replace default.css.
   - Updated CSS to work better with docutils.

- 0.0.12, released 1-Sep-2014:

   - Fixes so that CodeChat's Sphinx extension now works.
   - File encoding can now be specified.
   - Installaiton instructions added and docs reworked.

- 0.0.11, released 1-May-2014:

   - Fixed Unicode errors.
   - Removed incorrect extra spacing between code and comments.
   - Fixed unit tests and added a few more.
   - Removed unused CodeLink directive.

- 0.0.10, released 17-Apr-2014:

   - Revamped packaging.
   - Updated docs.
   - Used ``..`` instead of marker to indent comments, producing cleaner ReST.
   - Split ``CodeToRest`` into ``CodeToRest``, ``CodeToRestSphinx`` modules.

License
=======
Copyright (C) 2012-2015 Bryan A. Jones.

This file is part of CodeChat.

CodeChat is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

CodeChat is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with CodeChat.  If not, see <http://www.gnu.org/licenses/>.
