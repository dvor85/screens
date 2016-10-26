# -*- coding: utf-8 -*-

import os, sys
import threading
import base64
import defines
import urllib2
import time
import logger
import config
import requests

log = None

class Uploader(threading.Thread):
    def __init__(self, selfdir):
        threading.Thread.__init__(self)
        self.daemon = False
        self.active = False
        self.selfdir = selfdir
        self.datadir = defines.getDataDIR()       
        self.url = config.URL + '/upload'
        global log
        log = logger.Logger(os.path.join(self.datadir, 'logs/~screens.log'), 'uploader')
        self.cookie = {"username": defines.getUserName()} 
        defines.makedirs(self.datadir)
        
        
    def run(self):
        self.active = True
        while self.active:
            try:
                defines.makedirs(self.datadir)
                with requests.Session() as sess:
                    sess.auth = config.AUTH
                    sess.cookies = requests.utils.cookiejar_from_dict(self.cookie)
                    sess.timeout = (1,5)
                    for fn in [f for f in defines.rListFiles(self.datadir) if not os.path.basename(f).startswith('~')]:                        
                        filename = fn.replace(self.datadir, '').replace('\\','/').strip('/')
                        try:
                            with open(fn, 'rb') as fp:
                                data = {'filename': filename,
                                        'data': base64.urlsafe_b64encode(fp.read())}
                            if sess.post(self.url, data=data).content == '1':
                                os.unlink(fn)
                        except requests.exceptions.RequestException:
                            raise
                        except IOError as e:
                            log.error(e)

                        time.sleep(0.1)
            except Exception as e:
                log.error(e)
            
            time.sleep(10)
            
            
    def stop(self):
        self.active = False
    
    
if __name__ == "__main__":    
    selfdir = os.path.abspath(os.path.dirname(__file__))
    Uploader(selfdir).start()
#     for f in defines.rListFiles(selfdir):
#         log.debug(f)
#     print Uploader(selfdir).rgetFiles(selfdir)
    
    
    
        
        
        

        