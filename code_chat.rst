.. Copyright (C) 2012-2013 Bryan A. Jones.

   This file is part of CodeChat.

   CodeChat is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

   CodeChat is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

   You should have received a copy of the GNU General Public License along with CodeChat.  If not, see <http://www.gnu.org/licenses/>.

***********************
CodeChat implementation
***********************
Author: Bryan A. Jones <bjones AT ece DOT msstate DOT edu>

The :doc:`user manual <../README>` gives a broad overview of this system. In contrast, this document discusses the implementation specifics of the CodeChat system; it also runs the CodeChat application iteslf.

.. contents:: Table of Contents
   :local:
   :depth: 1

CodeChat application
====================
CodeChat provides two largely separate core functions. First, it presents a GUI to the user, enabling editing of source code, display of the resulting web page, and synchronization between the two. Second, it invokes a code to web backend as necessary so that the resulting web pages reflect the code.

In particular, :doc:`CodeChat.py <CodeChat/CodeChat.py>` implements the GUI, relying on :doc:`CodeChatUtils.py <CodeChat/CodeChatUtils.py>` for some supporting functionality and employing :doc:`FindLongestMatchingString.py <CodeChat/FindLongestMatchingString.py>` for the text matching underly web to code synchronization. `Sphinx <http://sphinx-doc.org/>`_, run in a separate process by :doc:`MultiprocessingSphinx.py <CodeChat/MultiprocessingSphinx.py>`, invokes the :doc:`CodeToRest.py <CodeChat/CodeToRest.py>` extension (which is specified in the Sphinx configuration file :doc:`conf.py <conf.py>`) to transform code into restructured text (the syntax Sphinx_ employs for markup), then produces web pages based on this input.

.. toctree::
   :maxdepth: 1

   code_chat.py
   CodeChat/CodeChat.py
   CodeChat/CodeChatUtils.py
   CodeChat/MultiprocessingSphinx.py
   CodeChat/FindLongestMatchingString.py
   CodeChat/CodeToRest.py
   CodeChat/LanguageSpecificOptions.py
   CodeChat/version.py
   conf.py


Unit testing
------------
The following modules perform unit tests on portions of the application.

.. toctree::
   :maxdepth: 1

   CodeChat/CodeChatUtils_test.py
   CodeChat/FindLongestMatchingString_test.py
   CodeChat/CodeToRest_test.py
   CodeChat/pytest.ini


.. _build_system:

Build system
============
The build system provides the ability to package this program into a self-contained executable then publish it on the web. In particular, :doc:`build_exe.bat <build_exe.bat>` transforms the Python code into a binary. After this succeeds, :doc:`build_dist.bat <build_dist.bat>` packages this binary, along with supporting files (docs, template, source code, etc.) into a single executable, which is then published (along with docs) to the web via a public Dropbox share. Core components:

.. toctree::
   :maxdepth: 1

   build_exe.bat
   build_dist.bat
   CodeChat.iss
