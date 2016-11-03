# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import logging, logging.handlers
import sys

class Logger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET):
        logging.Logger.__init__(self, name, level=level) 
        lf = logging.Formatter(fmt="%(asctime)-19s  %(levelname)s:%(module)s: %(message)s")  
        
        syslog_handler = logging.handlers.SysLogHandler()
        syslog_handler.setFormatter(lf)     
        self.addHandler(syslog_handler)
        
        sh = logging.StreamHandler(stream=sys.stdout)
        sh.setFormatter(lf)
        self.addHandler(sh)
        
        self.close_handlers()
        
        
    """
    It is need for rotating without errors in windows
    """        
    def close_handlers(self):
        if sys.platform.startswith('win'):
            for h in self.handlers:
                h.close()
        

    def _log(self, level, msg, args, exc_info=None, extra=None):      
        logging.Logger._log(self, level, msg, args, exc_info=exc_info, extra=extra)
        self.close_handlers()
        
        
def getLogger(name, level=logging.NOTSET):
    """
    Returns the logger with the specified name.
    name       - The name of the logger to retrieve
    """
    logging.setLoggerClass(Logger)

    log = logging.getLogger(name)
    log.setLevel(level)
    
    return log
        
        



        
    
        