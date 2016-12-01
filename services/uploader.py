# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os
import sys
import threading
import base64
import utils
import urllib2
import time
import logger
from config import config
import requests
from utils import fmt


log = logger.getLogger(config['NAME'], config['LOGLEVEL'])


class Uploader(threading.Thread):
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

        self.datadir = os.path.join(config['DATA_DIR'], config['NAME'])
        self.url = fmt('{URL}/upload', **config)
        self.cookie = {"username": base64.urlsafe_b64encode(utils.utf(utils.getUserName())),
                       'compname': base64.urlsafe_b64encode(utils.utf(utils.getCompName()))}
        self.auth = requests.auth.HTTPDigestAuth(*config['AUTH'])

        self.headers = {'user-agent': fmt("{NAME}/{VERSION}", **config)}

        utils.makedirs(self.datadir)

    def run(self):
        log.info(fmt('Start daemon: {0}', self.name))
        self.active = True
        prev_timeout, timeout = 13, 21
        while self.active:
            try:
                utils.makedirs(self.datadir)
                with requests.Session() as sess:
                    sess.auth = self.auth
                    sess.cookies = requests.utils.cookiejar_from_dict(self.cookie)
                    sess.timeout = (1, 5)
                    sess.headers = self.headers
                    for fn in (f for f in utils.rListFiles(self.datadir)
                               if not os.path.basename(f).startswith(config['EXCLUDE_CHR'])):
                        filename = fn.replace(self.datadir, '').replace('\\', '/').strip('/')
                        try:
                            with open(fn, 'rb') as fp:
                                data = {'filename': utils.utf(filename),
                                        'data': base64.urlsafe_b64encode(fp.read())}
                            log.debug(fmt('Try to upload: {fn}', fn=fn))
                            r = sess.post(self.url, data=data, verify=False)
                            r.raise_for_status()
                            if r.content == '1':
                                log.debug(fmt('Try to delete: {fn}', fn=fn))
                                os.unlink(fn)
                        except requests.exceptions.RequestException:
                            raise
                        except IOError as e:
                            log.error(e)

                        time.sleep(0.1)
                prev_timeout, timeout = 13, 21
            except Exception as e:
                if timeout < 60:
                    prev_timeout, timeout = timeout, prev_timeout + timeout
                log.error(e)

            time.sleep(timeout)

    def stop(self):
        log.info(fmt('Stop daemon: {0}', self.name))
        self.active = False


if __name__ == "__main__":
    t = Uploader()
    t.start()
    t.join()
