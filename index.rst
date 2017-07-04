.. Copyright (C) 2012-2016 Bryan A. Jones.

   This file is part of CodeChat.

   CodeChat is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

   CodeChat is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

   You should have received a copy of the GNU General Public License along with CodeChat.  If not, see <http://www.gnu.org/licenses/>.

@@@@@@@@@@@@@@@@@@@@@@@@@@@@
CodeChat's table of contents
@@@@@@@@@@@@@@@@@@@@@@@@@@@@
Welcome to CodeChat's documentation! For new users, begin by reading :doc:`README`. For others, documentation for this program is divided into the following two sections.

##################
User documentation
##################
.. toctree::
   :maxdepth: 2

   README.rst
   docs/tutorial.rst
   docs/rest-primer.rst
   docs/style_guide.cpp
   docs/install.rst

**********************
Template documentation
**********************
The following shows the documentation produced by a template CodeChat project.

.. toctree::
   :maxdepth: 2

   CodeChat/template/index.rst

#######################
Developer documentation
#######################
.. toctree::
   :maxdepth: 2

   CodeChat/__init__.py
   CodeChat/CodeToRest.py
   CodeChat/RestToCode.py
   CodeChat/CodeToRestSphinx.py
   CodeChat/CommentDelimiterInfo.py
   docs/history.rst

*******
Testing
*******
.. toctree::
   :maxdepth: 2

   test/pytest.ini
   test/CodeToRest_test.py
   test/RestToCode_test.py
   .travis.yml
   appveyor.yml

************************
Documentation generation
************************
.. toctree::
   :maxdepth: 2

   conf.py
   CodeChat.css

*********
Packaging
*********
.. toctree::
   :maxdepth: 2

   setup.py
   MANIFEST.in
   Linux_packaging/python-codechat.spec

################
Index and search
################
* :ref:`genindex`
* :ref:`search`

