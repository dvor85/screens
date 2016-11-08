# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import os, sys
from string import Template
from config import config
from core import logger, utils


log = logger.getLogger(config['NAME'], config['LOGLEVEL'])


class Generator():
    
    def __init__(self):
        self.templates_dir = os.path.join(config['SELF_DIR'], 'templates')
        self.generated_dir = os.path.join(config['SELF_DIR'], 'generated')
        utils.makedirs(self.generated_dir)
        
        
    def generate_file(self, filename, extra=None):
        generated_file = os.path.join(self.generated_dir, filename) 
        log.info('Generate file: {}'.format(generated_file))    
        try:
            with open(generated_file, 'w') as fp:
                tmpl = Template(open(os.path.join(self.templates_dir, filename), 'r').read())
                if extra is None: 
                    fp.write(tmpl.safe_substitute(config))
                else:                    
                    fp.write(tmpl.safe_substitute(config, **extra))
                    
        except Exception as e:
            log.error(e)
            
            
    def main(self):
        for filename in os.listdir(self.templates_dir):
            self.generate_file(filename)
            
            
if __name__ == '__main__':
    Generator().main()
            
            

    
        