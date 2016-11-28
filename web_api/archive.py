# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os
import json
from config import config
from core import logger, base, utils


log = logger.getLogger(config['NAME'], config['LOGLEVEL'])
fmt = utils.fmt


class Archive():

    def __init__(self, env):
        self.env = env

        self.params = utils.QueryParam(env, safe=True)
        self.username = env['REMOTE_USER']
        self.action = self.params['act']
        self.db = base.Base()

    def get(self, *args, **kwargs):
        journal = []
        try:
            allowed_comps = self.db.get_allowed_comps(self.username)
            if 'comp' in kwargs:
                allowed_users = self.db.get_allowed_users(self.username, kwargs['comp'])

            if self.action == 'get_movies':
                if 'user' in kwargs and 'comp' in kwargs and 'date' in kwargs and \
                        kwargs['user'] in allowed_users and kwargs['comp'] in allowed_comps:

                    journal = sorted((fmt("/archive/{date}/{comp}/{user}/{0}", f, **kwargs)
                                      for f in os.listdir(utils.trueEnc(
                                          fmt("{0}/{date}/{comp}/{user}", config['ARCHIVE_DIR'], **kwargs)))))
            elif self.action == 'get_users':
                journal = allowed_users
            elif self.action == 'get_comps':
                journal = allowed_comps
            elif self.action == 'get_dates':
                journal = sorted(os.listdir(config['ARCHIVE_DIR']), reverse=True)
        except Exception as e:
            log.error(e)

        return json.dumps(journal)

    def main(self):
        return self.get(**self.params)
