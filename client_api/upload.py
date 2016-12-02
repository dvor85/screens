# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os
import base64
from config import config
from core import logger, utils


log = logger.getLogger(config['NAME'], config['LOGLEVEL'])
fmt = utils.fmt


class Upload():

    def __init__(self, env):
        try:
            self.env = env
        except Exception as e:
            log.error(e)

    def store(self, filename, data):
        try:
            utils.makedirs(os.path.dirname(filename), mode=0775)

            with open(filename, 'wb') as fp:
                fp.write(data)
            os.chmod(filename, 0664)

            return 1

        except Exception as e:
            return str(e)

    def __call__(self, *args, **kwargs):
        compname = utils.trueEnc(utils.safe_str(kwargs.get('compname')))
        username = utils.trueEnc(utils.safe_str(kwargs.get('username')))
        filename = utils.trueEnc(utils.safe_str(kwargs.get('filename')))
        data = base64.b64decode(kwargs.get('data'))
        if len(compname) > 0 and len(username) > 0 and len(filename) > 0:
            self.datadir = os.path.join(config['DATA_DIR'], compname, username)
            return self.store(os.path.join(self.datadir, filename), data)
