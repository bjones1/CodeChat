.. Copyright (C) 2012-2015 Bryan A. Jones.

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
   CodeChat/template/index.rst
   CodeChat/template/conf.py
   CodeChat/template/CodeChat.css

#######################
Developer documentation
#######################
.. toctree::
   :maxdepth: 2

   docs/history.rst
   CodeChat/CodeToRest.py
   CodeChat/CodeToRestSphinx.py
   CodeChat/CommentDelimiterInfo.py
   CodeChat/__init__.py

*******
Testing
*******
.. toctree::
   :maxdepth: 2

   CodeChat/CodeToRest_test.py

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

################
Index and search
################
* :ref:`genindex`
* :ref:`search`

.. Ignore the following files. They're linked to elsewhere.

.. toctree::
   :hidden:

   CodeChat/LICENSE.html
