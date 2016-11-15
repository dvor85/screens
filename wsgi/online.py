# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os
import json
from config import config
from core import logger, base, utils


log = logger.getLogger(config['NAME'], config['LOGLEVEL'])
fmt = utils.fmt


class Online():

    def __init__(self, env):
        self.env = env

        self.params = utils.QueryParam(env, safe=True)
        self.username = env['REMOTE_USER']
        self.db = base.Base()

    def get(self, *args, **kwargs):
        journal = []
        try:
            if 'user' in kwargs and 'comp' in kwargs:

                allowed_comps = self.db.get_allowed_comps(self.username)
                allowed_users = self.db.get_allowed_users(self.username, kwargs['comp'])

                if kwargs['user'] in allowed_users and kwargs['comp'] in allowed_comps:
                    journal = sorted((fmt("/data/{comp}/{user}/images/{0}", f, **kwargs)
                                      for f in os.listdir(utils.trueEnc(
                                          fmt("{0}/{comp}/{user}/images", config['DATA_DIR'], **kwargs)))))[-1:]
        except Exception as e:
            log.error(e)

        return json.dumps(journal)

    def main(self):
        return self.get(**self.params)
