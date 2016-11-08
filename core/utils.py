# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import urllib, urllib2, os, sys
from cgi import parse_qs, escape
from UserDict import UserDict
import re
import shutil
import pwd


__denied_regex = re.compile(ur'[^./\wА-яЁё-]|[./]{2}', re.UNICODE | re.LOCALE)


def GET(target, post=None, cookie=None, headers=None, trys=1):    
    if not target:
        return
    if not headers:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.99 Safari/537.36'}
    req = urllib2.Request(url=target, headers=headers)
    
    if post:
        req.add_header("Content-type", "application/x-www-form-urlencoded")
        req.add_data(urllib.urlencode(post))
    if cookie:
        for coo in cookie.items():
            req.add_header('Cookie', "=".join(coo))
    
    resp = urllib2.urlopen(req, timeout=6)
    try:
        http = resp.read()
        return http
    finally:
        resp.close()
        

class QueryParam(UserDict):
   
    def __init__(self, environ, safe=False):
        self.safe = safe
        self.data = parse_qs(environ['QUERY_STRING'])
        if environ['REQUEST_METHOD'].upper() == 'POST':
            try:           
                request_body_size = int(environ.get('CONTENT_LENGTH', 0))
            except (ValueError):
                request_body_size = 0
            self.data.update(parse_qs(environ['wsgi.input'].read(request_body_size)))        
        
    
    def __getitem__(self, key):
        val = UserDict.__getitem__(self, key)[0]
        if self.safe:
            return safe_str('', val)
        return escape(val)
    
    
def safe_str(s):  
    res = s
    if not isinstance(res, unicode):
        res = res.decode('utf-8', errors='ignore')
    
    return __denied_regex.sub('', res).encode('utf-8', errors='ignore')
    
    
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
    [noDupes.append(i) for i in seq if noDupes.count(i) == 0]
    return noDupes


def add_userinfo(src_url, username, password):
    from urlparse import urlsplit
    
    url = urlsplit(src_url) 
    params = {'scheme':url.scheme, 'hostname':url.hostname, 'path':url.path}
    if url.query == '': 
        params['query'] = '' 
    else: 
        params['query'] = '?%s' % url.query
    if url.username is None:
        params['username'] = username
    else:
        params['username'] = url.username
    if url.password is None:
        params['password'] = password
    else:
        params['password'] = url.password
    if url.port is None:
        params['port'] = ''
    else:
        params['port'] = ':%i' % url.port 
    return "{scheme}://{username}:{password}@{hostname}{port}{path}{query}".format(**params)
       
       
def rListFiles(path):
        files = []
        for f in os.listdir(path):
            if os.path.isdir(os.path.join(path, f)):
                files += rListFiles(os.path.join(path, f))
            else:
                files.append(os.path.join(path, f))
        return files
    
    
def _get_uid(name):
    """Returns a gid, given a group name."""
    if name is None:
        return None
    try:
        result = pwd.getpwnam(name).pw_uid
    except AttributeError:
        result = None
    if result is not None:
        return result[2]
    return None


def _get_gid(name):
    """Returns a gid, given a group name."""
    if name is None:
        return None
    try:
        result = pwd.getpwnam(name).pw_gid
    except AttributeError:
        result = None
    if result is not None:
        return result[3]
    return None
    
    
def chown(path, user=None, group=None):
    """Change owner user and group of the given path.

    user and group can be the uid/gid or the user/group names, and in that case,
    they are converted to their respective uid/gid.
    """

    _user = user
    _group = group

    # -1 means don't change it
    if user is None:
        _user = -1
    # user can either be an int (the uid) or a string (the system username)
    elif isinstance(user, basestring):
        _user = _get_uid(user)
        if _user is None:
            raise LookupError("no such user: {!r}".format(user))

    if group is None:
        _group = -1
    elif not isinstance(group, int):
        _group = _get_gid(group)
        if _group is None:
            raise LookupError("no such group: {!r}".format(group))

    os.chown(path, _user, _group)
    
    
def makedirs(path, mode=0775, user=None, group=None):
    if not os.path.isdir(path):
        if not os.path.isdir(os.path.dirname(path)):
            makedirs(os.path.dirname(path), mode, user, group)
        
        os.mkdir(path)
        os.chmod(path, mode)
        chown(path, user, group)
        

def getUserName():
    if sys.platform.startswith('win'):
        return os.getenv('USERNAME')
    else:
        return os.getenv('USER')
    
    
def getCompName():
    if sys.platform.startswith('win'):
        return os.getenv('COMPUTERNAME')
    else:
        return os.getenv('HOSTNAME')

