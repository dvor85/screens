# -*- coding: utf-8 -*-
# from __future__ import unicode_literals
from cgi import escape
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import config  # @IgnorePep8
from core import logger, utils  # @IgnorePep8


log = logger.getLogger(config['NAME'], config['LOGLEVEL'])
fmt = utils.fmt


def application(env, start_response):

    try:
        status = '200 OK'
        body = ''
        path_info = escape(env['PATH_INFO'])

        if path_info == "/image":
            from client_api.image import ImageStore
            body = ImageStore(env).main()
        elif path_info == "/script":
            from client_api.script import Script
            body = Script(env).main()
        elif path_info == "/upload":
            from client_api.upload import Upload
            body = Upload(env).main()
        elif path_info == "/hello":
            from client_api.hello import Hello
            body = Hello(env).main()

        else:
            status = '404 Error'
            body = status

    except Exception as e:
        status = '500 Error'
        body = status
        log.error(e)
    finally:
        if body is None:
            body = ''
        body = utils.utf(body)

        start_response(status, [('Content-type', 'text/plain'),
                                ('Content-Length', str(len(body)))])
    return [body]


if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8080, application)
    log.debug("Serving on port 8080...")
    httpd.serve_forever()
