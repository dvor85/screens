#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os, sys
from config import config
from core import logger, utils, base


log = logger.getLogger(config['NAME'], 0)


class AccessControl():
    def __init__(self):
        self.db = base.Base()

    def add_viewer(self, viewer, comp, user):
        self.db.add_scheme(viewer, comp, user)
    

    def show_scheme(self, viewer):
        for line in self.db.get_scheme(viewer):
            print u"{viewer} | {comp} | {user}".format(**line)
    
    
       
def usage():
    print """
        Usage: {0}:        
            <show> [viewer_name] 
            <add> <viewer_name> <comp_name/user_name>
        """.format(os.path.basename(sys.argv[0]))
    
        
if __name__ == '__main__':
    if len(sys.argv) > 1:
        actrl = AccessControl()
        cmd = sys.argv[1]
        if cmd == 'show':
            viewer = sys.argv[2] if len(sys.argv) > 2 else ''
            actrl.show_scheme(viewer)
        elif cmd == 'add':
            viewer = sys.argv[2]
            comp, user = sys.argv[3].split('/')        
            actrl.add_viewer(viewer, comp, user)
        else:
            usage()
    else:
        usage()
        
        
