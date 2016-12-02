# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os
import base64
from config import config
from core import logger, utils


log = logger.getLogger(config['NAME'], config['LOGLEVEL'])
fmt = utils.fmt


class Hello():

    def __init__(self, env):
        try:
            self.env = env
        except Exception as e:
            log.error(e)

    def store(self, data):
        try:
            utils.makedirs(os.path.dirname(self.hello_file), mode=0775)

            with open(self.hello_file, 'wb') as fp:
                fp.write(data)
            os.chmod(self.hello_file, 0664)

            return 1

        except Exception as e:
            return str(e)

    def __call__(self, *args, **kwargs):
        compname = utils.trueEnc(utils.safe_str(kwargs.get('compname')))
        username = utils.trueEnc(utils.safe_str(kwargs.get('username')))
        data = base64.b64decode(kwargs.get('data'))
        if len(compname) > 0 and len(username) > 0 and len(data) > 0:
            self.datadir = os.path.join(config['DATA_DIR'], compname, username)
            self.hello_file = os.path.join(self.datadir, 'hello')
            return self.store(data)
