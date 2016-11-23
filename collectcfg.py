# encoding: utf8

import os
from config import config
import utils
import base64
import logger

log = logger.getLogger(config['NAME'], config['LOGLEVEL'])
fmt = utils.fmt


class Collector():

    def __init__(self):
        self.datadir = os.path.join(utils.getDataDIR(), '.{NAME}'.format(**config))
        self.info_file = os.path.join(self.datadir, 'ofni.bin')
        utils.makedirs(self.datadir)

    def collect(self):
        info = {}
        info.update(config)
        del info['AUTH']
        info['DATA_DIR'] = self.datadir
        return "\n".join(fmt('{k} = {v}', k=k, v=v) for k, v in info.iteritems())

    def save(self):
        try:
            with open(self.info_file, 'wb') as fd:
                fd.write(base64.urlsafe_b64encode(self.collect()))
        except Exception as e:
            log.error(e)

if __name__ == '__main__':
    Collector().save()
