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
    from archive import Archive
    from online import Online
    app = JsonRpcApplication(rpcs=dict(archive=Archive(env),
                                       online=Online(env)))
    return app(env, start_response)


if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8080, application)
    log.debug("Serving on port 8080...")
    httpd.serve_forever()
