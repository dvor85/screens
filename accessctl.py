#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os
import sys
from config import config
from core import logger, utils, base


log = logger.getLogger(config['NAME'])


class AccessControl():

    def __init__(self):
        self.db = base.Base()

    def add_viewer(self, viewer, comp, user):
        self.db.add_scheme(viewer, comp, user)

    def del_viewer(self, viewer, comp=None, user=None):
        if user is not None:
            self.del_user(viewer, comp, user)
        elif comp is not None:
            self.db.del_comp(viewer, comp)
        else:
            self.db.del_viewer(viewer)

    def show_scheme(self, viewer):
        for line in self.db.get_scheme(viewer):
            print u"{viewer} | {comp}/{user}".format(**line)


def usage():
    print """
        Usage: {0}:
            <show> [viewer_name]
            <add> <viewer_name> <comp_name/user_name>
            <del> <viewer> [<comp_name>[/user_name]]
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
        elif cmd == 'del':
            viewer = sys.argv[2]
            comp_user = []
            if len(sys.argv) > 3:
                comp_user = sys.argv[3].split('/')
            comp = comp_user[0] if len(comp_user) > 0 else None
            user = comp_user[1] if len(comp_user) > 1 else None
            actrl.del_viewer(viewer, comp, user)

        else:
            usage()
    else:
        usage()
