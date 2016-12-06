# -*- coding: utf-8 -*-
# from __future__ import unicode_literals


import sqlite3
import os
from config import config
from core import logger, utils


log = logger.getLogger(config['NAME'], config['LOGLEVEL'])
fmt = utils.fmt


class Base:

    TABLE_SCHEME = 'scheme'

    def __init__(self):
        utils.makedirs(os.path.dirname(config['BASE_FILE']), mode=0775)

        self.conn = sqlite3.connect(config['BASE_FILE'])  # @UndefinedVariable
        self.conn.row_factory = sqlite3.Row  # @UndefinedVariable
        sql = fmt("create table if not exists {scheme} (viewer varchar(32), comp varchar(32), user varchar(32))",
                  scheme=Base.TABLE_SCHEME)
        with self.conn:
            self.conn.execute(sql)

    def add_scheme(self, viewer, comp, user):
        if user not in self.get_allowed_users(viewer, comp):
            sql = fmt('insert into {scheme} values("{viewer}", "{comp}", "{user}")',
                      viewer=viewer, comp=comp, user=user, scheme=Base.TABLE_SCHEME)
            with self.conn:
                self.conn.execute(sql)

    def del_viewer(self, viewer):
        sql = fmt('delete from {scheme} where viewer="{viewer}"',
                  viewer=viewer, scheme=Base.TABLE_SCHEME)
        with self.conn:
            self.conn.execute(sql)

    def del_comp(self, viewer, comp):
        sql = fmt('delete from {scheme} where viewer like "{viewer}%" and comp="{comp}"',
                  viewer=viewer, comp=comp, scheme=Base.TABLE_SCHEME)
        with self.conn:
            self.conn.execute(sql)

    def del_user(self, viewer, comp, user):
        sql = fmt('delete from {scheme} where viewer like "{viewer}%" and comp like "{comp}%" and user="{user}"',
                  viewer=viewer, comp=comp, user=user, scheme=Base.TABLE_SCHEME)
        with self.conn:
            self.conn.execute(sql)

    def get_scheme(self, viewer):
        try:
            sql = fmt('select viewer, comp, user from {scheme} where viewer like "{viewer}%"',
                      viewer=viewer, scheme=Base.TABLE_SCHEME)
            with self.conn:
                return self.conn.execute(sql).fetchall()
        except Exception as e:
            log.error(e)
            return []

    def get_allowed_comps(self, viewer):
        try:
            sql = fmt('select distinct comp from {scheme} where viewer="{viewer}"',
                      viewer=viewer, scheme=Base.TABLE_SCHEME)
            with self.conn:
                return [utils.utf(r['comp']) for r in self.conn.execute(sql).fetchall()]
        except Exception as e:
            log.error(e)
            return []

    def get_allowed_users(self, viewer, comp):
        try:
            sql = fmt('select distinct user from {scheme} where viewer="{viewer}" and comp="{comp}"',
                      viewer=viewer, comp=comp, scheme=Base.TABLE_SCHEME)
            with self.conn:
                return [utils.utf(r['user']) for r in self.conn.execute(sql).fetchall()]
        except Exception as e:
            log.error(e)
            return []

    def rename_viewer(self, oldviewer, newviewer):
        sql = fmt('update {scheme} set viewer="{new}" where viewer="{old}"',
                  new=newviewer, old=oldviewer, scheme=Base.TABLE_SCHEME)
        with self.conn:
            self.conn.execute(sql)

    def rename_comp(self, oldcomp, newcomp):
        sql = fmt('update {scheme} set comp="{new}" where comp="{old}"',
                  new=newcomp, old=oldcomp, scheme=Base.TABLE_SCHEME)
        with self.conn:
            self.conn.execute(sql)

    def rename_user(self, comp, olduser, newuser):
        sql = fmt('update {scheme} set user="{new}" where user="{old}" and comp like "{comp}%"',
                  new=newuser, old=olduser, comp=comp, scheme=Base.TABLE_SCHEME)
        with self.conn:
            self.conn.execute(sql)


if __name__ == "__main__":
    pass
