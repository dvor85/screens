# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os
from config import config
from core import logger, base, utils

log = logger.getLogger(config['NAME'], config['LOGLEVEL'])
fmt = utils.fmt


class Archive():

    def __init__(self, env):
        try:
            self.env = env
            self.username = utils.true_enc(utils.safe_str(env.get('REMOTE_USER')))
            self.allowed_comps = []
            self.allowed_users = []
            self.db = base.Base()
        except Exception as e:
            log.error(e)

    def get_availible_comps(self, date):
        comps_dir = utils.true_enc(fmt("{data_dir}/{date}", data_dir=config['ARCHIVE_DIR'], date=date))
        avail_comps = os.listdir(comps_dir)
        return dict((k, v) for k, v in self.allowed_comps.iteritems() if k in avail_comps)

    def __call__(self, *args, **kwargs):
        journal = []
        try:
            self.action = utils.true_enc(utils.safe_str(kwargs.get('act')))

            _params = dict(
                comp=utils.true_enc(utils.safe_str(kwargs.get('comp', ''))),
                user=utils.true_enc(utils.safe_str(kwargs.get('user', ''))),
                date=utils.true_enc(utils.safe_str(kwargs.get('date', '')))
            )

            if len(self.username) > 0:
                self.allowed_comps = self.db.get_allowed_comps(self.username)
            if len(_params['comp']) > 0:
                self.allowed_users = self.db.get_allowed_users(self.username, _params['comp'])

            if self.action == 'get_movies':
                for p in _params.itervalues():
                    if len(p) <= 0:
                        return journal

                if _params['user'] in self.allowed_users and _params['comp'] in self.allowed_comps.iterkeys():
                    movies_dir = utils.true_enc(fmt("{data_dir}/{date}/{comp}/{user}", data_dir=config['ARCHIVE_DIR'], **_params))
                    if os.path.isdir(os.path.join(movies_dir, 'movies')):
                        movies_dir = os.path.join(movies_dir, 'movies')
                    if os.path.isdir(movies_dir):
                        journal = sorted(
                            fmt("{archive}/{fn}", fn=f, archive=movies_dir.replace(config['ARCHIVE_DIR'], '/archive'))
                            for f in os.listdir(movies_dir)
                        )
            elif self.action == 'get_users':
                journal = self.allowed_users
            elif self.action == 'get_comps' and _params['date']:
                journal = self.get_availible_comps(_params['date'])
            elif self.action == 'get_dates':
                journal = sorted(os.listdir(config['ARCHIVE_DIR']), reverse=True)
        except Exception as e:
            log.error(e)

        return journal
