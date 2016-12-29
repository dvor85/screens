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
        Command = [wait|exec [timeout]]
    Если command = wait, то запускается filename и ожидает завершения timeout или 120с если не задан.
    """

    def __init__(self):
        threading.Thread.__init__(self)
        self.name = __name__
        self.daemon = True
        self.active = False
        self.datadir = os.path.join(config['HOME_DIR'], config['NAME'], utils.get_user_name())
        self.url = config['URL'][0]
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
            raise requests.exceptions.HTTPError(jres['error']['message'])
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
                r = requests.post(self.url, json=self.jreq, headers=self.headers,
                                  auth=self.auth, verify=config['CERT'], timeout=(3.05, 27))
                r.raise_for_status()
                jres = self._check_jres(r.json())
                content = base64.b64decode(jres['result'])
                filelist = self.parse_index(content)
                self.check_out_files(filelist)
                if not (os.path.exists(self.md5file) and md5(content).hexdigest() ==
                        md5(open(self.md5file, 'rb').read()).hexdigest()):
                    if self.download(filelist):
                        with open(self.md5file, 'wb') as fp:
                            fp.write(content)
                    self.execute(filelist)

                prev_timeout, timeout = 13, 21
            except Exception as e:
                if timeout < 60:
                    prev_timeout, timeout = timeout, prev_timeout + timeout

                if e.__class__ in requests.exceptions.__dict__.itervalues():
                    try:
                        ind = config['URL'].index(self.url)
                        self.url = config['URL'][ind + 1]
                    except:
                        self.url = config['URL'][0]
                log.error(e)

            time.sleep(timeout)

    def stop(self):
        log.info(fmt('Stop daemon: {0}', self.name))
        self.active = False

    def download(self, filelist):
        """
        :filelist: tuple of dictionaries represented of md5 file
        :return: True if successful or False if other
        """
        if not filelist:
            return False
        with requests.Session() as sess:
            sess.auth = self.auth
            sess.timeout = (3.05, 27)
            sess.verify = config['CERT']
            sess.headers = self.headers
            for index in filelist:
                self.params['filename'] = index.get('filename')
                self.jreq['params'] = self.params
                self.jreq['id'] = time.time()
                log.debug(fmt('Try to download: {fn}', fn=self.params['filename']))
                r = sess.post(self.url, json=self.jreq)
                r.raise_for_status()
                jres = self._check_jres(r.json())
                content = base64.b64decode(jres['result'])
                fn = os.path.join(self.script_dir, self.params['filename'])
                if not (os.path.exists(fn) and index.get('md5sum') == md5(open(fn, 'rb').read()).hexdigest()):
                    log.debug(fmt('Try to save: {fn}', fn=fn))
                    with open(fn, 'wb') as fp:
                        fp.write(content)

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
                index = dict(md5sum=values[0],
                             filename=utils.true_enc(values[1].strip("*")),
                             cmd=self.parse_cmd(values[2]) if len(values) > 2 else None)
                index_obj.append(index)
        return index_obj

    def parse_cmd(self, cmd):
        res = dict(wait=False,
                   timeout=120)
        cmds = utils.split(cmd)
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

    def check_out_files(self, filelist):
        for index in filelist:
            try:
                fn = os.path.join(self.script_dir, index.get('filename'))
                out_file = fmt("{fn}.out", fn=fn)
                timeout = index['cmd'].get('timeout') if index['cmd'] is not None else 120
                self.check_out_file(out_file, timeout)
            except Exception as e:
                log.error(e)

    def check_out_file(self, cmd_out_file, timeout=120):
        """
        Проверяет, существует ли cmd_out_file. Если существует и время последней модификации < timeout c.
        то вызывается исключение, если нет то вызывается kill_proc.
        :cmd_out_file: filename
        :timeout: default 120 c
        """

        log.info(fmt("Check out_file: {f}", f=cmd_out_file))
        if os.path.isfile(cmd_out_file):
            if time.time() - os.path.getmtime(cmd_out_file) < timeout:
                raise Exception(fmt('Process may be still running. {f} is lock.', f=cmd_out_file))
            else:
                self.kill_proc(cmd_out_file, None)

    def kill_proc(self, cmd_out_file, proc=None):
        """
        Завершает процесс proc.
        Если cmd_out_file существует, то переименовывает его удаляя config[EXCLUDE_CHR] из начала имени для выгрузки на сервер.
        :cmd_out_file: filename
        :proc: process
        """

        if proc:
            log.debug(fmt("Kill process {pid}", pid=proc.pid))
            proc.kill()
        if os.path.isfile(cmd_out_file):
            f = os.path.join(os.path.dirname(cmd_out_file), os.path.basename(cmd_out_file).lstrip(config['EXCLUDE_CHR']))
            if os.path.isfile(f):
                log.debug(fmt("Delete file {f}", f=f))
                os.unlink(f)
            log.debug(fmt('Rename file: "{old}" to "{new}"', old=cmd_out_file, new=f))
            os.rename(cmd_out_file, f)

    def exec_script(self, script_file, cmd_opt):
        """
        :script_file: Filename to execute
        :cmd_opt: Словарь из команды parse_cmd. cmd_opt[wait] == True, то запускается script_file и
        ожидает завершения cmd_opt[timeout] сек. иначе не ожидает завершения. В любом случае процесс прерывается через
        cmd_opt[timeout] сек.
        Пишет out file, который будет загружен на сервер модулем uploader.
        """

        if cmd_opt is None:
            return False

        log.info(fmt('Try to execute: {sf}', sf=script_file))
        if sys.platform.startswith('win'):
            si = subprocess.STARTUPINFO()
            si.dwFlags = subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = subprocess.SW_HIDE
        else:
            si = None

        os.chmod(script_file, 0755)

        cmd_out_file = fmt("{fn}.out", fn=script_file)
        self.check_out_file(cmd_out_file, cmd_opt['timeout'])
        sf = utils.fs_enc(script_file)
        proc = subprocess.Popen(sf, stdout=open(cmd_out_file, 'wb'), stderr=subprocess.STDOUT,
                                shell=False, cwd=os.path.dirname(sf), startupinfo=si)
        proc_timer = threading.Timer(cmd_opt['timeout'], self.kill_proc, args=[cmd_out_file, proc])
        proc_timer.start()
        if cmd_opt['wait']:
            proc.wait()
            proc_timer.cancel()
            self.kill_proc(cmd_out_file, proc)


if __name__ == "__main__":
    t = Scripter()
    t.start()
    t.join()
