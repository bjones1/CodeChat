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
: ******************************************************************************
: build_exe.bat - Build a self-contained executable for the CodeChat application
: ******************************************************************************
: This file creates a Windows executable using `Pyinstaller <http://www.pyinstaller.org/>`_. This is the first step in the :ref:`build system <build_system>`. To do so:
:
: \1. Translate the ``.ui`` file. The frozen executable fails when loading the ``.ui`` file directly. So, translate it to a ``.py`` file instead.
call pyuic4 CodeChat\CodeChat.ui -o CodeChat\CodeChat_ui.py
:
: \2. Convert CodeChat to an executable. `Options <http://htmlpreview.github.io/?https://github.com/pyinstaller/pyinstaller/blob/develop/doc/Manual.html#options>`_ are:
:
: -y
:   Replace an existing executable folder or file without warning.
:
: --hidden-import
:   Name an imported Python module that is not visible in your code. (In this case, Sphinx dynamically loads the :doc:`CodeToRest <CodeChat/CodeToRest.py>` extension.)
:
: ``code_chat.py``
:   CodeChat entry point, from which Pyinstaller builds the application.
..\pyinstaller-git\pyinstaller.py -y --hidden-import=CodeChat.CodeToRest code_chat.py
:
: \3. Copy over template files which CodeChat uses for creating a new project and delete junk (which shouldn't be copied when crating a new project). **Note:** the first copy is really a kludgy symbolic link. I haven't found a better way to do this.
copy /Y default.css template
xcopy /E /I template dist\code_chat\template
del dist\code_chat\template\conf.py.rst
:
: \4. Finally, run the application to make sure it works. This also updates the generated documentation for packaging.
dist\code_chat\code_chat
