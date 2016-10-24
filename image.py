# -*- coding: utf-8 -*-

import os, sys, time, base64

class ImageStore():
    def __init__(self, selfdir, env):
        self.selfdir = selfdir
        self.env = env
        self.store_dir = "/tmp/"
        from utils import Request
        self.params = Request(env)
    
    
    def store(self, data):
        try:
            fn = os.path.join(self.store_dir, "{0}/{1}.jpg".format(self.env.get('REMOTE_ADDR'), time.time()))
            try:
                os.mkdir(os.path.dirname(fn))
            except:
                pass
            
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
        
       
        
