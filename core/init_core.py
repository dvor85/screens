# -*- coding: utf-8 -*-
import os, sys
from string import Template

from core import logger, defines
from core.config import config

selfdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
log = logger.getLogger(__name__, config['LOGLEVEL'])


class Generator():
    
    def __init__(self):
        self.templates_dir = os.path.join(selfdir, 'templates')
        self.generated_dir = os.path.join(selfdir, 'generated')
        defines.makedirs(self.generated_dir)
        
        
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
            
            

    
        