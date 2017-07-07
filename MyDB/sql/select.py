#-*- coding:utf8 -*-
#-*- 中文 -*-

from abstract import Abstract
from conditions import WhereMixIn, HavingMixIn
from fields import FieldsMixIn, GroupMixIn, OrderMixIn
from joins import JoinMixIn
from limit import LimitMixIn, PageMixIn


class Select(Abstract, FieldsMixIn, JoinMixIn, WhereMixIn, HavingMixIn, GroupMixIn, OrderMixIn, LimitMixIn, PageMixIn):

    def distinct(self):
        self._distinct = True
        return self

    def into(self, tablename):
        self._into_tablename = tablename
        return self

    def _tostring(self):
        rr = []
        rr.append('SELECT')
        if getattr(self, '_distinct', None):
            rr.append('DISTINCT')
        rr.append(self._fields_string())
        if getattr(self, '_into_tablename', None):
            rr.append('INTO')
            rr.append('`' + self._into_tablename + '`')
        rr.append('FROM')
        rr.append(self._table_string())
        _joins = self._join_string()
        if _joins:
            rr.append(_joins)
        _where = self._where_string()
        if _where:
            rr.append('WHERE')
            rr.append(_where)
        _group = self._group_string()
        if _group:
            rr.append('GROUP BY')
            rr.append(_group)
        _having = self._having_string()
        if _having:
            rr.append('HAVING')
            rr.append(_having)
        _order = self._order_string()
        if _order:
            rr.append('ORDER BY')
            rr.append(_order)
        _limit = self._limit_string()
        if _limit:
            rr.append('LIMIT')
            rr.append(_limit)

        return u' '.join(rr)
