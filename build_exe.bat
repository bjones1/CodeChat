: Copyright (C) 2012-2013 Bryan A. Jones.
:
: This file is part of CodeChat.
:
: CodeChat is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
:
: CodeChat is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
:
: You should have received a copy of the GNU General Public License along with CodeChat.  If not, see <http://www.gnu.org/licenses/>.


call pyuic4 CodeChat\CodeChat.ui -o CodeChat\CodeChat_ui.py
..\pyinstaller-git\pyinstaller.py -y code_chat.spec
copy /Y default.css template
xcopy /E /I template dist\code_chat\template
del dist\code_chat\template\conf.py.rst
dist\code_chat\code_chat
