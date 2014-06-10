***************************************
CodeChat, a programmer's word processor
***************************************
Welcome to `CodeChat <https://bitbucket.org/bjones/documentation/overview>`_, a programmer's word processor. CodeChat_ encourages `literate programming <http://www.literateprogramming.com/>`_ by transforming source files into web pages and by providing a powerful editor which synchronizes between the source code view and the web view of a document. CodeChat_ transforms plain-text source code into a beautiful and descriptive document, allowing you to record your ideas, helpful hyperlinks to on-line resources, include expressive images and diagrams, and much more.

.. contents::

Installation
============
First, `install <https://pip.pypa.io/en/latest/installing.html>`_
`pip <https://pip.pypa.io/en/latest/index.html#>`_ if you
don't yet have it. Then, from a command prompt, run ``pip install -U CodeChat``.
The `-U flag <https://pip.pypa.io/en/latest/reference/pip_install.html#cmdoption-U>`_
upgrades CodeChat to the latest version if it's already installed.

Next install `Enki <http://enki-editor.org/>`_, which hosts the CodeChat system.

Use
===
Open some source code of a supported format [#]_. In the ``Settings | Settings | CodeChat`` panel, click ``Enable`` then ``OK``. Now, any properly-formatted comments will be interpreted as ReST_. For example:

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

Sphinx_
-------
"Sphinx is a tool that makes it easy to create intelligent and beautiful documentation" [#]_. It provides additional features, including the ability to link together many documents (such as all the files in a program's source code). Enki_ will soon support Sphinx.

.. [#] Currently, only single-line comments in C/C++, Python, reST, assembly (.s), BASH scripts, PHP, MATLAB scripts, DOS batch (.bat) files, .ini, and .iss files are supported.
.. [#] http://sphinx-doc.org/index.html

ReST
----
"reStructuredText is an easy-to-read, what-you-see-is-what-you-get plaintext markup syntax" [#]_. Helpful pages:

* The excellent `reStructuredText primer <http://sphinx-doc.org/rest.html>`_ provided by the `Sphinx <http://sphinx-doc.org/index.html>`_ project.
* A longer `Quick reStructuredText <http://docutils.sourceforge.net/docs/user/rst/quickref.html>`_ guide.

.. [#] http://docutils.sourceforge.net/rst.html

Contributing
============
This is a fairly basic implementation; much improvement is needed! Please use the `issue tracker <http://bitbucket.org/bjones/documentation/issues?status=new&status=open>`_ to report bugs or request features; even better, or contribute to the code at the CodeChat_ homepage!

Recent changes
==============
- 0.0.12, not yet released:

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
Copyright (C) 2012-2014 Bryan A. Jones.

This file is part of CodeChat.

CodeChat is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

CodeChat is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with CodeChat.  If not, see <http://www.gnu.org/licenses/>.
