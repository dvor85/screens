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
    def __init__(self, name, level=logging.DEBUG):
        logging.Logger.__init__(self, name, level=level)
#            
        lf = logging.Formatter(fmt="%(asctime)-19s  %(levelname)s:%(module)s: %(message)s")  
            
        sh = logging.StreamHandler(stream=sys.stdout)
        sh.setFormatter(lf)
        self.addHandler(sh)
        logfile = os.path.join(defines.getDataDIR(), 'logs/~screens.log') 
            
        defines.makedirs(os.path.dirname(logfile))
        rfh = RFHandler(filename=logfile, maxBytes=1000, backupCount=2)                
        rfh.setFormatter(lf)     
        self.addHandler(rfh)
        
        self.close_handlers()
        
        
    """
    It is need for rotating without errors in windows
    """        
    def close_handlers(self):
        for h in self.handlers:
            h.close()
        

    def _log(self, level, msg, args, exc_info=None, extra=None):      
        if sys.platform.startswith('win'):
            msg = str(msg).decode('windows-1251', 'ignore')
        logging.Logger._log(self, level, msg, args, exc_info=exc_info, extra=extra)
        
        self.close_handlers()
        
        
def getLogger(name, level=logging.DEBUG):
    """
    Returns the logger with the specified name.
    If the logger doesn't exist, it is created.

    name       - The name of the logger to retrieve
    """
    logging.setLoggerClass(Logger)

    if name in Logger.manager.loggerDict:
        return logging.getLogger(name)
    
    log = logging.getLogger(name)
    log.setLevel(level)
    
    return log
        
   
        

            
    
        