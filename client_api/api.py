# -*- coding: utf-8 -*-
# from __future__ import unicode_literals
import os
import sys
from jsonrpc2 import JsonRpcApplication

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from config import config  # @IgnorePep8
from core import logger, utils  # @IgnorePep8


log = logger.getLogger(config['NAME'], config['LOGLEVEL'])
fmt = utils.fmt


def application(env, start_response):
    from client_api.hello import Hello
    from client_api.script import Script
    from client_api.image import ImageStore
    from client_api.upload import Upload
    app = JsonRpcApplication(rpcs=dict(hello=Hello(env),
                                       script=Script(env),
                                       image=ImageStore(env),
                                       upload=Upload(env)))
    return app(env, start_response)

if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8080, application)
    log.debug("Serving on port 8080...")
    httpd.serve_forever()
