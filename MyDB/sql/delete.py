#-*- coding:utf8 -*-

from abstract import Abstract
from conditions import WhereMixIn


class Delete(Abstract, WhereMixIn):
    def _tostring(self):
        rr = ['DELETE FROM']
        rr.append(self._table_string())
        where = self._where_string()
        if where:
            rr.append('WHERE')
            rr.append(where)

        return u' '.join(rr)
