# -*- mode: python -*-
#
# Note: to make this work wiht PyQt / SPI API v2, I applied the workaround at http://www.pyinstaller.org/wiki/Recipe/PyQtChangeApiVersion.
#
# To make this work with Sphinx, I created a new hook that includes everything in the sphinx.ext directory.
#
a = Analysis([os.path.join(HOMEPATH,'support\\_mountzlib.py'), os.path.join(HOMEPATH,'support\\useUnicode.py'), 'code_chat.py'],
             pathex=['C:\\Users\\bjones\\Documents\\documentation'], hookspath = 'C:\\Users\\bjones\\Documents\\documentation\\pyinstaller_hooks')
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name=os.path.join('build\\pyi.win32\\code_chat', 'code_chat.exe'),
          debug=False,
          strip=False,
          upx=False,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas + 
                   [('CodeChat.ui', 'C:\\Users\\bjones\\Documents\\documentation\\CodeChat\\CodeChat.ui', 'DATA'),
               ],
               strip=False,
               upx=False,
               name=os.path.join('dist', 'code_chat'))
