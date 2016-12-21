# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os
import time
import base64
from config import config
from core import logger, utils


log = logger.getLogger(config['NAME'], config['LOGLEVEL'])
fmt = utils.fmt


class ImageStore():

    def __init__(self, env):
        try:
            self.env = env
        except Exception as e:
            log.error(e)

    def store(self, data):
        fn = os.path.join(self.imagedir, fmt("{0}.jpg", time.time()))
        try:
            utils.makedirs(self.imagedir, mode=0775)

            with open(fn, 'wb') as fp:
                fp.write(data)
            os.chmod(fn, 0664)

            return 1

        except Exception as e:
            os.unlink(fn)
            return str(e)

    def __call__(self, *args, **kwargs):
        compname = utils.true_enc(utils.safe_str(kwargs.get('compname')))
        username = utils.true_enc(utils.safe_str(kwargs.get('username')))
        data = base64.b64decode(kwargs.get('data'))
        if len(compname) > 0 and len(username) > 0 and len(data) > 0:
            self.datadir = os.path.join(config['DATA_DIR'], compname, username)
            self.imagedir = os.path.join(self.datadir, 'images')
            return self.store(data)
