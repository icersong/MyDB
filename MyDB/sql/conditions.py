#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- 中文 -*-

from abstract import ErrorSql, UNICODE


class ErrorSQLCondition(ErrorSql): pass


class Condition():

    """
    条件生成器
    """

    # _conditions = []

    def __init__(self, condition=None, *args, **kwargs):
        self._conditions = []
        if condition:
            self.push(condition, *args, **kwargs)

    def push(self, condition, *args, **kwargs):

        self._conditions.append((
            self._conditions and 'AND' or '',
            UNICODE(condition).format(*args, **kwargs) if args or kwargs else condition))

        return self

    def pushOr(self, condition, *args, **kwargs):

        self._conditions.append((
            self._conditions and 'OR' or '',
            UNICODE(condition).format(*args, **kwargs) if args or kwargs else condition))

        return self

    def _to_array(self):

        ret = []

        for logic, condition in self._conditions:
            if isinstance(condition, self.__class__):
                aa = condition._to_array()
                if aa:
                    if logic:
                        ret.append(logic)
                    ret.append('(')
                    ret.extend(aa)
                    ret.append(')')
            else:
                condition = UNICODE(condition)
                if condition and logic:
                    ret.append(logic)
                ret.append(condition)

        return ret

    def _tostring(self):
        return u' '.join(self._to_array())

    def toString(self):
        return self._tostring()

    def tostring(self):
        return self._tostring()

    def __str__(self):
        return self._tostring()


def and_(*args):
    return reduce(lambda a, b: a.push(b), args, Condition())


def or_(*args):
    return reduce(lambda a, b: a.pushOr(b), args, Condition())


class WhereMixIn():

    def where(self, *args, **kvargs):
        if not hasattr(self, '_where'): self._where = Condition()
        self._where.push(*args, **kvargs)
        return self

    def whereOr(self, *args, **kvargs):
        if not hasattr(self, '_where'): self._where = Condition()
        self._where.pushOr(*args, **kvargs)
        return self

    def _where_string(self):
        if not hasattr(self, '_where'):
            return None
        return self._where.toString()

    def get_where(self):
        return getattr(self, '_where', None)


class HavingMixIn():

    def having(self, *args, **kvargs):
        if not hasattr(self, '_having'): self._having = Condition()
        self._having.push(*args, **kvargs)
        return self

    def havingOr(self, *args, **kvargs):
        if not hasattr(self, '_having'): self._having = Condition()
        self._having.pushOr(*args, **kvargs)
        return self

    def _having_string(self):
        if not hasattr(self, '_having'):
            return None
        return self._having.toString()

    def get_having(self):
        return getattr(self, '_having', None)
