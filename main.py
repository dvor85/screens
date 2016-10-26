# -*- coding: utf-8 -*-

import os, sys
import signal,time
from screenshoter import Screenshoter
from scripter import Scripter
from uploader import Uploader
import logger, logging
import config
import defines


log = logger.getLogger('main')
# for i in range(10):
#     log.debug('test')
# 
# 
# sys.exit()


class Screen():
    def __init__(self, selfdir):
        self.sefdir = selfdir
        self.datadir = defines.getDataDIR()
        self.daemons = []
#         log.debug('test')
        
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
    log.debug(os.getpid())
    log.debug('Exit')
        
    
    
