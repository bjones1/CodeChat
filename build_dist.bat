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
start installer.aip
