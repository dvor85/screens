# -*- coding: utf-8 -*-

import os, sys, time, base64
import Cookie


from core import logger, defines, base
from core.config import config


log = logger.getLogger(__name__, config['LOGLEVEL'])


class Script():
    def __init__(self, env):
        self.env = env
        self.params = defines.QueryParam(env)
        self.cookie = Cookie.SimpleCookie(self.env.get('HTTP_COOKIE'))
        if not (self.cookie.has_key('username') and self.cookie.has_key('compname')):
            raise Exception('Cookie not set')
        self.datadir = os.path.join(config['DATA_DIR'], self.cookie['compname'].value, self.cookie['username'].value)  
        self.script_dir = os.path.join(self.datadir, 'script')              
        self.query_file = os.path.join(self.script_dir, self.params.get('filename'))               
        
    
    def get(self):       
        try:
            with open(self.query_file, 'rb') as fp:
                return fp.read()
            
        except Exception as e:
            return ''
        
        
    def main(self):
        return self.get()
            
        