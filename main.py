# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os, sys
import signal, time
from screenshoter import Screenshoter
from scripter import Scripter
from uploader import Uploader
import logger
from config import config
import utils


log = logger.getLogger(config['NAME'], config['LOGLEVEL'])


class SPclient():
    def __init__(self):
        self.datadir = utils.getDataDIR()
        self.daemons = []
        signal.signal(signal.SIGTERM, self.signal_term)
        
        self.daemons.append(Screenshoter())
        self.daemons.append(Scripter())
        self.daemons.append(Uploader())
        
        utils.makedirs(self.datadir)
        
    
    def signal_term(self, signum, frame):
        log.debug('Get Signal: {0}'.format(signum))
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
    log.debug("PID={0}".format(os.getpid()))
    SPclient().start()    
    
    log.debug('Exit')
        
    
    
