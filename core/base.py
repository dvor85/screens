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
    TABLE_COMPTITLE = 'comptitle'

    def __init__(self):
        utils.makedirs(os.path.dirname(config['BASE_FILE']), mode=0775)

        self.conn = sqlite3.connect(config['BASE_FILE'])  # @UndefinedVariable
        self.conn.row_factory = sqlite3.Row  # @UndefinedVariable
        sql = []
        sql.append(
            fmt("create table if not exists {scheme} \
                    (viewer varchar(32) NOT NULL, comp varchar(32) NOT NULL, user varchar(32) NOT NULL)",
                scheme=Base.TABLE_SCHEME))
        sql.append(
            fmt("create table if not exists {base} (comp varchar(32) PRIMARY KEY, title varchar(32) NOT NULL)",
                base=Base.TABLE_COMPTITLE))
        with self.conn:
            for s in sql:
                self.conn.execute(s)

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
        sql = []
        sql.append(fmt('delete from {base} where viewer like "{viewer}%" and comp="{comp}"',
                       viewer=viewer, comp=comp, base=Base.TABLE_SCHEME))
        sql.append(fmt('delete from {base} where comp="{comp}"',
                       comp=comp, base=Base.TABLE_COMPTITLE))
        with self.conn:
            for s in sql:
                self.conn.execute(s)

    def del_user(self, viewer, comp, user):
        sql = fmt('delete from {scheme} where viewer like "{viewer}%" and comp like "{comp}%" and user="{user}"',
                  viewer=viewer, comp=comp, user=user, scheme=Base.TABLE_SCHEME)
        with self.conn:
            self.conn.execute(sql)

    def get_scheme(self, viewer):
        try:
            sql = fmt('select distinct {scheme}.comp, viewer, title, user from {scheme} left join {comptitle} \
                             on {scheme}.comp={comptitle}.comp where viewer like "{viewer}%"',
                      viewer=viewer, scheme=Base.TABLE_SCHEME, comptitle=Base.TABLE_COMPTITLE)
            with self.conn:
                return self.conn.execute(sql).fetchall()
        except Exception as e:
            log.error(e)
            return []

    def get_comp_titles(self, comp):
        try:
            sql = fmt('select comp, title from {base} where comp like "{comp}%"',
                      comp=comp, base=Base.TABLE_COMPTITLE)
            with self.conn:
                return [(utils.utf(r['comp']), utils.utf(r['title'])) for r in self.conn.execute(sql).fetchall()]
        except Exception as e:
            log.error(e)
            return []

    def get_allowed_comps(self, viewer):
        try:
            sql = fmt('select distinct {scheme}.comp, title from {scheme} left join {comptitle} \
                            on {scheme}.comp={comptitle}.comp where viewer="{viewer}"',
                      viewer=viewer, scheme=Base.TABLE_SCHEME, comptitle=Base.TABLE_COMPTITLE)
            with self.conn:
                return dict((utils.utf(r['comp']), utils.utf(r['title']) if r['title'] is not None else utils.utf(r['comp']))
                            for r in self.conn.execute(sql).fetchall())
        except Exception as e:
            log.error(e)
            return {}

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
            cur = self.conn.execute(sql)
            return cur.rowcount

    def set_comp_title(self, comp, title):
        sql = []
        sql.append(fmt('update {base} set title="{title}" where comp="{comp}"',
                       comp=comp, title=title, base=Base.TABLE_COMPTITLE))
        sql.append(fmt('insert into {base} values ("{comp}", "{title}")',
                       comp=comp, title=title, base=Base.TABLE_COMPTITLE))
        with self.conn:
            cur = self.conn.execute(sql[0])
            if cur.rowcount == 0:
                cur = self.conn.execute(sql[1])
            return cur.rowcount

    def rename_user(self, comp, olduser, newuser):
        sql = fmt('update {scheme} set user="{new}" where user="{old}" and comp like "{comp}%"',
                  new=newuser, old=olduser, comp=comp, scheme=Base.TABLE_SCHEME)
        with self.conn:
            cur = self.conn.execute(sql)
            return cur.rowcount


if __name__ == "__main__":
    db = Base()
    print db.get_comp_titles('')
