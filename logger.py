# -*- coding: utf-8 -*-

import logging
import sys, os
import defines
from logging.handlers import RotatingFileHandler as RFHandler

# try:
#     from cloghandler import ConcurrentRotatingFileHandler as RFHandler
# except ImportError:
#     # Next 2 lines are optional:  issue a warning to the user
#     from warnings import warn
#     warn("ConcurrentLogHandler package not installed.  Using builtin log handler")
#     from logging.handlers import RotatingFileHandler as RFHandler


class Logger(logging.Logger):
    def __init__(self, logfile, name, level=logging.DEBUG):
        logging.Logger.__init__(self, name, level=level)
        
        lf = logging.Formatter(fmt="%(asctime)-19s  %(levelname)s:%(module)s: %(message)s")  
        
        sh = logging.StreamHandler(stream=sys.stdout)
        sh.setFormatter(lf)
        self.addHandler(sh)   
        
        defines.makedirs(os.path.dirname(logfile))
        rfh = RFHandler(filename=logfile, maxBytes=1024000, backupCount=2)                
        rfh.setFormatter(lf)     
        self.addHandler(rfh)
        

    def __call__(self, msg):
        logging.log(self.level, msg)
        
        
    def _log(self, level, msg, args, exc_info=None, extra=None):
        if sys.platform.startswith('win'):
            msg = str(msg).decode('windows-1251', 'ignore')
        logging.Logger._log(self, level, msg, args, exc_info=exc_info, extra=extra)
            
    
        