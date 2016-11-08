﻿# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os, threading
import utils
import logger
import time
import requests
import base64
from config import config


log = logger.getLogger(config['NAME'], config['LOGLEVEL'])


class Env(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = False
        self.datadir = utils.getDataDIR()        
        self.url = config['URL'] + '/env'
        self.cookie = {"username": base64.urlsafe_b64encode(utils.getUserName()), \
                       'compname': base64.urlsafe_b64encode(utils.getCompName())}
        global log
        
        utils.makedirs(self.datadir)
        
    def run(self):
        print requests.get(self.url, cookies=self.cookie, auth=config['AUTH'], timeout=(1, 5)).text
#             time.sleep(2)
        
        
if __name__ == "__main__":    
    Env().start()
        
