# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os, sys, time, base64, urllib2
import Cookie
from config import config
from core import logger, utils


log = logger.getLogger(config['NAME'], config['LOGLEVEL'])


class Upload():
    def __init__(self, env):
        self.env = env
        self.cookie = Cookie.SimpleCookie(self.env.get('HTTP_COOKIE'))
        if not (self.cookie.has_key('username') and self.cookie.has_key('compname')):
            raise Exception('Cookie not set')
        self.datadir = os.path.join(config['DATA_DIR'], \
                                    utils.safe_str(base64.urlsafe_b64decode(self.cookie['compname'].value)), \
                                    utils.safe_str(base64.urlsafe_b64decode(self.cookie['username'].value)))         
        self.params = utils.QueryParam(env)
        
    
    def store(self, filename, data):
        try:            
            utils.makedirs(os.path.dirname(filename), mode=0775)
            
            with open(filename, 'wb') as fp:
                fp.write(base64.urlsafe_b64decode(data))
            os.chmod(filename, 0664)
            
            return '1'
                
        except Exception as e: 
            return str(e)
        
        
    def main(self):
        if self.params.has_key('data') and self.params.has_key('filename'):
            return self.store(os.path.join(self.datadir, urllib2.unquote(utils.safe_str(self.params.get('filename')))), self.params.get('data'))
        else:
            return ''

            
        