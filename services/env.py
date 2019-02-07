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
from utils import fmt


log = logger.getLogger(config['NAME'], config['LOGLEVEL'])


class Env(threading.Thread):

    def __init__(self):
        log.info(fmt('Init daemon: {0}', __name__))
        threading.Thread.__init__(self)
        self.daemon = False
        self.datadir = os.path.join(config['HOME_DIR'], config['NAME'])
        self.url = config['URL'] + '/env'
        self.cookie = {"username": base64.urlsafe_b64encode(utils.get_user_name().encode('utf8')),
                       'compname': base64.urlsafe_b64encode(utils.get_comp_name().encode('utf8'))}
        self.auth = requests.auth.HTTPDigestAuth(*config['AUTH'])
        global log

        utils.makedirs(self.datadir)

    def run(self):
        print requests.get(self.url, cookies=self.cookie, auth=self.auth, timeout=(1, 5)).text
#             time.sleep(2)


if __name__ == "__main__":
    Env().start()
