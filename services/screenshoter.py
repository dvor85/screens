# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

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
from utils import fmt


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
        self.daemon = True
        self.active = False

        self.datadir = os.path.join(config['HOME_DIR'], config['NAME'])
        self.imagesdir = os.path.join(self.datadir, 'images')
        self.quality = config['SCR_QUALITY']
        self.maxRMS = config['CHGSCR_THRESHOLD']
        self.auth = requests.auth.HTTPDigestAuth(*config['AUTH'])
        self.img1_histogram, self.img2_histogram = None, None
        self.params = {"username": utils.utf(utils.getUserName()),
                       'compname': utils.utf(utils.getCompName())}
        self.jreq = {'jsonrpc': '2.0', 'method': 'image', 'id': __name__, 'params': self.params}

        self.headers = {'user-agent': fmt("{NAME}/{VERSION}", **config)}

        utils.makedirs(self.datadir)

    def stop(self):
        log.info(fmt('Stop daemon: {0}', self.name))
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

    def grabImage_PIL(self):
        """
        Делает скриншот с помощью Pillow библиотеки.
        ImageGrab.grab() порождает большую утечку памяти, если при вызове произошла ошибка.
        """
        bt = time.time()
        from PIL import ImageGrab
        try:
            return ImageGrab.grab()
        finally:
            log.debug(fmt("time of execution = {t}", t=time.time() - bt))

    def grabImage_win32(self):
        """
        Делает скриншот с помощью win32 api.
        """
        bt = time.time()
        import win32gui
        import win32ui
        import win32con
        import win32api
        from PIL import Image
        bmp = win32ui.CreateBitmap()
        try:
            CAPTUREBLT = 0x40000000
            hwin = win32gui.GetDesktopWindow()
            width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
            height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
            left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
            top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
            hwindc = win32gui.GetWindowDC(hwin)
            srcdc = win32ui.CreateDCFromHandle(hwindc)
            memdc = srcdc.CreateCompatibleDC()
            bmp.CreateCompatibleBitmap(srcdc, width, height)
            memdc.SelectObject(bmp)
            memdc.BitBlt((0, 0), (width, height), srcdc, (left, top), win32con.SRCCOPY | CAPTUREBLT)

            bmpinfo = bmp.GetInfo()
            bmpstr = bmp.GetBitmapBits(True)
            return Image.frombuffer(
                'RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr,
                'raw', 'BGRX', 0, 1)
        finally:
            memdc.DeleteDC()
            srcdc.DeleteDC()
            win32gui.ReleaseDC(hwin, hwindc)
            win32gui.DeleteObject(bmp.GetHandle())
            log.debug(fmt("time of execution = {t}", t=time.time() - bt))

    def _check_jres(self, jres):
        if self.jreq['id'] != jres['id']:
            raise ValueError('Invalid ID')
        if 'error' in jres:
            raise Exception(jres['error']['message'])
        return jres

    def run(self):
        log.info(fmt('Start daemon: {0}', self.name))

        self.active = True
        prev_timeout, timeout = 1, 2
        while self.active:
            try:
                utils.makedirs(self.datadir)
                log.debug('Try to grab image')

                img = self.grabImage_win32()
#                 img = self.grabImage_PIL()
                self.img1_histogram = img.histogram()
                rms = self.compare_images() if self.img1_histogram and self.img2_histogram else self.maxRMS + 1

                log.debug(fmt("Root Mean Square={rms}", rms=rms))
                if rms > self.maxRMS:
                    self.img2_histogram = self.img1_histogram
                    with closing(cStringIO.StringIO()) as data:
                        img.save(data, "JPEG", quality=self.quality)
                        self.params['data'] = base64.b64encode(data.getvalue())

                        self.jreq['params'] = self.params
                        self.jreq['id'] = time.time()
                        try:
                            log.debug('Try to upload image data')
                            r = requests.post(config['URL'], json=self.jreq, headers=self.headers, auth=self.auth,
                                              timeout=(1, 5), verify=False)
                            jres = self._check_jres(r.json())
                            if jres['result'] != 1:
                                raise requests.exceptions.HTTPError

                        except Exception as e:
                            log.debug(e)
                            utils.makedirs(self.imagesdir)
                            fn = os.path.join(self.imagesdir, fmt("{0}.jpg", self.jreq['id']))
                            log.debug(fmt('Try to save: {fn}', fn=fn))
                            with open(fn, 'wb') as imfp:
                                imfp.write(data.getvalue())
                            for i in os.listdir(self.imagesdir)[-config['SAVED_IMAGES']::-1]:
                                log.debug(fmt('Try to delete: {fn}', fn=os.path.join(self.imagesdir, i)))
                                os.unlink(os.path.join(self.imagesdir, i))

                prev_timeout, timeout = 1, 2
            except Exception as e:
                if timeout < 3600:
                    prev_timeout, timeout = timeout, prev_timeout + timeout
                log.error(e)

            time.sleep(timeout)

if __name__ == "__main__":
    t = Screenshoter()
    t.start()
    t.join()