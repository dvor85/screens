# -*- coding: utf-8 -*-

from distutils.core import setup
import py2exe
import os
import sys
import shutil

if len(sys.argv) == 1:
    sys.argv.append('py2exe')
    sys.argv.append('-q')


_name = 'spsvc'
_data_files = [('', ['setup.bat', 'psexec.exe', 'c:\\Windows\\System32\\msvcr100.dll']),
               ('kbdsvc', ['kbdsvc/kbdsvc.exe'])]
_py2exe_options = dict(dist_dir=os.path.join("dist", _name),
                       optimize=2,
                       )
try:
    print "delete %s" % _py2exe_options['dist_dir']
    shutil.rmtree(_py2exe_options['dist_dir'])
except Exception as e:
    print e
# os.removedirs(os.path.abspath())

setup(windows=[{'script': 'main.py', 'dest_base': _name}],
      zipfile='modules.dat',
      data_files=_data_files,
      options={"py2exe": _py2exe_options},
      )
