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
        self.daemon = True
        self.sema = sema
        self.comp = comp
        self.user = user

    def make_video(self):
        log.info(fmt('Make video: {comp}/{user}', comp=self.comp, user=self.user))
        src_dir = os.path.join(config['DATA_DIR'], self.comp, self.user, 'images')
        im_list = sorted(float(os.path.splitext(f)[0]) for f in os.listdir(src_dir) if f.endswith('.jpg'))

        if len(im_list) > 0:
            _params = dict(
                bt=datetime.datetime.fromtimestamp(im_list[0]),
                et=datetime.datetime.fromtimestamp(im_list[-1]),
                user=self.user,
                comp=self.comp)

            is_same_date = _params['et'].date() == datetime.date.today()

            if is_same_date:
                im_list = im_list[:-1]

            if not is_same_date or len(im_list) > 14:
                dst_file = os.path.join(
                    config['ARCHIVE_DIR'], fmt('{bt:%Y%m%d}/{comp}/{user}/movies/{bt:%H%M%S}-{et:%H%M%S}.mp4', **_params))
                utils.makedirs(os.path.dirname(dst_file), mode=0775)
                metadata = '-metadata creation_time="{dtime}"'.format(dtime=_params['bt'].strftime("%Y-%m-%d %H:%M:%S"))

                proc = subprocess.Popen(
                    fmt('ffmpeg -loglevel error -threads auto -y -f image2pipe -r 2 -c:v mjpeg -i - -c:v libx264 -preset ultrafast \
                        -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" \
                        -profile:v baseline -b:v 100k -qp 28 -an -r 25 {metadata} "{dst_file}"',
                        dst_file=dst_file,
                        metadata=metadata),
                    shell=True, close_fds=True, stdin=subprocess.PIPE)
                with proc.stdin:
                    log.info(fmt('Add images: {comp}/{user}', comp=self.comp, user=self.user))
                    for f in im_list:
                        try:
                            fn = os.path.join(src_dir, fmt("{fn}.jpg", fn=f))
                            log.debug(fmt('Add: {fn}', fn=fn))
                            proc.stdin.write(open(fn, 'rb').read())
                        except Exception as e:
                            log.error(e)
                proc.wait()
                if proc.returncode != 0:
                    log.error(fmt('Process of {comp}/{user} return {code}', comp=self.comp, user=self.user, code=proc.returncode))
    #                 raise subprocess.CalledProcessError(proc.returncode, str(proc.pid))
                log.info(fmt('Delete images: {comp}/{user}', comp=self.comp, user=self.user))
                for f in im_list:
                    try:
                        fn = os.path.join(src_dir, fmt("{fn}.jpg", fn=f))
                        log.debug(fmt('Delete: {fn}', fn=fn))
                        os.unlink(fn)
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
                    try:
                        proc.join(config['VIDEO_LENGTH'])
                        proc.terminate()
                    except Exception as e:
                        log.error(e)
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
        return self.active


if __name__ == '__main__':
    vm = VideoMaker()
    vm.start()
    vm.join()
