# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os
import base64
import Cookie
from config import config
from core import logger, utils


log = logger.getLogger(config['NAME'], config['LOGLEVEL'])
fmt = utils.fmt


class Hello():

    def __init__(self, env):
        self.env = env
        self.cookie = Cookie.SimpleCookie(self.env.get('HTTP_COOKIE'))
        if not ('username' in self.cookie and 'compname' in self.cookie):
            raise Exception('Cookie not set')
        self.datadir = os.path.join(config['DATA_DIR'],
                                    utils.trueEnc(utils.safe_str(base64.urlsafe_b64decode(self.cookie['compname'].value))),
                                    utils.trueEnc(utils.safe_str(base64.urlsafe_b64decode(self.cookie['username'].value))))
        self.hello_file = os.path.join(self.datadir, 'hello')
        self.params = utils.QueryParam(env)

    def store(self, data):
        try:
            utils.makedirs(os.path.dirname(self.hello_file), mode=0775)

            with open(self.hello_file, 'wb') as fp:
                fp.write(base64.urlsafe_b64decode(data))
            os.chmod(self.hello_file, 0664)

            return '1'

        except Exception as e:
            return str(e)

    def main(self):
        if 'data' in self.params:
            return self.store(self.params.get('data'))
