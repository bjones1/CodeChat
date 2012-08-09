rmdir /q /s build
rmdir /q /s dist
..\pyinstaller-git\pyinstaller.py -y --noupx --additional-hooks-dir=pyinstaller_hooks code_chat.spec
dist\code_chat\code_chat