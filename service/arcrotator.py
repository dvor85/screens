# -*- coding: utf-8 -*-

import os, sys
import time
import threading
import shutil

from config import config
from core import logger, defines


log = logger.getLogger(__name__, config['LOGLEVEL'])



class ArchiveRotator(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.name = __name__
        self.active = False
        
        
    def calculate_arc_size(self):
        total_size = 0
        for f in defines.rListFiles(config['ARCHIVE_DIR']):
            total_size += os.path.getsize(os.path.join(config['ARCHIVE_DIR'], f))
        return total_size/(1024**3)
        
        
    def rotate(self):
        arch_size = self.calculate_arc_size()
        log.info('Archive size = {}'.format(arch_size))
        if arch_size > config['ARC_SIZE_GB']:
            dayslist = sorted(os.listdir(config['ARCHIVE_DIR']))
            log.info('Delete day: {}'.format(dayslist[0]))
            shutil.rmtree(os.path.join(config['ARCHIVE_DIR'], dayslist[0]))
            
    
    def run(self):
        log.info('Start ArchiveRotator')
        self.active = True
        while self.active:
            try:
                self.rotate()
            except Exception as e:
                log.exception(e)
            
            self.sleep(3600)
            
            
    def stop(self):
        log.info('Stop ArchiveRotator')
        self.active = False
        
        
    def sleep(self, timeout):
        t = 0          
        p = timeout - int(timeout)
        precision = p if p > 0 else 1      
        while self.active and t < timeout:            
            t += precision
            time.sleep(precision)
    
        
if __name__ == '__main__':
    ArchiveRotator().start()
        
        
