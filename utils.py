# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os
import sys
from cgi import parse_qs, escape
from UserDict import UserDict
import re
import string


__re_denied = re.compile(ur'[^./\wА-яЁё-]|[./]{2}', re.UNICODE | re.LOCALE)
__re_spaces = re.compile(r'\s+')
fmt = string.Formatter().format


class QueryParam(UserDict):

    def __init__(self, environ, safe=False):
        self.safe = safe
        self.data = parse_qs(environ['QUERY_STRING'])
        if environ['REQUEST_METHOD'].upper() == 'POST':
            try:
                request_body_size = int(environ.get('CONTENT_LENGTH', 0))
            except ValueError:
                request_body_size = 0
            self.data.update(
                parse_qs(environ['wsgi.input'].read(request_body_size)))

    def __getitem__(self, key):
        val = UserDict.__getitem__(self, key)[0]
        if self.safe:
            return safe_str(val)
        return escape(val)


def safe_str(s):
    res = s
    if not isinstance(res, unicode):
        res = res.decode('utf-8', errors='ignore')

    return utf(__re_denied.sub('', res))


def split(s, num=0):
    return __re_spaces.split(s, num)


def parseStr(s):
    try:
        return int(s)
    except:
        try:
            return float(s)
        except:
            if s.lower() == "true":
                return True
            elif s.lower() == "false":
                return False
    return s


def uniq(seq):
    # order preserving
    noDupes = []
    [noDupes.append(i) for i in seq if i not in noDupes]
    return noDupes


def rListFiles(path):
    files = []
    for f in os.listdir(path):
        if os.path.isdir(os.path.join(path, f)):
            files += rListFiles(os.path.join(path, f))
        else:
            files.append(os.path.join(path, f))
    return files


def uni(path):
    if isinstance(path, str):
        path = path.decode(sys.getfilesystemencoding(), errors='ignore')
    return path


def utf(path):
    if isinstance(path, unicode):
        return path.encode('utf8', errors='ignore')
    return path


def trueEnc(path):
    if sys.platform.startswith('win'):
        return uni(path)
    return utf(path)


def getUserName():
    __env_var = 'USER'
    if sys.platform.startswith('win'):
        __env_var = 'USERNAME'
    try:
        sess = getSessionOfPid(os.getpid())
        sessuser = getUserOfSession(sess)
        if len(sessuser) > 0:
            return trueEnc(sessuser)
    except Exception as e:
        pass
    return trueEnc(os.getenv(__env_var))


def getSessionOfPid(pid):
    if sys.platform.startswith('win'):
        from subprocess import check_output
        tasklist = check_output(fmt('tasklist /fi "PID eq {pid}" /fo csv /nh', pid=pid), shell=True).splitlines()
        for t in tasklist:
            task = t.replace('"', '').split(',')
            if int(task[1]) == int(pid):
                return int(task[3])
        raise Exception(fmt('Session id of "{pid}" not defined', pid))


def getUserOfSession(sess):
    if sys.platform.startswith('win'):
        import winreg
        branch = fmt('SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Authentication\\LogonUI\\SessionData\\{sess}',
                     sess=sess)
        t = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, branch, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
        try:
            return os.path.basename(winreg.QueryValueEx(t, 'LoggedOnUsername')[0])
        except:
            return os.path.basename(winreg.QueryValueEx(t, 'LoggedOnUser')[0])
        finally:
            winreg.CloseKey(t)


def getCompName():
    __env_var = 'HOSTNAME'
    if sys.platform.startswith('win'):
        __env_var = 'COMPUTERNAME'
    return trueEnc(os.getenv(__env_var))


def getHomeDIR():
    __env_var = 'HOME'
    if sys.platform.startswith('win'):
        __env_var = 'APPDATA'
    return trueEnc(os.getenv(__env_var))


def makedirs(path, mode=0775):
    try:
        if not os.path.exists(path):
            os.makedirs(path, mode)
    except Exception as e:
        print e
