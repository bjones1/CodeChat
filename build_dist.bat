: .. Copyright (C) 2012-2013 Bryan A. Jones.
:
:    This file is part of CodeChat.
:
:    CodeChat is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
:
:    CodeChat is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
:
:    You should have received a copy of the GNU General Public License along with CodeChat.  If not, see <http://www.gnu.org/licenses/>.
:
:
: .. highlight:: BatchLexer
:
: ***************************************************************************
: build_dist.bat - Package the executable and source then publish to the web.
: ***************************************************************************
: Package creation
: ================
: This script makes use of several DOS commands with flags. A quick reference:
:
: For ``rmdir``:
:
: /S      Removes all directories and files in the specified directory in addition to the directory itself.  Used to remove a directory tree.
: /Q      Quiet mode, do not ask if ok to remove a directory tree with /S
:
: For ``xcopy``:
:
: /E           Copies directories and subdirectories, including empty ones.
: /I           If destination does not exist and copying more than one file, assumes that destination must be a directory.
:
: Gather files
: ------------
: First, this script gathers the following components needed to create a package.
:
: **Note:** this should only by run after a successfull execution of :doc:`build_exe.bat <build_exe.bat>`, which creates the executable. The documentation should be update to date (a successful run on the executable does this) and Mercurial should have all changes committed.
:
: ==============   ========================   ======================
: Component        Source                     Dest
: ==============   ========================   ======================
: The executable   ``dist/code_chat``         ``dist/all/code_chat``
: Documentation    ``_build/html``            ``dist/all/bin``
: Source code      Mercurial repo in ``./``   ``dist/all/doc``
: ==============   ========================   ======================
:
: Create a clean ``dist/all`` directory and enter it.
mkdir dist
cd dist
rmdir /q /s all
mkdir all
cd all
:
: Copy over the source code with no intermediate files by cloning the repo then removing the repo files.
hg clone ..\.. src
rmdir /q /s src\.hg
:
: Copy over the executable and documentation.
xcopy /E /I ..\code_chat bin
xcopy /E /I ..\..\_build\html doc
:
: Package
: -------
: The :doc:`CodeChat.iss <CodeChat.iss>` script then packages everything in ``dist/all``.
cd ..\..
"\Program Files (x86)\Inno Setup 5\ISCC.exe" CodeChat.iss
:
: Publish to web
: ==============
: Copy the package and docs to the web.
set WEB=C:\Users\bjones\Documents\Dropbox\Public\CodeChat
copy Install_CodeChat.exe %WEB%
rmdir /q /s %WEB%\doc
xcopy /E /I dist\all\doc %WEB%\doc
