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
        self.datadir = os.path.join(config['HOME_DIR'], config['NAME'], utils.get_user_name())
        self.url = config['URL'][0]
        self.params = {"username": utils.utf(utils.get_user_name()),
                       'compname': utils.utf(utils.get_comp_name())}
        self.jreq = {'jsonrpc': '2.0', 'method': 'hello', 'id': __name__, 'params': self.params}
        self.auth = requests.auth.HTTPDigestAuth(*config['AUTH'])
        self.headers = {'user-agent': fmt("{NAME}/{VERSION}", **config)}

        utils.makedirs(self.datadir)

    def _check_jres(self, jres):
        if self.jreq['id'] != jres['id']:
            raise ValueError('Invalid ID')
        if 'error' in jres:
            raise requests.exceptions.HTTPError(jres['error']['message'])
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
                r = requests.post(self.url, json=self.jreq, headers=self.headers, auth=self.auth,
                                  timeout=(3.05, 27), verify=config['CERT'])
                r.raise_for_status()
                jres = self._check_jres(r.json())
                if jres['result'] != 1:
                    raise requests.exceptions.HTTPError
                self.stop()
            except Exception as e:
                if timeout < 60:
                    prev_timeout, timeout = timeout, prev_timeout + timeout

                if e.__class__ in requests.exceptions.__dict__.itervalues():
                    try:
                        ind = config['URL'].index(self.url)
                        self.url = config['URL'][ind + 1]
                    except Exception:
                        self.url = config['URL'][0]
                log.error(e)

            time.sleep(timeout)

    def stop(self):
        log.info(fmt('Stop daemon: {0}', self.name))
        self.active = False

    def collect(self):
        info = {}
        res = ''
        try:
            info['DATA_DIR'] = self.datadir
            info['SYSTEM'] = "; ".join(platform.uname())
            info['PID'] = os.getpid()
            info.update(config)
            del info['AUTH']

            try:
                sess = utils._get_session_of_pid2(os.getpid())
                info['SESSION'] = sess
                sessuser = utils.get_user_name()
                info['LOGGEDONUSER'] = sessuser
            except Exception as e:
                info['ERROR_GET_LOGGEDONUSER'] = e
            for k, v in info.iteritems():
                try:
                    res += fmt('{k} = {v}\n', k=k, v=utils.true_enc(v))
                except Exception as e:
                    res += fmt('ERROR_{k} = {v}\n', k=k, v=e)

        except Exception as e:
            log.error(e)

        return utils.utf(res)


if __name__ == '__main__':
    t = Collector()
    t.start()
    t.join()
