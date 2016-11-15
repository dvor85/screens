# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os
import time
import base64
import Cookie
from config import config
from core import logger, utils


log = logger.getLogger(config['NAME'], config['LOGLEVEL'])
fmt = utils.fmt


class ImageStore():

    def __init__(self, env):
        self.env = env
        self.cookie = Cookie.SimpleCookie(self.env.get('HTTP_COOKIE'))
        if not ('username' in self.cookie and 'compname' in self.cookie):
            raise Exception('Cookie not set')
        self.datadir = os.path.join(config['DATA_DIR'],
                                    utils.trueEnc(utils.safe_str(base64.urlsafe_b64decode(self.cookie['compname'].value))),
                                    utils.trueEnc(utils.safe_str(base64.urlsafe_b64decode(self.cookie['username'].value))))
        self.imagedir = os.path.join(self.datadir, 'images')
        self.params = utils.QueryParam(env)

    def store(self, data):
        fn = os.path.join(self.imagedir, fmt("{0}.jpg", time.time()))
        try:
            utils.makedirs(self.imagedir, mode=0775)

            with open(fn, 'wb') as fp:
                fp.write(base64.urlsafe_b64decode(data))
            os.chmod(fn, 0664)

            return '1'

        except Exception as e:
            os.unlink(fn)
            return str(e)

    def main(self):
        if 'data' in self.params:
            return self.store(self.params.get('data'))
