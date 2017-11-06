.. Copyright (C) 2012-2017 Bryan A. Jones.

    This file is part of CodeChat.

    CodeChat is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    CodeChat is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with CodeChat.  If not, see <http://www.gnu.org/licenses/>.

*****************************
A programmer's word processor
*****************************
`CodeChat <http://codechat.readthedocs.io/en/latest/README.html>`_ transforms source code into a web page, allowing developers to view their program as a beautiful and descriptive document by adding headings, formatting, hyperlinks, diagrams, images, and other forms of rich content to capture the ideas and insights that naturally flow from the process of writing a program. It also provides a blank slate in which to plan ahead, by sketching out an algorithm before committing it to code or laying out a design document which can evolve as the code does. This `literate programming <http://www.literateprogramming.com/>`_ paradigm changes the way developers think by intermingling ideas with their implementation as code, dramatically improving a programmer’s abilities.

.. Note that hyperlinks don't use the typical :doc: syntax here, because:

    1. This same file will be processed by reST-only tools on the GitHub and PyPI pages, so :doc: will produce errors.

    2. Pointing to the doc homepage causes GitHub and PyPI links to automatically refer users to the full documentation set, rather than the single file (this one) hosted automatically there.

.. The following includes a YouTube CodeChat playlist.

.. raw:: html

    <iframe width="853" height="480" src="https://www.youtube.com/embed/videoseries?list=PLOJAqFa3UI2EmpUOy7PhAJ7adRnBZkC6U" frameborder="0" allowfullscreen></iframe>

Installation
============
See the `installation intructions <http://codechat.readthedocs.io/en/latest/docs/install.html>`_.


Background
==========
Put simply, literate programming (LP) is the realization that a program is a document written to and for fellow programmers, not simply a list of instructions for a computer. LP tools therefore produce a nicely-formatted document which contains the code intermixed with explanatory prose. `Donald Knuth <http://en.wikipedia.org/wiki/Donald_Knuth>`_ introducted literate programming using his WEB tool in his seminal `paper <http://www.literateprogramming.com/knuthweb.pdf>`_. Per Figure 1 of this paper_, the WEB system takes a ``.w`` document as input then produces either a "tangled" source file for compilation or a "woven" document as a ``.tex`` file. The document is beautiful; the WEB source is difficult to digest (see Figure 2a-c); the source code is completely unreadable (see Figure 3). While a plethora of `tools <http://en.wikipedia.org/wiki/Literate_programming#Tools>`_ developed over the years attempt to address these problems, only one `LP-inspired <http://rant.gulbrandsen.priv.no/udoc/history>`_ variant has gained widespread acceptance: documentation generators, such as `Doxygen <http://www.doxygen.org>`_ and `JavaDoc <http://www.oracle.com/technetwork/java/javase/documentation/index-jsp-135444.html>`_, which extract documentation directly from source code, rather than extracting source code from the documentation, as WEB and most LP tools do. CodeChat addresses these LP weaknesses by producing a doucment directly from the code; employing human-readable markup (reStructuredText); and by supporting a GUI to make editing an LP document-program faster and easier.


Tutorial
========
The `CodeChat tutorial <http://codechat.readthedocs.io/en/latest/docs/tutorial.html>`_ guides new users into exploring CodeChat's literate programming abilities. Start here! Or, peruse the examples below to see the ways in which CodeChat transforms plain source code into beautiful documents.


.. _tutorial-examples:

Examples
========
Some examples of literate programming using CodeChat:

*   Use of a ``toctree`` directive to categorize all source files in `CodeChat itself <http://codechat.readthedocs.io/en/latest/>`_
*   Use of tables to help design a `simple parser <http://codechat.readthedocs.io/en/latest/CodeChat/CodeToRest.py.html#step-5-of-lexer-to-rest>`_.
*   Use of a numbered list to explain a `simple state machine <http://codechat.readthedocs.io/en/latest/CodeChat/CodeToRest.py.html#summary-and-implementation>`_.
*   Use of hyperlinks to provide reference information for all `Sphinx configuration values <http://codechat.readthedocs.io/en/latest/conf.py.html>`_.
*   Use of fonts to show what ``setup.py`` `commands to run <http://codechat.readthedocs.io/en/latest/setup.py.html>`_
*   Use of a screenshot to demonstrate the operation of a `3-D simulation <https://dl.dropboxusercontent.com/u/2337351/CodeChat_MAVs/homework_1_solution.html>`_.
*   Use of equations and diagrams in `scientific computing <https://dl.dropboxusercontent.com/u/2337351/CodeChat_MAVs/mav3d_simulation.html#dynamics>`_.
*   Use of equations to explain the resulting code for an `integrator <https://dl.dropboxusercontent.com/u/2337351/CodeChat_MAVs/integrating_omega_3d.html>`_.
*   CodeChat is used for code examples in a course on `microprocessors <http://www.ece.msstate.edu/courses/ece3724/main_pic24/docs/sphinx/textbook_examples.html>`_.


Contributing
============
This is a fairly basic implementation; much improvement is needed! Please use the `issue tracker <https://github.com/bjones1/CodeChat/issues>`_ to report bugs or request features; even better, contribute to the `code <https://github.com/bjones1/CodeChat>`_!


License
=======
Copyright (C) 2012-2017 Bryan A. Jones.

This file is part of CodeChat.

CodeChat is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

CodeChat is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a `copy of the GNU General Public License <CodeChat/LICENSE.html>`_ along with CodeChat.  If not, see http://www.gnu.org/licenses/.
