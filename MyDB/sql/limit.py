#!/usr/bin python
# -*- coding: UTF8 -*-
# Copyright (C) 2011 Python Software Foundation
# Author: icewater.song
# Contact: icersong@gmail.com

""" UTF8文件编码  """

__version__ = '1.0.0'

from abstract import ErrorSql


class LimitMixIn:
    def limit(self, *args):
        if not args:
            self._limit = None
            return self

        if len(args) == 1:
            args = [0, args[0]]

        # args[0]: offset; args[1]: row count
        rowcount = args[1] or 0
        if not isinstance(rowcount, (int, long)):
            rowcount = int(rowcount, 10)
        if rowcount > 0:
            offset = args[0] or 0
            if not isinstance(offset, (int, long)):
                offset = int(offset, 10)
            if offset > 0:
                self._limit = [offset, rowcount]
            else:
                self._limit = [0, rowcount]
        else:
            self._limit = None
        return self

    def _limit_string(self):
        if hasattr(self, '_limit') and self._limit:
            limit = self._limit
            if limit[0]:
                return u'{0}, {1}'.format(*limit)
            else:
                return u'{0}'.format(limit[1])
        return ''


class PageMixIn:
    def page(self, page, rspp):
        """
        page: page number, start from 0, max is total page count - 1
        rspp: rows per page
        """
        if not rspp:
            return self

        if not isinstance(rspp, (int, long)):
            try:
                rspp = int(rspp, 10)
            except:
                raise ErrorSql(u"Error! rspp not valid number. {0}".format(rspp))
        if rspp == 0:
            return self

        if rspp < 0:
            raise ErrorSql(u"Error! rspp must great then 0. {0}".format(rspp))

        if not page:
            page = 0
        elif not isinstance(page, (int, long)):
            try:
                page = int(page, 10)
            except:
                raise ErrorSql(u"Error! page not valid number. {0}".format(page))

        if page < 0:
            return self

        return self.limit(page * rspp, rspp)
