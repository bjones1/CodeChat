# -*- mode: python -*-
a = Analysis(['code_chat.py'],
             pathex=['C:\\Users\\bjones\\Documents\\documentation'],
             hiddenimports=[],
             hookspath=['C:\\Users\\bjones\\Documents\\documentation\\pyinstaller_hooks'])
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name=os.path.join('build\\pyi.win32\\code_chat', 'code_chat.exe'),
          debug=False,
          strip=None,
          upx=False,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=False,
               name=os.path.join('dist', 'code_chat'))
