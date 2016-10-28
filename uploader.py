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

log = logger.getLogger(__name__, config.LOGLEVEL)

class Uploader(threading.Thread):
    def __init__(self, selfdir):
        threading.Thread.__init__(self)
        self.name = __name__
        self.daemon = False
        self.active = False
        
        self.selfdir = selfdir
        self.datadir = defines.getDataDIR()       
        self.url = config.URL + '/upload'
        self.cookie = {"username": defines.getUserName(), 'compname': defines.getCompName()} 
        defines.makedirs(self.datadir)
        
        
    def run(self):
        log.info('Start daemon: {0}'.format(self.name))
        self.active = True
        while self.active:
            try:
                defines.makedirs(self.datadir)
                with requests.Session() as sess:
                    sess.auth = config.AUTH
                    sess.cookies = requests.utils.cookiejar_from_dict(self.cookie)
                    sess.timeout = (1, 5)
                    for fn in [f for f in defines.rListFiles(self.datadir) if not os.path.basename(f).startswith('~')]:                        
                        filename = fn.replace(self.datadir, '').replace('\\', '/').strip('/')
                        try:
                            with open(fn, 'rb') as fp:
                                data = {'filename': filename,
                                        'data': base64.urlsafe_b64encode(fp.read())}
                            log.debug('Try to upload: {0}'.format(fn))    
                            if sess.post(self.url, data=data).content == '1':
                                log.debug('Try to delete: {0}'.format(fn))
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
    
    
    
        
        
        

        
