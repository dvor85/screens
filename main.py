# -*- coding: utf-8 -*-

import os, sys
import time
import threading
import signal

from config import config
from core import logger, defines
from service.videomaker import VideoMaker
from service.arcrotator import ArchiveRotator
from core.init_core import Generator


log = logger.getLogger(__name__, config['LOGLEVEL'])


class Starter():

    def __init__(self):
        signal.signal(signal.SIGTERM, self.signal_term)
        self.active = False
        self.daemons = []
        self.daemons.append(VideoMaker())
        self.daemons.append(ArchiveRotator())
        Generator().main()
        
        
    def signal_term(self, signum, frame):
        log.debug('Get Signal: {0}'.format(signum))
        self.stop()
        
        
    def start(self):
        log.info('Start daemons')
        self.active = True
        for d in self.daemons:
            d.start()
            
    
    def stop(self):
        log.info('Stop daemons')
        self.active = False
        for d in self.daemons:
            d.stop()
            
            
    def sleep(self, timeout):
        t = 0          
        p = timeout - int(timeout)
        precision = p if p > 0 else 1      
        while self.active and t < timeout:            
            t += precision
            time.sleep(precision)
            
            
    def wait_termination(self):
        log.debug('Wait for termination')
        while self.active:   
            self.sleep(1)         
        for d in self.daemons:
            try:      
                log.debug('Wait for {}'.format(d.getName()))              
                d.join()
            except Exception as e:
                log.exception(e)
    
            
if __name__ == '__main__':
    log.debug("PID={0}".format(os.getpid()))
    starter = Starter()
    starter.start()
    
    starter.wait_termination()
    log.info('Exit')

            
        
    
        