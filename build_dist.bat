: Copyright (C) 2012-2013 Bryan A. Jones.
:
: This file is part of CodeChat.
:
: CodeChat is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
:
: CodeChat is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
:
: You should have received a copy of the GNU General Public License along with CodeChat.  If not, see <http://www.gnu.org/licenses/>.

cd dist
rmdir /q /s all
mkdir all
cd all
hg clone ..\.. src
rmdir /q /s src\.hg
xcopy /E /I ..\code_chat bin
xcopy /E /I ..\..\_build\html doc
cd ..\..
"\Program Files (x86)\Inno Setup 5\ISCC.exe" CodeChat.iss
set WEB=C:\Users\bjones\Documents\Dropbox\Public\CodeChat
copy Install_CodeChat.exe %WEB%
rmdir /q /s %WEB%\doc
xcopy /E /I dist\all\doc %WEB%\doc
