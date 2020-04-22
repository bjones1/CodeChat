.. Copyright (C) 2012-2020 Bryan A. Jones.

   This file is part of CodeChat.

   CodeChat is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

   CodeChat is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

   You should have received a copy of the GNU General Public License along with CodeChat.  If not, see <http://www.gnu.org/licenses/>.

****************************
CodeChat's table of contents
****************************
Welcome to CodeChat's documentation! For new users, begin by reading :doc:`README`. For others, documentation for this program is divided into the following two sections.

User documentation
==================
.. toctree::
   :maxdepth: 2

   README.rst
   docs/tutorial.rst
   docs/rest-primer.rst
   docs/style_guide.cpp
   docs/style_guide.md.cpp
   docs/install.rst
   docs/reference_manual.rst
   docs/history.rst


Template documentation
----------------------
The following shows the documentation produced by a CodeChat project template. It also presents the style sheets used for CodeChat webpages.

.. toctree::
   :maxdepth: 2

   CodeChat/sphinx_template/index.rst
   CodeChat/css/CodeChat.css
   CodeChat/css/CodeChat_default.css


Developer documentation
=======================
.. toctree::
   :maxdepth: 2

   CodeChat/__init__.py
   CodeChat/SourceClassifier.py
   CodeChat/CodeToRest.py
   CodeChat/CodeToMarkdown.py
   CodeChat/RestToCode.py
   CodeChat/CodeToRestSphinx.py
   CodeChat/CommentDelimiterInfo.py
   .gitignore


Testing
-------
To run the tests, execute ``pytest test`` from the root directory of the project.

.. toctree::
   :maxdepth: 2

   test/CodeToRest_test.py
   test/CodeToMarkdown_test.py
   test/RestToCode_test.py
   test/HtmlToCode_test.py
   .travis.yml
   appveyor.yml
   docs/style_test.py


Documentation generation
------------------------
To build the documentation, execute ``sphinx-build -d _build\doctrees . _build`` from the root directory of the project.

.. toctree::
   :maxdepth: 2

   conf.py
   readthedocs.yml


Packaging
---------
.. toctree::
   :maxdepth: 2

   setup.py
   MANIFEST.in


Search
======
* :ref:`search`
