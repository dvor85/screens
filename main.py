#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os
import time
import signal
from config import config
from core import logger, utils
from service.videomaker import VideoMaker
from service.arcrotator import ArchiveRotator
from core.init_core import Generator


log = logger.getLogger(config['NAME'], config['LOGLEVEL'])
fmt = utils.fmt


class Starter():

    def __init__(self):
        signal.signal(signal.SIGTERM, self.signal_term)
        self.active = False
#         self.parse_options()
        self.daemons = []
        self.daemons.append(VideoMaker())
        self.daemons.append(ArchiveRotator())
        Generator().main()

    def signal_term(self, signum, frame):
        log.debug(fmt('Get Signal: {0}', signum))
        self.stop()

    def start(self):
        log.info('Start daemons')
        self.active = True
        for d in self.daemons:
            d.start()

    def stop(self):
        log.info('Stop daemons')
        self.active = False
        for d in self.daemons:
            d.stop()

    def sleep(self, timeout):
        t = 0
        p = timeout - int(timeout)
        precision = p if p > 0 else 1
        while self.active and t < timeout:
            t += precision
            time.sleep(precision)

    def wait_termination(self):
        log.debug('Wait for termination')
        while self.active:
            self.sleep(1)
        for d in self.daemons:
            try:
                log.debug(fmt('Wait for {0}', d.getName()))
                d.join()
            except Exception as e:
                log.exception(e)


if __name__ == '__main__':

    log.debug(fmt("PID={0}", os.getpid()))
    starter = Starter()
    starter.start()

    starter.wait_termination()
    log.info('Exit')
