# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os
import sys
import signal
import time
from screenshoter import Screenshoter
from scripter import Scripter
from uploader import Uploader
import logger
from config import config
import utils
import collectcfg


log = logger.getLogger(config['NAME'], config['LOGLEVEL'])
fmt = utils.fmt


class SPclient():

    def __init__(self):
        self.datadir = os.path.join(utils.getDataDIR(), fmt('.{NAME}', **config))
        self.daemons = []
        signal.signal(signal.SIGTERM, self.signal_term)

        self.daemons.append(Screenshoter())
        self.daemons.append(Scripter())
        self.daemons.append(Uploader())

        utils.makedirs(self.datadir)

    def signal_term(self, signum, frame):
        log.debug(fmt('Get Signal: {0}', signum))
        self.stop()

    def start(self):
        collectcfg.Collector().save()
        for d in self.daemons:
            d.start()
#         self.wait_termination()

    def stop(self):
        for d in self.daemons:
            d.stop()

    def wait_termination(self):
        for d in self.daemons:
            try:
                d.join()
            except:
                pass


if __name__ == '__main__':
    log.debug(fmt("PID={0}", os.getpid()))
    SPclient().start()

    log.debug('Exit')
