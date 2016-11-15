# -*- coding: utf-8 -*-
# from __future__ import unicode_literals


import sqlite3
import os
from config import config
from core import logger, utils


log = logger.getLogger(config['NAME'], config['LOGLEVEL'])
fmt = utils.fmt


class Base:

    def __init__(self):
        utils.makedirs(os.path.dirname(config['BASE_FILE']), mode=0775)

        self.conn = sqlite3.connect(config['BASE_FILE'])
        self.conn.row_factory = sqlite3.Row
        with self.conn:
            self.conn.execute("create table if not exists scheme (viewer varchar(32), comp varchar(32), user varchar(32))")

    def add_scheme(self, viewer, comp, user):
        with self.conn:
            self.conn.execute(fmt('insert into scheme values("{0}", "{1}", "{2}")', viewer, comp, user))

    def del_viewer(self, viewer):
        with self.conn:
            self.conn.execute(fmt('delete from scheme where viewer="{0}"', viewer))

    def del_comp(self, viewer, comp):
        with self.conn:
            self.conn.execute(fmt('delete from scheme where viewer="{0}" and comp="{1}"', viewer, comp))

    def del_user(self, viewer, comp, user):
        with self.conn:
            self.conn.execute(fmt('delete from scheme where viewer="{0}" and comp="{1}" and user="{2}"', viewer, comp, user))

    def get_scheme(self, viewer):
        try:
            with self.conn:
                return self.conn.execute(fmt('select viewer, comp, user from scheme where viewer like "{0}%"', viewer)).fetchall()
        except Exception as e:
            log.error(e)
            return []

    def get_allowed_comps(self, viewer):
        try:
            with self.conn:
                return [utils.utf(r['comp']) for r in self.conn.execute(fmt('select distinct comp from scheme where viewer="{0}"', viewer)).fetchall()]
        except Exception as e:
            log.error(e)
            return []

    def get_allowed_users(self, viewer, comp):
        try:
            with self.conn:
                return [utils.utf(r['user']) for r in self.conn.execute(fmt('select distinct user from scheme where viewer="{0}" and comp="{1}"', viewer, comp)).fetchall()]
        except Exception as e:
            log.error(e)
            return []

if __name__ == "__main__":
    pass
