# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os
from config import config
from core import logger, base, utils


log = logger.getLogger(config['NAME'], config['LOGLEVEL'])
fmt = utils.fmt


class Online():

    def __init__(self, env):
        try:
            self.env = env
            self.username = utils.true_enc(utils.safe_str(env.get('REMOTE_USER')))
            self.allowed_comps = []
            self.allowed_users = []
            self.db = base.Base()
        except Exception as e:
            log.error(e)

    def __call__(self, *args, **kwargs):
        journal = []
        try:
            _params = dict(
                comp=utils.true_enc(utils.safe_str(kwargs.get('comp', ''))),
                user=utils.true_enc(utils.safe_str(kwargs.get('user', ''))),
            )
            if len(_params['user']) > 0 and len(_params['comp']) > 0:
                if len(self.username) > 0:
                    self.allowed_comps = self.db.get_allowed_comps(self.username)
                self.allowed_users = self.db.get_allowed_users(self.username, _params['comp'])

                if _params['user'] in self.allowed_users and _params['comp'] in self.allowed_comps.iterkeys():
                    online_dir = utils.true_enc(fmt("{data_dir}/{comp}/{user}/images", data_dir=config['DATA_DIR'], **_params))
                    if os.path.isdir(online_dir):
                        journal = sorted(
                            fmt("{data_dir}/{fn}", data_dir=online_dir.replace(config['DATA_DIR'], '/data'), fn=f)
                            for f in os.listdir(online_dir))[-1:]
        except Exception as e:
            log.error(e)

        return journal
