# -*- coding: utf-8 -*-

import logging, logging.handlers
import sys, os
import defines

class Logger(logging.Logger):
    def __init__(self, logfile, name, level=logging.DEBUG):
        logging.Logger.__init__(self, name, level=level)        
        
        lf = logging.Formatter(fmt="%(asctime)-19s  %(levelname)s:%(module)s: %(message)s")  
        
        sh = logging.StreamHandler(stream=sys.stdout)
        sh.setFormatter(lf)
        self.addHandler(sh)   
        
        defines.makedirs(os.path.dirname(logfile))
        rfh = logging.handlers.RotatingFileHandler(filename=logfile, maxBytes=1024000, backupCount=2)                
        rfh.setFormatter(lf)     
        self.addHandler(rfh)
        

    def __call__(self, msg):
        logging.log(self.level, msg)
        
        
    def _log(self, level, msg, args, exc_info=None, extra=None):
        logging.Logger._log(self, level, msg, args, exc_info=exc_info, extra=extra)


        
    
        