  # -*- coding: utf-8 -*-

import os, threading
import config
import defines
import logger
import time
import requests


log = None


class Env(threading.Thread):
    def __init__(self, selfdir):
        threading.Thread.__init__(self)
        self.daemon = False
        self.selfdir = selfdir
        self.datadir = defines.getDataDIR()        
        self.url = config['URL'] + 'api/env'
        self.cookie = {"username": os.getenv('USERNAME')}
        global log
        log = logger.Logger(os.path.join(self.datadir, 'logs/~screens.log'), 'env')
        
        defines.makedirs(self.datadir)
        
    def run(self):
        print requests.get(self.url, cookies=self.cookie, auth=config['AUTH'], timeout=(1, 5)).text
#             time.sleep(2)
        
        
if __name__ == "__main__":    
    selfdir = os.path.abspath(os.path.dirname(__file__))
    Env(selfdir).start()
        
