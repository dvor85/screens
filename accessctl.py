#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os
from config import config
from core import logger, utils, base
import argparse
import subprocess


log = logger.getLogger(config['NAME'])
fmt = utils.fmt


def rename_comp_arch(old, new):
    for dt in os.listdir(config['ARCHIVE_DIR']):
        for comp in os.listdir(os.path.join(config['ARCHIVE_DIR'], dt)):
            if comp.startswith(old):
                os.rename(
                    os.path.join(config['ARCHIVE_DIR'], dt, comp), os.path.join(config['ARCHIVE_DIR'], dt, new))


def rename_user_arch(comp, old, new):
    for dt in os.listdir(config['ARCHIVE_DIR']):
        for cp in os.listdir(os.path.join(config['ARCHIVE_DIR'], dt)):
            if cp.startswith(comp):
                for user in os.listdir(os.path.join(config['ARCHIVE_DIR'], dt, cp)):
                    if user == old:
                        os.rename(
                            os.path.join(config['ARCHIVE_DIR'], dt, cp, user), os.path.join(config['ARCHIVE_DIR'], dt, cp, new))


def createParser():
    parser = argparse.ArgumentParser(description="Tools for manipulate of access's schemes",
                                     epilog='(c) 2016 Dmitriy Vorotilin',
                                     prog='accessctl')
    subparsers = parser.add_subparsers(dest='action', title='Possible commands')

    show_parser = subparsers.add_parser('show', description="Show viewer's scheme.")
    show_parser.add_argument('--viewer', '-v', default='', help='Viewer for show')

    add_parser = subparsers.add_parser('add', description='Add viewer scheme.')
    add_parser.add_argument('--viewer', '-v', help='VIEWER for add', required=True)
    add_parser.add_argument('--comp', '-c', help='COMP for add', required=True)
    add_parser.add_argument('--user', '-u', help='USER in COMP for add', required=True)

    del_parser = subparsers.add_parser('delete', description='Delete viewer scheme.')
    del_parser.add_argument('--viewer', '-v', help='Delete VIEWER scheme', default='')
    del_parser.add_argument('--comp', '-c', help='''Delete COMP with all users.
                                              If VIEWER is not set, then delete from all viewers''', default='')
    del_parser.add_argument('--user', '-u', help='''Delete USER.
                                              If VIEWER is not set, then delete from all viewers.
                                              If COMP is not set then delete from all computers''')

    rename_parser = subparsers.add_parser('rename', description='Rename values.')
    rename_parser.add_argument('--viewer', '-v', help='Rename VIEWER to NEW value')
    rename_parser.add_argument('--comp', '-c', help='Set COMP title to NEW value', default='')
    rename_parser.add_argument('--user', '-u', help='''Rename USER to NEW value.
                                                 If COMP is not set, then rename on all computers''')
    rename_parser.add_argument('new', help='New value', metavar='NEW')

    passwd_parser = subparsers.add_parser('passwd', description='Add or change viewer password.')
    passwd_parser.add_argument('viewer')

    return parser


def main():
    parser = createParser()
    options = parser.parse_args()

    db = base.Base()

    if options.action == 'show':
        print fmt("{0:10s} | {1:10s} | {2:10s} | {3:10s}", 'VIEWER', 'COMP', 'TITLE', 'USER')
        print fmt('{0:-^45s}', '-')
        for line in db.get_scheme(options.viewer):
            print fmt("{viewer:10s} | {comp:10s} | {title:10s} | {user:10s}", **line)

    elif options.action == 'add':
        db.add_scheme(options.viewer, options.comp, options.user)

    elif options.action == 'delete':
        if options.user is not None:
            db.del_user(options.viewer, options.comp, options.user)
        elif options.comp != '':
            db.del_comp(options.viewer, options.comp)
        elif options.viewer != '':
            db.del_viewer(options.viewer)
        else:
            parser.print_help()

    elif options.action == 'rename':
        if options.viewer is not None:
            db.rename_viewer(options.viewer, options.new)
        elif options.user is not None:
            db.rename_user(options.comp, options.user, options.new)
            rename_user_arch(options.comp, options.user, options.new)
        elif options.comp != '':
            db.set_comp_title(options.comp, options.new)
#             rename_comp_arch(options.comp, options.new)

    elif options.action == 'passwd':
        cmd = ['htdigest']
        if not os.path.lexists(config['PASSWORD_FILE']):
            utils.makedirs(os.path.dirname(config['PASSWORD_FILE']))
            cmd.append('-c')
        cmd += [config['PASSWORD_FILE'], config['NAME'], options.viewer]
        subprocess.call(cmd)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
