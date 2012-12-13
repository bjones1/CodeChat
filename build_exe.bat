call pyuic4 CodeChat\CodeChat.ui -o CodeChat\CodeChat_ui.py
..\pyinstaller-git\pyinstaller.py -y code_chat.spec
copy /Y default.css template
xcopy /E /I template dist\code_chat\template
del dist\code_chat\template\conf.py.rst
dist\code_chat\code_chat
