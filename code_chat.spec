# -*- mode: python -*-
a = Analysis([os.path.join(HOMEPATH,'support\\_mountzlib.py'), os.path.join(HOMEPATH,'support\\useUnicode.py'), 'code_chat.py'],
             pathex=['C:\\Users\\bjones\\Documents\\documentation'])
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name=os.path.join('build\\pyi.win32\\code_chat', 'code_chat.exe'),
          debug=False,
          strip=False,
          upx=False,
          console=True )
coll = COLLECT( exe,
               a.binaries,
               a.zipfiles,
               a.datas + [('CodeChat.ui', 'C:\\Users\\bjones\\Documents\\documentation\\CodeChat\\CodeChat.ui', 'DATA')],
               strip=False,
               upx=False,
               name=os.path.join('dist', 'code_chat'))
