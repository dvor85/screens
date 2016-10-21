# -*- coding: utf-8 -*-

import os, sys
import signal,time
from screenshoter import Screenshoter
from scripter import Scripter
from uploader import Uploader
import logger
import config
import defines


log = None


class Screen():
    def __init__(self, selfdir):
        self.sefdir = selfdir
        self.datadir = os.path.expandvars(config.DATADIR)
        self.daemons = []
        global log
        log = logger.Logger(os.path.join(self.datadir, 'logs/~screens.log'), 'screenshoter')
        signal.signal(signal.SIGTERM, self.signal_term)
        self.daemons.append(Screenshoter(self.sefdir))
        self.daemons.append(Scripter(selfdir))
        self.daemons.append(Uploader(selfdir))
        
        defines.makedirs(self.datadir)
        
    
    def signal_term(self, signum, frame):
        log.debug('Get Signal')
        self.stop()
        
        
    def start(self):
        for d in self.daemons:
            d.start()
#         self.wait_termination()
            
    
    def stop(self):
        for d in self.daemons:
            d.stop()  
            
            
    def wait_termination(self):
        for d in self.daemons:
            try:
                d.join()
            except:
                pass
    

if __name__ == '__main__':
    selfdir = os.path.abspath(os.path.dirname(__file__)) 
    Screen(selfdir).start()
    log.debug('Exit')
        
    
    
