# -*- coding: utf-8 -*-

import os, sys, time, base64
import Cookie
import defines

class ImageStore():
    def __init__(self, selfdir, env):
        self.selfdir = selfdir
        self.env = env
        self.cookie = Cookie.SimpleCookie(self.env.get('HTTP_COOKIE'))        
        self.datadir = os.path.join('/tmp/.screens', self.env.get('REMOTE_ADDR'), self.cookie['username'].value)
        self.imagedir = os.path.join(self.datadir, 'images')
        defines.makedirs(self.imagedir)
        self.params = defines.Request(env)
    
    
    def store(self, data):
        fn = os.path.join(self.imagedir, "{0}.jpg".format(time.time()))
        try:            
            defines.makedirs(self.imagedir)
            
            with open(fn, 'wb') as fp:
                fp.write(base64.urlsafe_b64decode(data))
            
            return ''
                
        except Exception as e:
            os.unlink(fn)
            return e
        
    
    def main(self):
        if self.params.has_key('data'):
            return self.store(self.params.get('data'))
        else:
            return ''
        
       
        
