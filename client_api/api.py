# -*- coding: utf-8 -*-
# from __future__ import unicode_literals
import os
import sys
from jsonrpc2 import JsonRpcApplication

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.dirname(__file__))

from config import config  # @IgnorePep8
from core import logger, utils  # @IgnorePep8


log = logger.getLogger(config['NAME'], config['LOGLEVEL'])
fmt = utils.fmt


def application(env, start_response):
    from hello import Hello
    from script import Script
    from image import ImageStore
    from upload import Upload
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
