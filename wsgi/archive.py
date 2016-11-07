# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os, sys, time, base64, urllib2
import Cookie
import json

from config import config
from core import logger, base, utils


log = logger.getLogger(__name__, config['LOGLEVEL'])


class Archive():
    def __init__(self, env):
        self.env = env
        
        self.params = utils.QueryParam(env, safe=True)
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
        allowed_comps = self.db.get_allowed_comps(self.username)
        if kwargs.has_key('comp'):
            allowed_users = self.db.get_allowed_users(self.username, kwargs['comp'])      
                  
        if kwargs.has_key('user') and kwargs.has_key('comp') and kwargs.has_key('date') and \
            kwargs['user'] in allowed_users and kwargs['comp'] in allowed_comps:
                
            journal = sorted(["/archive/{date}/{comp}/{user}/{}".format(f, **kwargs) for f \
                       in os.listdir("{}/{date}/{comp}/{user}".format(config['ARCHIVE_DIR'], **kwargs))])            
        elif kwargs.has_key('comp') and kwargs.has_key('date') and kwargs['comp'] in allowed_comps:
            
            journal = [u for u in os.listdir("{}/{date}/{comp}".format(config['ARCHIVE_DIR'], **kwargs)) if u in allowed_users] 
        elif kwargs.has_key('date'):
            
            journal = [c for c in os.listdir("{}/{date}".format(config['ARCHIVE_DIR'], **kwargs)) if c in allowed_comps]
        else:
            journal = sorted(os.listdir(config['ARCHIVE_DIR']), reverse=True)
            
        return json.dumps(journal)
    

    def main(self): 
        return self.get(**self.params)    
        

            
        