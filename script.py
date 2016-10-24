# -*- coding: utf-8 -*-

import os, sys, time, base64
import Cookie
import defines

class Script():
    def __init__(self, selfdir, env):
        self.env = env
        self.selfdir = selfdir
        self.cookie = Cookie.SimpleCookie(self.env.get('HTTP_COOKIE'))
        self.datadir = os.path.join('/tmp/.screens', self.env.get('REMOTE_ADDR'), self.cookie['username'].value)                
        self.script = os.path.join(self.datadir, 'script/script')               
        
        self.params = defines.Request(env)
        
    
    def get(self):       
        try:
            defines.makedirs(os.path.dirname(self.script))
            with open(self.script, 'rb') as fp:
                return fp.read()
            
        except Exception as e:
            return ''
        
        
    def main(self):
        return self.get()
            
        