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

    FLAG = 1  # Битовый флаг запуска

    def __init__(self):
        threading.Thread.__init__(self)
        self.name = __name__
        self.daemon = True
        self.active = False

        self.datadir = os.path.join(config['HOME_DIR'], config['NAME'], utils.get_user_name())
        self.imagesdir = os.path.join(self.datadir, 'images')
        self.quality = config['SCR_QUALITY']
        self.url = config['URL'][0]
        self.maxRMS = config['CHGSCR_THRESHOLD']
        self.auth = requests.auth.HTTPDigestAuth(*config['AUTH'])
        self.img1_histogram, self.img2_histogram = None, None
        self.params = {"username": utils.utf(utils.get_user_name()),
                       'compname': utils.utf(utils.get_comp_name())}
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

    def grabImage(self):
        try:
            return self.grabImage_PIL()
        except Exception as e:
            log.error(e)
            try:
                return self.grabImage_win32()
            except Exception as e:
                log.error(e)
                return self.grabImage_wx()

    def grabImage_wx(self):
        from PIL import Image
        import wx
        bt = time.time()
        try:
            app = wx.App()  # Need to create an App instance before doing anything
            screen = wx.ScreenDC()
            size = screen.GetSize()
            bmp = wx.Bitmap(size[0], size[1])
            mem = wx.MemoryDC(bmp)
            try:
                mem.Blit(0, 0, size[0], size[1], screen, 0, 0)
            finally:
                del mem  # Release bitmap
            myWxImage = bmp.ConvertToImage()
            PilImage = Image.new('RGB', (myWxImage.GetWidth(), myWxImage.GetHeight()))
            PilImage.frombytes(str(myWxImage.GetData()))
            return PilImage
        finally:
            log.debug(fmt("time of execution = {t}", t=time.time() - bt))

    def grabImage_PIL(self):
        """
        Делает скриншот с помощью Pillow библиотеки.
        ImageGrab.grab() порождает большую утечку памяти, если при вызове произошла ошибка.
        """
        from PIL import ImageGrab
        bt = time.time()
        try:
            return ImageGrab.grab()
        finally:
            log.debug(fmt("time of execution = {t}", t=time.time() - bt))

    def grabImage_win32(self):
        """
        Делает скриншот с помощью win32 api.
        """
        import win32gui
        import win32ui
        import win32con
        import win32api
        from PIL import Image
        bt = time.time()
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
            raise requests.exceptions.HTTPError(jres['error']['message'])
        return jres

    def run(self):
        log.info(fmt('Start daemon: {0}', self.name))

        self.active = True
        prev_timeout, timeout = 1, 2
        while self.active:
            try:
                utils.makedirs(self.datadir)
                log.debug('Try to grab image')

#                 img = self.grabImage_win32()
#                 img = self.grabImage_PIL()
                img = self.grabImage()
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
                            bt = time.time()
                            r = requests.post(self.url, json=self.jreq, headers=self.headers, auth=self.auth,
                                              timeout=(3.05, 27), verify=config['CERT'])
                            jres = self._check_jres(r.json())
                            log.debug(fmt("time of request = {t}", t=time.time() - bt))
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
                            raise
                        finally:
                            prev_timeout, timeout = 1, 2

            except Exception as e:
                if timeout < 60:
                    prev_timeout, timeout = timeout, prev_timeout + timeout

                if e.__class__ in requests.exceptions.__dict__.itervalues():
                    try:
                        ind = config['URL'].index(self.url)
                        self.url = config['URL'][ind + 1]
                    except Exception:
                        self.url = config['URL'][0]
                log.error(e)

            time.sleep(timeout)


if __name__ == "__main__":
    t = Screenshoter()
    t.start()
    t.join()
