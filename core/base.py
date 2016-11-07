# -*- coding: utf-8 -*-
# from __future__ import unicode_literals


import sqlite3
import os, sys

from config import config
from core import logger, utils


log = logger.getLogger(__name__, config['LOGLEVEL'])


class Base:
    def __init__(self, root_path): 
        log.info('Init Base') 
        utils.makedirs(os.path.dirname(config['BASE_FILE']), mode=0775)     
        
        self.conn = sqlite3.connect(config['BASE_FILE'])
        self.conn.row_factory = sqlite3.Row
        with self.conn:
#             self.conn.execute("create table if not exists comps (comp varchar(16), title varchar(32))")
#             self.conn.execute("create table if not exists users (id integer primary key autoincrement, comp varchar(16), name varchar(32))")
#             self.conn.execute("create table if not exists viewers (id integer primary key autoincrement, name varchar(32))")
            self.conn.execute("create table if not exists scheme (viewer varchar(32), comp varchar(32), user varchar(32))")
            
    def test_add(self):
        with self.conn:
            self.conn.execute('insert into comps values("10.0.0.193", "demon")')
            self.conn.execute('insert into users values(null, "10.0.0.193", "Dmitriy")')
            
            last_user = self.conn.execute('select max(id) as id from users').fetchone()['id']
            self.conn.execute('insert into viewers values(null, "viewer 1")')
            last_viwer = self.conn.execute('select max(id) as id from viewers').fetchone()['id']
            self.conn.execute('insert into scheme values({0}, {1})'.format(last_viwer, last_user))
            
    def add_comp(self, comp, title):
        with self.conn:
            self.conn.execute('insert into comps values("{0}", "{1}")'.format(comp, title))
            
    def add_scheme(self, viewer, comp, user):
        with self.conn:
            self.conn.execute('insert into scheme values("{0}", "{1}", "{2}")'.format(viewer, comp, user))
            
    
    def get_allowed_comps(self, viewer):
        try:
            with self.conn:
                return [r['comp'] for r in self.conn.execute('select distinct comp from scheme where viewer="{0}"'.format(viewer)).fetchall()]
        except Exception as e:
            log.error(e)
            return []   
        
    def get_allowed_users(self, viewer, comp):
        try:
            with self.conn:
                return [r['user'] for r in self.conn.execute('select distinct user from scheme where viewer="{0}" and comp="{1}"'.format(viewer, comp)).fetchall()]
        except Exception as e:
            log.error(e)
            return []             
    
            
    def get_comps(self, viewer):
        try:
            with self.conn:
                return self.conn.execute("select * from comps inner join ( users inner join scheme on users.id=scheme.user_id ) on comps.comp=users.comp  where viewer_id={0}".format(viewer)).fetchall()
        except Exception as e:
            log.error(e)
            return []
        
    def test(self):
#         self.add_comp('10.0.0.193', 'test 1')
#         self.add_comp('10.0.0.19', 'test 2')
#         self.add_comp('10.0.0.12', 'test 3')
        self.add_scheme('viewer 1', 'VDV-PC', 'user')
        self.add_scheme('viewer 1', 'VDV-PC', 'admin')
        self.add_scheme('viewer 1', 'COMP2', 'user')
        self.add_scheme('viewer 2', 'COMP1', 'user')
        self.add_scheme('viewer 2', 'VDV-PC', 'user')
        self.add_scheme('admin', 'COMP2', 'user')
        self.add_scheme('admin', 'COMP1', 'user')
        self.add_scheme('admin', 'VDV-PC', 'user')
        self.add_scheme('admin', 'VDV-PC', 'Dmitriy')

    
if __name__ == "__main__":
    db = Base('')
#     db.test()    
    print db.get_allowed_comps('viewer 1')
    print db.get_allowed_users('viewer 1', 'VDV-PC')
#     [sys.stdout.write(r+" ") for r in db.get_allowed_comp('viewer 1')]
    
        
#     res = db.get_allowed_comp('viewer 1')
#     for r in res:
#         print r
#     print [r['comp'] for r in res]
#     print res[0]['comp']
    

