# -*- coding: utf-8 -*-

import os, threading
import config
import defines
import logger
import time


log = None


class Env(threading.Thread):
    def __init__(self, selfdir):
        threading.Thread.__init__(self)
        self.daemon = False
        self.selfdir = selfdir
        self.datadir = os.path.expandvars(config.DATADIR)        
        self.url = config.URL + '/env'
        self.cookie = {"username": os.getenv('USERNAME')}
        global log
        log = logger.Logger(os.path.join(self.datadir, 'logs/~screens.log'), 'env')
        
        defines.makedirs(self.datadir)
        
    def run(self):
        print defines.GET(self.url, cookie=self.cookie)
#             time.sleep(2)
        
        
if __name__ == "__main__":    
    selfdir = os.path.abspath(os.path.dirname(__file__))
    Env(selfdir).start()
        