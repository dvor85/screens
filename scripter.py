# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os
import sys
import threading
import utils
import time
import subprocess
import base64
from hashlib import md5
import logger
from config import config
import requests


log = logger.getLogger(config['NAME'], config['LOGLEVEL'])
fmt = utils.fmt


class Scripter(threading.Thread):
    """
    Скачивает -script.md5 со списком файлов каждые 10с.
        Формат -script.md5:
        md5sum filename command
        Command = [wait [timeout]|nowait|None]
    Если command = wait, то запускается filename и ожидает завершения timeout или 60с если не задан.

    Download -script.md5 with list of files every 10s.
        Format: md5sum filename command
        Command = [wait [timeout]|nowait|None]
    If command is "wait" then exec filename and wait for complete timeout or 60 seconds if not specified
    """

    def __init__(self):
        threading.Thread.__init__(self)
        self.name = __name__
        self.daemon = False
        self.active = False
        self.datadir = os.path.join(utils.getDataDIR(), fmt('.{NAME}', **config))
        self.url = fmt('{URL}/script', **config)

        self.script_dir = os.path.join(self.datadir, 'script')
        self.md5file = os.path.join(self.script_dir, '-script.md5')

        utils.makedirs(self.script_dir)
        utils.makedirs(self.datadir)
        self.cookie = {"username": base64.urlsafe_b64encode(utils.utf(utils.getUserName())),
                       'compname': base64.urlsafe_b64encode(utils.utf(utils.getCompName()))}
        self.auth = requests.auth.HTTPDigestAuth(*config['AUTH'])

        self.headers = {'user-agent': fmt("{NAME}/{VERSION}", **config)}

    def run(self):
        log.info(fmt('Start daemon: {0}', self.name))
        self.active = True
        while self.active:
            try:
                utils.makedirs(os.path.dirname(self.md5file))
                utils.makedirs(self.datadir)
                data = {'filename': os.path.basename(self.md5file)}
                log.debug(fmt('Try to download: {0}', data.get('filename')))
                r = requests.post(self.url, data=data, cookies=self.cookie, headers=self.headers,
                                  auth=self.auth, verify=False, timeout=(1, 5))
                r.raise_for_status()
                index_content = r.content
                if not (os.path.exists(self.md5file) and md5(index_content).hexdigest() ==
                        md5(open(self.md5file, 'rb').read()).hexdigest()):
                    indexlist = self.parseIndex(index_content)
                    if self.download(indexlist):
                        with open(self.md5file, 'wb') as fp:
                            fp.write(index_content)

            except Exception as e:
                log.error(e)

            time.sleep(10)

    def download(self, indexlist):
        """
        :indexlist: tuple of dictionaries represented of md5 file
        :return: True if successful or False if other
        """
        if not indexlist:
            return False
        with requests.Session() as sess:
            sess.auth = self.auth
            sess.cookies = requests.utils.cookiejar_from_dict(self.cookie)
            sess.timeout = (1, 5)
            sess.headers = self.headers
            for index in indexlist:
                try:
                    log.debug(fmt('Try to download: {0}', index.get('filename')))
                    r = sess.post(self.url, data=index, verify=False)
                    r.raise_for_status()
                    content = r.content
                    fn = os.path.join(self.script_dir, index.get('filename'))
                    if not (os.path.exists(fn) and index.get('md5sum') == md5(open(fn, 'rb').read()).hexdigest()):
                        log.debug(fmt('Try to save: {0}', fn))
                        with open(fn, 'wb') as fp:
                            fp.write(content)

                    self.exec_script(fn, index.get('cmd'))
                except Exception as e:
                    log.error(e)
                    return False
            return True

    def parseIndex(self, indexdata):
        """
        :indexdata: raw data of md5 file
        :return: tuple of dictionaries represented of md5 file
        """
        index_obj = []
        for line in indexdata.splitlines():
            values = line.split(' ', 2)
            if len(values) > 1:
                index = {"md5sum": values[0],
                         "filename": utils.trueEnc(values[1].strip("*")),
                         "cmd": values[2] if len(values) > 2 else None}
                index_obj.append(index)
        return index_obj

    def stop(self):
        self.active = False

    def exec_script(self, script_file, cmd):
        """
        :script_file: Filename to execute
        :cmd: Если command = wait, то запускается script_file и ожидает завершения timeout или 60с если не задан.
        По окончании пишет out file, который будет загружен на сервер модулем uploader.

        Command. If None then return. If it's "wait" then wait for complete and write out file,
        which will be upload to server.
        :raise  CalledProcessError if return code is not zero
        """
        if not cmd:
            return False

        log.info(
            fmt('Try to execute: {0} with command: {1}', script_file, cmd))
        if sys.platform.startswith('win'):
            si = subprocess.STARTUPINFO()
            si.dwFlags = subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = subprocess.SW_HIDE
        else:
            si = None

        os.chmod(script_file, 0755)

        cmds = cmd.split(' ')
        timeout = utils.parseStr(cmds[1]) if len(cmds) > 1 else 60

        proc = subprocess.Popen(script_file, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                shell=False, cwd=os.path.dirname(script_file), startupinfo=si)
        threading.Timer(timeout, proc.kill).start()
        if cmd.startswith('wait'):
            script_out = proc.communicate()[0]
            f = os.path.join(
                os.path.dirname(script_file), os.path.basename(script_file).lstrip('-'))
            cmd_out_file = fmt("{0}.out", f)
            log.debug(fmt('Try to save: {0}', cmd_out_file))
            with open(cmd_out_file, 'wb') as fp:
                fp.write(script_out)

            if proc.returncode != 0:
                raise subprocess.CalledProcessError(
                    returncode=proc.returncode, cmd=script_file, output=script_out)


if __name__ == "__main__":
    selfdir = os.path.abspath(os.path.dirname(__file__))
    Scripter(selfdir).start()
