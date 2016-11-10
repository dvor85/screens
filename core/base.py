# -*- coding: utf-8 -*-
# from __future__ import unicode_literals


import sqlite3
import os, sys
from config import config
from core import logger, utils


log = logger.getLogger(config['NAME'], config['LOGLEVEL'])


class Base:
    def __init__(self): 
        utils.makedirs(os.path.dirname(config['BASE_FILE']), mode=0775)     
        
        self.conn = sqlite3.connect(config['BASE_FILE'])
        self.conn.row_factory = sqlite3.Row
        with self.conn:
            self.conn.execute("create table if not exists scheme (viewer varchar(32), comp varchar(32), user varchar(32))")
            
            
    def add_scheme(self, viewer, comp, user):
        with self.conn:
            self.conn.execute('insert into scheme values("{0}", "{1}", "{2}")'.format(viewer, comp, user))
            
            
    def get_scheme(self, viewer):
        try:
            with self.conn:
                return self.conn.execute('select viewer, comp, user from scheme where viewer like "{0}%"'.format(viewer)).fetchall()
        except Exception as e:
            log.error(e)
            return []
            
    
    def get_allowed_comps(self, viewer):
        try:
            with self.conn:
                return [r['comp'].encode('utf8') for r in self.conn.execute('select distinct comp from scheme where viewer="{0}"'.format(viewer)).fetchall()]
        except Exception as e:
            log.error(e)
            return []   
        
    def get_allowed_users(self, viewer, comp):
        try:
            with self.conn:
                return [r['user'].encode('utf8') for r in self.conn.execute('select distinct user from scheme where viewer="{0}" and comp="{1}"'.format(viewer, comp)).fetchall()]
        except Exception as e:
            log.error(e)
            return []             
    
if __name__ == "__main__":
    pass

