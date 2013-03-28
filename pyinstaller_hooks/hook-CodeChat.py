# hook-CodeChat.py - PyInstaller hook
# ===================================
# This script is loaded by PyInstaller during its processing. It identifies a hidden import, the CodeToRest module, which is dynamically loaded by Sphinx during its run.
hiddenimports = ['CodeToRest']
