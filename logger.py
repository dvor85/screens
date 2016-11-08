# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import logging
import sys, os
import utils
from logging.handlers import RotatingFileHandler as RFHandler


class Logger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET):
        logging.Logger.__init__(self, name, level=level)

        stream_format = logging.Formatter(fmt="%(asctime)-19s: %(name)s[%(module)s]: %(levelname)s: %(message)s")
        stream_handler = logging.StreamHandler(stream=sys.stdout)
        stream_handler.setFormatter(stream_format)
        self.addHandler(stream_handler)
        
        logfile = os.path.join(utils.getDataDIR(), 'logs/-screens.log')             
        utils.makedirs(os.path.dirname(logfile))
        rfh = RFHandler(filename=logfile, maxBytes=1024 * 1024, backupCount=2)                
        rfh.setFormatter(stream_format)     
        self.addHandler(rfh)
        

    def _log(self, level, msg, args, exc_info=None, extra=None):      
        logging.Logger._log(self, level, msg, args, exc_info=exc_info, extra=extra)
        
        
def getLogger(name, level=logging.NOTSET):
    """
    Returns the logger with the specified name.
    name       - The name of the logger to retrieve
    """
    logging.setLoggerClass(Logger)

    log = logging.getLogger(name)
    log.setLevel(level)
    
    return log
        
   
        

            
    
        
