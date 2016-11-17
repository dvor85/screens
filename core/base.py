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
        sql = "create table if not exists scheme (viewer varchar(32), comp varchar(32), user varchar(32))"
        with self.conn:
            self.conn.execute(sql)

    def add_scheme(self, viewer, comp, user):
        sql = fmt('insert into scheme values("{0}", "{1}", "{2}")', viewer, comp, user)
        with self.conn:
            self.conn.execute(sql)

    def del_viewer(self, viewer):
        sql = fmt('delete from scheme where viewer="{0}"', viewer)
        with self.conn:
            self.conn.execute(sql)

    def del_comp(self, viewer, comp):
        sql = fmt('delete from scheme where viewer="{0}" and comp="{1}"', viewer, comp)
        with self.conn:
            self.conn.execute(sql)

    def del_user(self, viewer, comp, user):
        sql = fmt('delete from scheme where viewer="{0}" and comp="{1}" and user="{2}"', viewer, comp, user)
        with self.conn:
            self.conn.execute(sql)

    def get_scheme(self, viewer):
        try:
            sql = fmt('select viewer, comp, user from scheme where viewer like "{0}%"', viewer)
            with self.conn:
                return self.conn.execute(sql).fetchall()
        except Exception as e:
            log.error(e)
            return []

    def get_allowed_comps(self, viewer):
        try:
            sql = fmt('select distinct comp from scheme where viewer="{0}"', viewer)
            with self.conn:
                return [utils.utf(r['comp']) for r in self.conn.execute(sql).fetchall()]
        except Exception as e:
            log.error(e)
            return []

    def get_allowed_users(self, viewer, comp):
        try:
            sql = fmt('select distinct user from scheme where viewer="{0}" and comp="{1}"', viewer, comp)
            with self.conn:
                return [utils.utf(r['user']) for r in self.conn.execute(sql).fetchall()]
        except Exception as e:
            log.error(e)
            return []

    def rename_viewer(self, oldviewer, newviewer):
        sql = fmt('update scheme set viewer={0} where viewer={1}', newviewer, oldviewer)
        with self.conn:
            self.conn.execute(sql)

    def rename_comp(self, oldcomp, newcomp):
        sql = fmt('update scheme set comp={0} where comp={1}', newcomp, oldcomp)
        with self.conn:
            self.conn.execute(sql)

    def rename_user(self, olduser, newuser):
        sql = fmt('update scheme set user={0} where user={1}', newuser, olduser)
        with self.conn:
            self.conn.execute(sql)


if __name__ == "__main__":
    pass
