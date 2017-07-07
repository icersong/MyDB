#-*- coding:UTF8 -*-
from abstract import Abstract
from conditions import WhereMixIn
from sets import SetsMixIn
from fields import OrderMixIn
from limit import LimitMixIn


class Update(Abstract, WhereMixIn, SetsMixIn, OrderMixIn, LimitMixIn):

    def set_low_priority(self):
        self._priority = 'LOW_PRIORITY'

    def ignore(self):
        self._ignore = 'IGNORE'

    def _tostring(self):
        rr = ['UPDATE']

        if getattr(self, '_priority', None):
            rr.append(self._priority)

        if getattr(self, '_ignore', None):
            rr.append(self._ignore)

        rr.append(self._table_string())

        rr.append('SET')
        rr.append(self._sets_string())

        where = self._where_string()
        if where:
            rr.append('WHERE')
            rr.append(where)

        order = self._order_string()
        if order:
            rr.append('ORDER BY')
            rr.append(order)

        limit = self._limit_string()
        if limit:
            rr.append('LIMIT')
            rr.append(limit)

        return u' '.join(rr)
