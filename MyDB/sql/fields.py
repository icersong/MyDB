# -*- coding:utf8 -*-

import re

from types import StringTypes

from abstract import ErrorSql, UNICODE


class ErrorSqlField(ErrorSql): pass


class Field():

    __keys = ['null']

    def __init__(self, expression, *args):
        """
        expression
        expression, aliasname
        tablename, fieldname, aliasname
        """
        if isinstance(expression, self.__class__):
            """ 拷贝构造 """
            self._expression = expression._expression
            self._aliasname = expression._aliasname
        else:
            if len(args) == 0:
                ptable = '`?(?P<table>[a-z_][\w:]*)`?'
                pfield = '`?(?P<field>[a-z_][\w:]*)`?'
                palias = '`?(?P<alias>[a-z_][\w:]*)`?'
                p = re.compile(u'^\s*({0}\\.)?{1}(\s+as\s+{2})?\s*$'.format(ptable, pfield, palias), re.IGNORECASE)
                m = p.match(expression)
                if m:   # [table.]field as alias
                    d = m.groupdict()
                    if d['table']:
                        self._expression = u'`{table}`.`{field}`'.format(**d)
                    elif d['alias'] and expression[0] != '`' and d['field'] in self.__keys:
                        self._expression = u'{field}'.format(**d)
                    elif d['alias'] and expression[0] != '`' and re.match('\d+', d['field']):
                        self._expression = u'{field}'.format(**d)
                    else:
                        self._expression = u'`{field}`'.format(**d)
                    self._aliasname = d['alias']
                else:
                    p = re.compile(u'^\s*(?P<expression>.+)\s+as\s+{0}\s*$'.format(palias), re.IGNORECASE)
                    m = p.match(expression)
                    if m:
                        d = m.groupdict()
                        self._expression = d['expression']
                        self._aliasname = d['alias']
                    else:
                        self._expression = expression
                        self._aliasname = None
            elif len(args) == 1:
                self._aliasname = args[0].strip().strip('`')
                ptable = '`?(?P<table>[a-z_][\w:]*)`?'
                pfield = '`?(?P<field>[a-z_][\w:]*)`?'
                p = re.compile(u'^\s*({0}\\.)?{1}\s*$'.format(ptable, pfield), re.IGNORECASE)
                m = p.match(expression)
                if m:
                    d = m.groupdict()
                    if d['table']:
                        self._expression = u'`{table}`.`{field}`'.format(**d)
                    elif self._aliasname and expression[0] != '`' and d['field'] in self.__keys:
                        self._expression = u'{field}'.format(**d)
                    elif self._aliasname and expression[0] != '`' and re.match('\d+', d['field']):
                        self._expression = u'{field}'.format(**d)
                    else:
                        self._expression = u'`{field}`'.format(**d)
                else:
                    self._expression = expression
            else:
                tablename = expression.strip().strip('`')
                fieldname = args[0].strip().strip('`')
                self._expression = '`' + tablename + '`.`' + fieldname + '`'
                self._aliasname = args[1].strip().strip('`')

        self._expression = UNICODE(self._expression)

    def aliasname(self, name=None):
        if name is not None:
            assert(isinstance(name, StringTypes) and name.strip() != '')
            self._aliasname = name.strip()
        return self._aliasname

    def currname(self):
        if self._aliasname:
            return self._aliasname
        return self._expression

    def tostring(self):
        expression = self._expression
        if self._aliasname:
            return expression + ' AS `' + self._aliasname + '`'
        return expression

    def __str__(self, coding=None):
        return self.tostring()


class FieldsMixIn():

    def field(self, *args):
        if not hasattr(self, '_fields'):
            self._fields = []

        self._fields.append(Field(*args))
        return self

    def fields(self, *args):
        """
        args:
          Field String, orignal sql fields string
          Field list or tuple, (expression, alias) | (table, field, alias)
          Field Object
        kvargs:
          {aliasname:field expression, ...}
        """
        if not hasattr(self, '_fields'):
            self._fields = []

        for field in args:
            if isinstance(field, StringTypes):
                self._fields.append(Field(field))
            elif isinstance(field, Field):
                self._fields.append(field)
            elif isinstance(field, tuple) or isinstance(field, list):
                self._fields.append(Field(*field))
            else:
                raise ErrorSqlField('Agument must be string or Field object. current type is"' + type(field) + '"', field)

        return self

    def get_fields(self):
        return self._fields

    def set_fields(self, *args):
        self._fields = []
        self.fields(*args)
        return self

    def _fields_string(self):
        assert(len(self._fields) > 0)
        return ', '.join([(isinstance(x, str) or isinstance(x, unicode)) and x or x.__str__('UTF8')
                          for x in self._fields])


