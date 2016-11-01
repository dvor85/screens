# -*- coding: utf-8 -*-

import os, sys
import datetime, time
import threading, multiprocessing
import subprocess

from core import logger, defines
from core.config import config



selfdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
log = logger.getLogger(__name__, config['LOGLEVEL'])
sema = multiprocessing.Semaphore(8)



class VideoProcess(multiprocessing.Process):
    def __init__(self, sema, comp, user):
        multiprocessing.Process.__init__(self)
        self.sema = sema
        self.comp = comp
        self.user = user
        
        
    def make_video(self):
        log.info('Make video: {}/{}'.format(self.comp, self.user))
        _params = dict(
            src_dir = os.path.join(config['DATA_DIR'], self.comp, self.user, 'images'),
            dst_file = os.path.join(config['ARCHIVE_DIR'], self.comp, self.user)
        )
        im_list = sorted([float(os.path.splitext(f)[0]) for f in os.listdir(_params['src_dir']) if f.endswith('.jpg')])
        
        if len(im_list) > 15:
            _bt = datetime.datetime.fromtimestamp(im_list[0])
            _et = datetime.datetime.fromtimestamp(im_list[-1])
            _params['dst_file'] = os.path.join(_params['dst_file'],'{:%Y%m%d}'.format(_bt))
            _params['dst_file'] = os.path.join(_params['dst_file'],'{:%H%M%S}-{:%H%M%S}.mp4'.format(_bt, _et))
            defines.makedirs(os.path.dirname(_params['dst_file']))
            proc = subprocess.Popen('avconv -threads auto -y -f image2pipe -r 2 -c:v mjpeg -i - -c:v libx264 -preset ultrafast -profile:v baseline -b:v 100k -qp 28 -an -r 25 {dst_file}'.format(**_params), shell=True, close_fds=True, stdin=subprocess.PIPE)
            with proc.stdin:
                log.debug('Add images to process stdin')
                for f in im_list:
                    try:
                        proc.stdin.write(open(os.path.join(_params['src_dir'], "{}.jpg".format(f)), 'rb').read())
                    except Exception as e:
                        log.error(e)
            proc.wait()
            if proc.returncode != 0:
                raise subprocess.CalledProcessError(proc.returncode, str(proc.pid))
            log.debug('Delete images')
            for f in im_list:
                try:
                    os.unlink(os.path.join(_params['src_dir'], "{}.jpg".format(f)))
                except Exception as e:
                    log.error(e)
        
        
    def run(self):        
        with self.sema:
            self.make_video()
                
        

class VideoMaker(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        
        self.daemon = False
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
            time.sleep(60)
            
            
    def stop(self):
        log.info('Stop VideoMaker')
        self.active = False
        


if __name__ == '__main__':
    VideoMaker().start()
        