# -*- coding: utf-8 -*-
import os, sys
from string import Template

from core import logger, defines
from core.config import config

selfdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
log = logger.getLogger(__name__, config['LOGLEVEL'])


class Initialization():
    
    def __init__(self):
        self.apache_template = os.path.join(selfdir, 'template/apache_vhost.conf')
        self.apache_vhost = os.path.join(selfdir, 'apache/spagent.conf')
        
        
    def generate_apache_vhost(self):
        log.debug('Generate apache virtual host')        
        defines.makedirs(os.path.dirname(self.apache_vhost))
        try:
            with open(self.apache_vhost, 'w') as fp:
                fp.write(Template(open(self.apache_template, 'r').read()).safe_substitute(config))
        except Exception as e:
            log.error(e)
            
            
    def main(self):
        self.generate_apache_vhost()
            
            
if __name__ == '__main__':
    Initialization().main()
            
            

    
        