class GroupMixIn():

    def group(self, *args):
        """
        [tablename, fieldname], ...
        "tablename.fieldname", ...
        """

        if not hasattr(self, '_group_fields'):
            self._group_fields = []

        self._group_fields.extend(args)

        return self

    def get_group(self):
        return getattr(self, '_group_fields', None)

    def _group_string(self):
        if not hasattr(self, '_group_fields'):
            return None

        ret = []

        for v in self._group_fields:
            if isinstance(v, list) or isinstance(v, tuple):
                assert(v)
                if len(v) == 1:
                    if v[0].find('.') == -1:
                        ret.append('`' + v[0] + '`')
                    else:
                        ret.append(v[0])
                else:
                    ret.append('`' + v[0] + '`.`' + v[1] + '`')
            else:
                for s in v.split(','):
                    aa = s.split('.')
                    if len(aa) > 1:
                        ret.append('`' + aa[0].strip().strip('`') + '`.`' + aa[1].strip().strip('`') + '`')
                    else:
                        ret.append('`' + aa[0].strip().strip('`') + '`')

        return ', '.join(ret)


class OrderMixIn():

    def order(self, *args):
        """
        arg: expression
             (expression)
             (expression, ASC|DESC)
             (table, field, ASC|DESC)
        args: [arg,...]
        """
        if not args:
            self._order_fields = []
        else:
            if not hasattr(self, '_order_fields'):
                self._order_fields = []

            self._order_fields.extend(args)

        return self

    def get_order(self):
        return getattr(self, '_order_fields', None)

    def set_order(self, *args):
        self._order_fields = []
        return self.order(*args)

    def _order_string(self):
        if not hasattr(self, '_order_fields'):
            return None

        ret = []

        ptable = '`?(?P<table>[a-z_][\w:]*)`?'
        pfield = '`?(?P<field>[a-z_][\w:]*)`?'
        porder = '(?P<order>asc|desc)'

        for v in self._order_fields:
            assert(len(v))
            if not (isinstance(v, (list, tuple))):
                assert(isinstance(v, StringTypes))
                v = (v,)

            if len(v) == 1:
                pattern = re.compile(u'^({0}\\.)?{1}(\s+{2})?$'.format(ptable, pfield, porder), re.IGNORECASE)
                m = pattern.match(v[0])
                if m:
                    x = m.groupdict()
                    order = x['order'] and x['order'].upper() or ''
                    if x['table']:
                        ret.append((u'`{0}`.`{1}` {2}'.format(x['table'], x['field'], order)).rstrip())
                    else:
                        ret.append((u'`{0}` {1}'.format(x['field'], order)).rstrip())
                else:
                    ret.append(v[0])
            elif len(v) == 2:
                order = v[1] and v[1].upper() or ''
                assert(order in ('ASC', 'DESC', ''))
                pattern = re.compile(u'^({0}\\.)?{1}$'.format(ptable, pfield), re.IGNORECASE)
                m = pattern.match(v[0])
                if m:
                    x = m.groupdict()
                    if x['table']:
                        ret.append((u'`{0}`.`{1}` {2}'.format(x['table'], x['field'], order)).rstrip())
                    else:
                        ret.append((u'`{0}` {1}'.format(x['field'], order)).rstrip())
                else:
                    ret.append(u'{0} {1}'.format(v[0], order).rstrip())

            else:
                pattern = re.compile('`?(?P<named>[a-z_][\w:]*)`?', re.IGNORECASE)
                assert(len(v) == 3)
                table = pattern.match(v[0]).groupdict()['name']
                assert(table)
                field = pattern.match(v[1]).groupdict()['name']
                assert(field)
                order = v[2].upper()
                assert(order in ('ASC', 'DESC', ''))

                ret.append((u'`{0}`.`{1}` {2}'.format(table, field, order)).rstrip())

        return ', '.join(ret)
