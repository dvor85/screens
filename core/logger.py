# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import sys
import logging
from logging.handlers import SysLogHandler


class Logger(logging.Logger):

    def __init__(self, name, level=logging.NOTSET):
        logging.Logger.__init__(self, name, level=level)

        stream_format = logging.Formatter(fmt="%(asctime)-19s: %(name)s[%(module)s]: %(levelname)s: %(message)s")
        stream_handler = logging.StreamHandler(stream=sys.stdout)
        stream_handler.setFormatter(stream_format)
        self.addHandler(stream_handler)

        syslog_format = logging.Formatter(fmt="%(name)s: %(levelname)s: [%(module)s]: %(message)s")
        syslog_handler = SysLogHandler(address='/dev/log')
        syslog_handler.setFormatter(syslog_format)
        self.addHandler(syslog_handler)


def getLogger(name, level=logging.NOTSET):
    """
    Returns the logger with the specified name.
    name       - The name of the logger to retrieve
    """
    logging.setLoggerClass(Logger)

    log = logging.getLogger(name)
    log.setLevel(level)

    return log
