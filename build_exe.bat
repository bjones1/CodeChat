call pyuic4 CodeChat\CodeChat.ui -o CodeChat\CodeChat_ui.py
..\pyinstaller-git\pyinstaller.py -y code_chat.spec
dist\code_chat\code_chat
