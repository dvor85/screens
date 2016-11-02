# -*- coding: utf-8 -*-

import os, sys, time, base64, urllib2
import Cookie
import json

from config import config
from core import logger, defines, base


log = logger.getLogger(__name__, config['LOGLEVEL'])


class Online():
    def __init__(self, env):
        self.env = env
        
        self.params = defines.QueryParam(env, safe=True)
#         self.username = self.getUsername()
        self.username = 'admin'
        self.db = base.Base('')
        
        
    def getUsername(self):
        try:
            username = ''
            auth = self.env['HTTP_AUTHORIZATION']            
            if auth:
                scheme, data = auth.split(None, 1)
                if scheme.lower() == 'basic':
                    username, password = data.decode('base64').split(':', 1)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print 'error {type}: {value}'.format(**{'type':exc_type, 'value':exc_value})
        return username
        
    
    def get(self, *args, **kwargs):
        journal = []
        if kwargs.has_key('user') and kwargs.has_key('comp'): 
                 
            allowed_comps = self.db.get_allowed_comps(self.username)  
            allowed_users = self.db.get_allowed_users(self.username, kwargs['comp'])
                  
            if kwargs['user'] in allowed_users and kwargs['comp'] in allowed_comps:
                journal = sorted(["/data/{comp}/{user}/images/{}".format(f, **kwargs) for f in os.listdir("{}/{comp}/{user}/images".format(config['DATA_DIR'], **kwargs))])[-1:]
        
            
        return json.dumps(journal)
    

    def main(self): 
        return self.get(**self.params) 
    
    
        