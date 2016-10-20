# -*- coding: utf-8 -*-

import urllib2, os

def GET(target, post=None, cookie=None, headers=None, trys=1):    
    if not target:
        return
    if not headers:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.99 Safari/537.36'}
    req = urllib2.Request(url=target, data=post, headers=headers)
    
    if post:
        req.add_header("Content-type", "application/x-www-form-urlencoded")
    if cookie:
        for coo in cookie:
            req.add_header('Cookie', coo)
    
    resp = urllib2.urlopen(req, timeout=6)
    try:
        http = resp.read()
        return http
    finally:
        resp.close()
        
def rListFiles(path):
        files = []
        for f in os.listdir(path):
            if os.path.isdir(os.path.join(path, f)):
                files += rListFiles(os.path.join(path, f))
            else:
                files.append(os.path.join(path, f))
        return files
