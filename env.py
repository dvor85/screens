# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os
import threading
import utils
import logger
import time
import requests
import base64
from config import config


log = logger.getLogger(config['NAME'], config['LOGLEVEL'])


class Env(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = False
        self.datadir = os.path.join(utils.getDataDIR(), '.{NAME}'.format(**config))
        self.url = config['URL'] + '/env'
        self.cookie = {"username": base64.urlsafe_b64encode(utils.getUserName()),
                       'compname': base64.urlsafe_b64encode(utils.getCompName())}
        self.auth = requests.auth.HTTPDigestAuth(*config['AUTH'])
        global log

        utils.makedirs(self.datadir)

    def run(self):
        print requests.get(self.url, cookies=self.cookie, auth=self.auth, timeout=(1, 5)).text
#             time.sleep(2)


if __name__ == "__main__":
    Env().start()
