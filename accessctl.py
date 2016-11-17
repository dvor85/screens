#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os
import sys
from config import config
from core import logger, utils, base
from optparse import OptionParser


log = logger.getLogger(config['NAME'])
fmt = utils.fmt


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
            print fmt("{viewer} | {comp}/{user}", **line)


def main():
    parser = OptionParser(conflict_handler="resolve",
                          version=config['VERSION'],
                          description=config['NAME'])
    parser.add_option("--show",
                      action="store_const", const="show", dest="action")
    parser.add_option("--add",
                      action="store_const", const="add", dest="action")
    parser.add_option("--del",
                      action="store_const", const="del", dest="action")

    (options, arguments) = parser.parse_args()

    actrl = AccessControl()
    if options.action == 'show':
        if len(arguments) > 0:
            for arg in arguments:
                actrl.show_scheme(arg)
        else:
            actrl.show_scheme('')
    elif options.action == 'add':
        if len(arguments) > 0:
            viewer = arguments[0]
        if len(arguments) == 2:
            comp, user = arguments[1].split('/')
        elif len(arguments) == 3:
            comp, user = arguments[1:]
        actrl.add_viewer(viewer, comp, user)
    elif options.action == 'del':
        comp, user = None, None
        if len(arguments) > 0:
            viewer = arguments[0]
        if len(arguments) == 2:
            comp_user = arguments[1].split('/')
            comp = comp_user[0] if len(comp_user) > 0 else None
            user = comp_user[1] if len(comp_user) > 1 else None
        if len(arguments) == 3:
            comp, user = arguments[1:]
        actrl.del_viewer(viewer, comp, user)


if __name__ == '__main__':
    main()
