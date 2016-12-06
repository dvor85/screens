#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os
from config import config
from core import logger, utils
import argparse
from hashlib import md5


log = logger.getLogger(config['NAME'])
fmt = utils.fmt


def generate(comp, user):
    script_dir = os.path.join(config['DATA_DIR'], comp, user, 'script')
    md5_file = os.path.join(script_dir, 'script.md5')
    if os.path.isdir(script_dir):
        with open(md5_file, 'wb') as fp:
            for fn in (f for f in utils.rListFiles(script_dir) if not f.endswith('script.md5')):
                filename = fn.replace(script_dir, '').replace('\\', '/').strip('/')
                md5_hash = md5(open(fn, 'rb').read()).hexdigest()
                fp.write(fmt('{md5_hash} {fn}\n', fn=filename, md5_hash=md5_hash))
        print fmt('Now you must execute bellow cmd:\nmv "{old}" "{new}"',
                  old=md5_file,
                  new=os.path.join(script_dir, fmt('_{0}', os.path.basename(md5_file))))


def createParser():
    parser = argparse.ArgumentParser(description="Tools for generate script.md5",
                                     epilog='(c) 2016 Dmitriy Vorotilin',
                                     prog='gen_script_md5')
    parser.add_argument('--comp', '-c', help='generate for COMP', required=True)
    parser.add_argument('--user', '-u', help='generate for USER in COMP', required=True)

    return parser


def main():
    parser = createParser()
    options = parser.parse_args()

    generate(options.comp, options.user)


if __name__ == '__main__':
    main()
