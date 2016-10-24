# -*- coding: utf-8 -*-

import os, sys, time, base64

class Script():
    def __init__(self, selfdir, env):
        self.env = env
        self.selfdir = selfdir
        self.datadir = os.path.join(self.selfdir, 'data', self.env.get('REMOTE_ADDR'))        
        self.script = os.path.join(self.datadir, 'script/script')                
        from utils import Request
        self.params = Request(env)
        
    
    def get(self):       
        try:
            with open(self.script, 'rb') as fp:
                return fp.read()
            
        except Exception as e:
            return ''
        
        
    def main(self):
        return self.get()
            
        