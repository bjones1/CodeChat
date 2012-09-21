cd dist
rmdir /q /s all
mkdir all
cd all
hg clone ..\.. src
rmdir /q /s src\.hg
xcopy /E /I ..\code_chat bin
xcopy /E /I ..\..\_build\html doc
xcopy /E /I ..\..\template template
copy ..\..\default.css template
del template\conf.py.rst
cd ..\..
"\Program Files (x86)\Inno Setup 5\ISCC.exe" CodeChat.iss
set WEB=C:\Users\bjones\Documents\Dropbox\Public\CodeChat
copy Install_CodeChat.exe %WEB%
rmdir /q /s %WEB%\doc
xcopy /E /I dist\all\doc %WEB%\doc
