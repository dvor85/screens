# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os
from config import config
from core import logger, utils
import base64


log = logger.getLogger(config['NAME'], config['LOGLEVEL'])
fmt = utils.fmt


class Script():

    def __init__(self, env):
        try:
            self.env = env
        except Exception as e:
            log.error(e)

    def get(self):
        try:
            with open(self.query_file, 'rb') as fp:
                return base64.b64encode(fp.read())

        except:
            return ''

    def __call__(self, *args, **kwargs):
        compname = utils.trueEnc(utils.safe_str(kwargs.get('compname')))
        username = utils.trueEnc(utils.safe_str(kwargs.get('username')))
        filename = utils.trueEnc(utils.safe_str(kwargs.get('filename')))
        if len(compname) > 0 and len(username) > 0 and len(filename) > 0:
            self.datadir = os.path.join(config['DATA_DIR'], compname, username)
            self.query_file = os.path.join(self.datadir, 'script', filename)
            return self.get()
