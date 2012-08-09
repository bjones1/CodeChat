..\pyinstaller-2.0\pyinstaller.py -y --noupx --additional-hooks-dir=C:\Users\bjones\Documents\documentation\pyinstaller_hooks code_chat.py
:xcopy /E /I C:\Python27\Lib\site-packages\Sphinx-1.1.3-py2.7.egg\sphinx\themes dist\code_chat\themes
:copy C:\Python27\Lib\site-packages\docutils\writers\html4css1\*.css dist\code_chat
:copy C:\Python27\Lib\site-packages\docutils\writers\html4css1\*.txt dist\code_chat
:copy C:\Python27\Lib\site-packages\docutils\parsers\rst\include\*.* dist\code_chat
dist\code_chat\code_chat