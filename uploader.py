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


log = logger.getLogger(config['NAME'], config['LOGLEVEL'])


class Uploader(threading.Thread):
    """
    Выгружает файлы из data_dir на сервер каждые 10с, за исключением файлов начинающихся с "-".
    Все выгруженные файлы удаляются.

    Upload all of data dir every 10s, except files with leading "-".
    All uploaded files are removed.
    """

    def __init__(self):
        threading.Thread.__init__(self)
        self.name = __name__
        self.daemon = False
        self.active = False

        self.datadir = os.path.join(utils.getDataDIR(), '.{NAME}'.format(**config))
        self.url = config['URL'] + '/upload'
        self.cookie = {"username": base64.urlsafe_b64encode(utils.getUserName()),
                       'compname': base64.urlsafe_b64encode(utils.getCompName())}
        self.auth = requests.auth.HTTPDigestAuth(*config['AUTH'])

        self.headers = {'user-agent': "{NAME}/{VERSION}".format(**config)}

        utils.makedirs(self.datadir)

    def run(self):
        log.info('Start daemon: {0}'.format(self.name))
        self.active = True
        while self.active:
            try:
                utils.makedirs(self.datadir)
                with requests.Session() as sess:
                    sess.auth = self.auth
                    sess.cookies = requests.utils.cookiejar_from_dict(self.cookie)
                    sess.timeout = (1, 5)
                    sess.headers = self.headers
                    for fn in [f for f in utils.rListFiles(self.datadir) if not os.path.basename(f).startswith('-')]:
                        filename = fn.replace(self.datadir, '').replace('\\', '/').strip('/')
                        try:
                            with open(fn, 'rb') as fp:
                                data = {'filename': filename,
                                        'data': base64.urlsafe_b64encode(fp.read())}
                            log.debug('Try to upload: {0}'.format(fn))
                            r = sess.post(self.url, data=data, verify=False)
                            r.raise_for_status()
                            if r.content == '1':
                                log.debug('Try to delete: {0}'.format(fn))
                                os.unlink(fn)
                        except requests.exceptions.RequestException:
                            raise
                        except IOError as e:
                            log.error(e)

                        time.sleep(0.1)
            except Exception as e:
                log.error(e)

            time.sleep(10)

    def stop(self):
        self.active = False


if __name__ == "__main__":
    selfdir = os.path.abspath(os.path.dirname(__file__))
    Uploader(selfdir).start()
#     for f in utils.rListFiles(selfdir):
#         log.debug(f)
#     print Uploader(selfdir).rgetFiles(selfdir)
