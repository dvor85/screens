# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os
import sys
import time
import base64
import urllib2
import Cookie
import json
from config import config
from core import logger, base, utils


log = logger.getLogger(config['NAME'], config['LOGLEVEL'])


class Online():

    def __init__(self, env):
        self.env = env

        self.params = utils.QueryParam(env, safe=True)
#         self.username = self.getUsername()
        self.username = 'admin'
        self.db = base.Base()

    def getUsername(self):
        try:
            username = ''
            auth = self.env['HTTP_AUTHORIZATION']
            if auth:
                scheme, data = auth.split(None, 1)
                if scheme.lower() == 'basic':
                    username, password = data.decode('base64').split(':', 1)
        except Exception as e:
            log.error(e)
        return username

    def get(self, *args, **kwargs):
        journal = []
        try:
            if 'user' in kwargs and 'comp' in kwargs:

                allowed_comps = self.db.get_allowed_comps(self.username)
                allowed_users = self.db.get_allowed_users(self.username, kwargs['comp'])

                if kwargs['user'] in allowed_users and kwargs['comp'] in allowed_comps:
                    journal = sorted(["/data/{comp}/{user}/images/{}".format(f, **kwargs)
                                      for f in os.listdir("{}/{comp}/{user}/images".format(config['DATA_DIR'], **kwargs))])[-1:]
        except Exception as e:
            log.error(e)

        return json.dumps(journal)

    def main(self):
        return self.get(**self.params)
