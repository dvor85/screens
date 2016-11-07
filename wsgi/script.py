# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os, sys, time, base64
import Cookie

from config import config
from core import logger, utils


log = logger.getLogger(__name__, config['LOGLEVEL'])


class Script():
    def __init__(self, env):
        self.env = env
        self.params = utils.QueryParam(env)
        self.cookie = Cookie.SimpleCookie(self.env.get('HTTP_COOKIE'))
        if not (self.cookie.has_key('username') and self.cookie.has_key('compname')):
            raise Exception('Cookie not set')
        self.datadir = os.path.join(config['DATA_DIR'], \
                                    utils.safe_str(base64.urlsafe_b64decode(self.cookie['compname'].value)), \
                                    utils.safe_str(base64.urlsafe_b64decode(self.cookie['username'].value)))
        self.script_dir = os.path.join(self.datadir, 'script')              
        self.query_file = os.path.join(self.script_dir, utils.safe_str(self.params.get('filename')))               
        
    
    def get(self):       
        try:
            with open(self.query_file, 'rb') as fp:
                return fp.read()
            
        except Exception as e:
            return ''
        
        
    def main(self):
        return self.get()
            
        