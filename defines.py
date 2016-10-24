# -*- coding: utf-8 -*-

import urllib, urllib2, os, sys

from cgi import parse_qs, escape
from UserDict import UserDict



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
        

class Request(UserDict):
   
    def __init__(self, environ):
        
        self.data = parse_qs(environ['QUERY_STRING'])
        if environ['REQUEST_METHOD'].upper() == 'POST':
            try:           
                request_body_size = int(environ.get('CONTENT_LENGTH', 0))
            except (ValueError):
                request_body_size = 0
            self.data.update(parse_qs(environ['wsgi.input'].read(request_body_size)))        
        
    
    def __getitem__(self, key):
        return escape(UserDict.__getitem__(self, key)[0])


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
    

def makedirs(path):
    try:
        os.makedirs(path)
    except:
        pass


def getUserName():
    if sys.platform.startswith('win'):
        return os.getenv('USERNAME')
    else:
        return os.getenv('USER')
    
    