# .. -*- coding: utf-8 -*-
#
#    Copyright (C) 2012-2013 Bryan A. Jones.
#
#    This file is part of CodeChat.
#
#    CodeChat is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#    CodeChat is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along with CodeChat.  If not, see <http://www.gnu.org/licenses/>.
#

a = Analysis(['code_chat.py'],
             pathex=['C:\\Users\\bjones\\Documents\\documentation'],
             hiddenimports=[],
             hookspath=['pyinstaller_hooks'])
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts, # + [('v', '', 'OPTION')], # for extra run-time debug
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
