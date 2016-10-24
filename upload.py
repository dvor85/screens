# -*- coding: utf-8 -*-

import os, sys, time, base64, urllib2
import Cookie
import defines

class Upload():
    def __init__(self, selfdir, env):
        self.selfdir = selfdir
        self.env = env
        self.cookie = Cookie.SimpleCookie(self.env.get('HTTP_COOKIE'))
        self.datadir = os.path.join('/tmp/.screens', self.env.get('REMOTE_ADDR'), self.cookie['username'].value)                
        self.params = defines.Request(env)
        
    
    def store(self, filename, data):
        try:            
            defines.makedirs(os.path.dirname(filename))
            
            with open(filename, 'wb') as fp:
                fp.write(base64.urlsafe_b64decode(data))
            
            return ''
                
        except Exception as e: 
            return e
        
        
    def main(self):
        if self.params.has_key('data') and self.params.has_key('filename'):
            return self.store(os.path.join(self.datadir, urllib2.unquote(self.params.get('filename'))), self.params.get('data'))
        else:
            return ''

            
        