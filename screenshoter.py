# -*- coding: utf-8 -*-

import sys
import os
import cStringIO
import time
import base64
from contextlib import closing
import defines
import threading
import logger
from config import config
import requests
import math

log = logger.getLogger(__name__, config['LOGLEVEL'])


class Screenshoter(threading.Thread):
    def __init__(self, selfdir):
        threading.Thread.__init__(self)
        self.name = __name__
        self.daemon = False   
        self.active = False
        
        self.selfdir = selfdir
        self.datadir = defines.getDataDIR()     
        self.imagesdir = os.path.join(self.datadir, 'images')  
        self.url = config['URL'] + '/image'
        self.quality = 30        
        self.maxRMS = 50
        self.cookie = {"username": defines.getUserName(), 'compname': defines.getCompName()} 
        
        defines.makedirs(self.datadir)      
        
        
    def stop(self):
        self.active = False
        
    """
    Сравнение изображений методом среднеквадратичного отклонения
    :return: среднеквадратичное отклонение. Если  0, то изображения одинаковы
    """    
    def compare_img(self, img1, img2):        
        h1 = img1.histogram()
        h2 = img2.histogram()
        rms = math.sqrt(sum(map(lambda a,b: (a-b)**2, h1, h2))/len(h1))
        return rms
        
        
    def run(self): 
        log.info('Start daemon: {0}'.format(self.name))
        from PIL import ImageGrab
        self.active = True
        prev_img = None
        while self.active:
            try:
                
                defines.makedirs(self.datadir)
                log.debug('Try to grab image')
                
                img = ImageGrab.grab()
                
                rms = self.compare_img(img, prev_img) if prev_img else self.maxRMS + 1
                    
                log.debug("Root Mean Square={}".format(rms))
                if rms > self.maxRMS:
                    prev_img = img.copy()                        
                    with closing(cStringIO.StringIO()) as fp:       
                        img.save(fp, "JPEG", quality=self.quality) 
                        data = {'data': base64.urlsafe_b64encode(fp.getvalue())}
                        try:
                            log.debug('Try to upload image data')
                            r = requests.post(self.url, data=data, cookies=self.cookie, auth=config['AUTH'], timeout=(1, 5))
                            r.raise_for_status()                        
                            if r.content != '1':
                                raise requests.exceptions.HTTPError
                                
                        except Exception as e:
                            log.debug(e)
                            defines.makedirs(self.imagesdir)
                            fn = os.path.join(self.imagesdir, "{0}.jpg".format(time.time())) 
                            log.debug('Try to save: {0}'.format(fn))                       
                            with open(fn, 'wb') as imfp:
                                imfp.write(fp.getvalue())                        
                            for i in os.listdir(self.imagesdir)[-config['SAVED_IMAGES']::-1]:
                                log.debug('Try to delete: {0}'.format(os.path.join(self.imagesdir, i)))  
                                os.unlink(os.path.join(self.imagesdir, i))
            
            except Exception as e:
                log.error(e)
            
            time.sleep(2)
        
if __name__ == "__main__":
    selfdir = os.path.abspath(os.path.dirname(__file__))
    Screenshoter(selfdir).start()
            
             
        
        
