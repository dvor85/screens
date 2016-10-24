# -*- coding: utf-8 -*-

import logging, logging.handlers
import sys

class Logger(logging.Logger):
    def __init__(self, name, level=logging.DEBUG):
        logging.Logger.__init__(self, name, level=level) 
        lf = logging.Formatter(fmt="%(asctime)-19s  %(levelname)s:%(module)s: %(message)s")  
        
        syslog_handler = logging.handlers.SysLogHandler()
        syslog_handler.setFormatter(lf)     
        self.addHandler(syslog_handler)
        
        sh = logging.StreamHandler(stream=sys.stdout)
        sh.setFormatter(lf)
        self.addHandler(sh)
        

    def __call__(self, msg):
        logging.log(self.level, msg)
        
        
    def _log(self, level, msg, args, exc_info=None, extra=None):
        logging.Logger._log(self, level, msg, args, exc_info=exc_info, extra=extra)


        
    
        