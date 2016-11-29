# encoding: utf8

import os
from config import config
import utils
import base64
import logger
import threading
import requests
import time

log = logger.getLogger(config['NAME'], config['LOGLEVEL'])
fmt = utils.fmt


class Collector(threading.Thread):
    """
    Собирает информацию о конфигурации клиента и отправляет на сервер.
    После успешной отправки - завершает свою работу.
    """

    def __init__(self):
        threading.Thread.__init__(self)
        self.name = __name__
        self.daemon = True
        self.active = False
        self.datadir = os.path.join(config['DATA_DIR'], config['NAME'])
        self.url = fmt('{URL}/hello', **config)
        self.cookie = {"username": base64.urlsafe_b64encode(utils.utf(utils.getUserName())),
                       'compname': base64.urlsafe_b64encode(utils.utf(utils.getCompName()))}
        self.auth = requests.auth.HTTPDigestAuth(*config['AUTH'])
        self.headers = {'user-agent': fmt("{NAME}/{VERSION}", **config)}

        utils.makedirs(self.datadir)

    def run(self):
        log.info(fmt('Start daemon: {0}', self.name))
        self.active = True
        self.info = self.collect()
        data = {'data': base64.urlsafe_b64encode(self.info)}
        prev_timeout, timeout = 13, 21
        while self.active:
            try:
                r = requests.post(self.url, data=data, cookies=self.cookie, headers=self.headers, auth=self.auth,
                                  timeout=(1, 5), verify=False)
                r.raise_for_status()
                if r.content != '1':
                    raise requests.exceptions.HTTPError
                self.stop()
            except Exception as e:
                if timeout < 60:
                    prev_timeout, timeout = timeout, prev_timeout + timeout
                log.debug(e)

            time.sleep(timeout)

    def stop(self):
        log.info(fmt('Stop daemon: {0}', self.name))
        self.active = False

    def collect(self):
        info = {}
        info.update(config)
        del info['AUTH']
        return "\n".join(fmt('{k} = {v}', k=k, v=v) for k, v in info.iteritems())
