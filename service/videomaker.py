# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os
import datetime
import time
import threading
import multiprocessing
import subprocess
from config import config
from core import logger, utils


log = logger.getLogger(config['NAME'])
fmt = utils.fmt
sema = multiprocessing.Semaphore(8)


class VideoProcess(multiprocessing.Process):

    def __init__(self, sema, comp, user):
        multiprocessing.Process.__init__(self)
        self.sema = sema
        self.comp = comp
        self.user = user

    def make_video(self):
        log.info(fmt('Make video: {comp}/{user}', comp=self.comp, user=self.user))
        src_dir = os.path.join(config['DATA_DIR'], self.comp, self.user, 'images')
        im_list = sorted([float(os.path.splitext(f)[0]) for f in os.listdir(src_dir) if f.endswith('.jpg')])

        if len(im_list) > 15:
            _params = dict(bt=datetime.datetime.fromtimestamp(im_list[0]),
                           et=datetime.datetime.fromtimestamp(im_list[-1]),
                           user=self.user,
                           comp=self.comp)

            dst_file = os.path.join(
                config['ARCHIVE_DIR'], fmt('{bt:%Y%m%d}/{comp}/{user}/{bt:%H%M%S}-{et:%H%M%S}.mp4', **_params))
            utils.makedirs(os.path.dirname(dst_file), mode=0775)

            proc = subprocess.Popen(
                fmt('avconv -threads auto -y -f image2pipe -r 2 -c:v mjpeg -i - -c:v libx264 -preset ultrafast \
                    -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" \
                    -profile:v baseline -b:v 100k -qp 28 -an -r 25 "{dst_file}"', dst_file=dst_file),
                shell=True, close_fds=True, stdin=subprocess.PIPE)
            with proc.stdin:
                log.debug('Add images to process stdin')
                for f in im_list:
                    try:
                        proc.stdin.write(open(os.path.join(src_dir, fmt("{0}.jpg", f)), 'rb').read())
                    except Exception as e:
                        log.error(e)
            proc.wait()
            if proc.returncode != 0:
                raise subprocess.CalledProcessError(proc.returncode, str(proc.pid))
            log.debug('Delete images')
            for f in im_list:
                try:
                    os.unlink(os.path.join(src_dir, fmt("{fn}.jpg", fn=f)))
                except Exception as e:
                    log.error(e)

    def run(self):
        try:
            with self.sema:
                self.make_video()
        except Exception as e:
            log.error(e)


class VideoMaker(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

        self.daemon = True
        self.active = False
        self.name = __name__

    def run(self):
        log.info('Start VideoMaker')
        self.active = True
        while self.active:
            try:
                processes = []
                for comp in os.listdir(config['DATA_DIR']):
                    for user in os.listdir(os.path.join(config['DATA_DIR'], comp)):
                        try:
                            processes.append(VideoProcess(sema, comp, user))
                        except Exception as e:
                            log.error(e)
                for proc in processes:
                    proc.start()
                for proc in processes:
                    proc.join()
            except Exception as e:
                log.exception(e)
            self.sleep(config['VIDEO_LENGTH'])

    def stop(self):
        log.info('Stop VideoMaker')
        self.active = False

    def sleep(self, timeout):
        t = 0
        p = timeout - int(timeout)
        precision = p if p > 0 else 1
        while self.active and t < timeout:
            t += precision
            time.sleep(precision)


if __name__ == '__main__':
    VideoMaker().start()
