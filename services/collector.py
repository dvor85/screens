# encoding: utf8

import os
from config import config
import utils
import base64
import logger
import threading
import requests
import time
import platform
from utils import fmt

log = logger.getLogger(config['NAME'], config['LOGLEVEL'])


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
        self.datadir = os.path.join(config['HOME_DIR'], config['NAME'], utils.getUserName())

        self.params = {"username": utils.utf(utils.getUserName()),
                       'compname': utils.utf(utils.getCompName())}
        self.jreq = {'jsonrpc': '2.0', 'method': 'hello', 'id': __name__, 'params': self.params}
        self.auth = requests.auth.HTTPDigestAuth(*config['AUTH'])
        self.headers = {'user-agent': fmt("{NAME}/{VERSION}", **config)}

        utils.makedirs(self.datadir)

    def _check_jres(self, jres):
        if self.jreq['id'] != jres['id']:
            raise ValueError('Invalid ID')
        if 'error' in jres:
            raise Exception(jres['error']['message'])
        return jres

    def run(self):
        log.info(fmt('Start daemon: {0}', self.name))
        self.active = True
        self.info = self.collect()
        self.params['data'] = base64.b64encode(self.info)
        self.jreq['params'] = self.params
        prev_timeout, timeout = 13, 21
        while self.active:
            try:
                self.jreq['id'] = time.time()
                r = requests.post(config['URL'], json=self.jreq, headers=self.headers, auth=self.auth,
                                  timeout=(1, 5), verify=False)
                r.raise_for_status()
                jres = self._check_jres(r.json())
                if jres['result'] != 1:
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
        info['DATA_DIR'] = self.datadir
        info['SYSTEM'] = utils.trueEnc("; ".join(platform.uname()))
        info['PID'] = os.getpid()
#         try:
#             sess = utils.getSessionOfPid(os.getpid())
#             info['sess'] = sess
#             sessuser = utils.getUserOfSession(sess)
#             info['sessuser'] = utils.trueEnc(sessuser)
#         except Exception as e:
#             info['get_sessuser_error'] = e
        info.update(config)
        del info['AUTH']
        return utils.utf("\n".join(fmt('{k} = {v}', k=k, v=v) for k, v in info.iteritems()))

if __name__ == '__main__':
    t = Collector()
    t.start()
    t.join()
