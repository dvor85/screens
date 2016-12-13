# -*- coding: utf-8 -*-

from distutils.core import setup
import py2exe
import os
import sys

if len(sys.argv) == 1:
    sys.argv.append('py2exe')
    sys.argv.append('-q')

_name = 'spsvc'
_data_files = [('', ['spsvc.bat', 'setup.bat', 'psexec.exe']),
               ('redist', ['redist/vcredist_x86.exe'])]
_py2exe_options = dict(dist_dir=os.path.join("dist", _name),
                       optimize=2,
                       )

setup(windows=[{'script': 'main.py', 'dest_base': _name}],
      data_files=_data_files,
      options={"py2exe": _py2exe_options},
      )
