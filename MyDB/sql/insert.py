# -*- coding:utf8 -*-
import re
from abstract import Abstract, ErrorSql, tovalue, SqlBase
from fields import FieldsMixIn
from select import Select
from sets import SetsMixIn, UpdateMixIn


class Insert(Abstract, FieldsMixIn, SetsMixIn, UpdateMixIn):

    PRIORITY = ['PRIORITY_LOW', 'DELAYED', 'PRIORITY_HIGH']
    DEFAULT = SqlBase('DEFAULT')

    def priority(self, flag=None):
        self._priority = flag

    def ignore(self, flag=True):
        self._ignore = flag

    def values(self, *args):
        """ 参数说明：
        1、只有一个参数，并且为字符串，则表示原始一行或多行 sql 数据， 如："(1,2,3),(4,5,6),..."
        2、含有一个或过个数组，则认为args中每一个参数为一行数据，如：(1,2),"(3,4)",[5,6],...
        3、其它情况认为args为一行数据，如：'var1', 1, 'var2', ...
        4、如果value为自定义class并且包含tosql方法，则使用tosql获得字符串，并视为表达式字符串
        """
        if not args:
            return self

        if len(args) == 1 and isinstance(args[0], Select):
            self.select(args[0])
            return self

        if not hasattr(self, '_values'): self._values = []

        if len(args) == 1 and isinstance(args[0], basestring):
            # 只有一个参数并且为字符串，则认为是一行或多行标准字符串数据
            self._values.append(args[0])
        if [True for x in args if isinstance(x, (list, tuple))]:
            # 一个或者多个数据时，有至少一个为数组，则认为每个参数为一行数据
            self._values.extend(args)
        else:
            # 否则认为args为一行数据
            self._values.append(args)
        return self

    def value(self, *args):
        if args:
            if not hasattr(self, '_tmp_row'): self._tmp_row = []
            self._tmp_row.extend(args)
            return self
        if not getattr(self, '_tmp_row', None): return self
        self.values(self._tmp_row)
        self._tmp_row = []
        return self

    def value_end(self, *args):
        self.value(*args)
        if args:
            self.value()
        return self

    def get_values(self):
        return getattr(self, '_values', None)

    def _values_string(self):
        if not getattr(self, '_values', None): return None
        rr = []
        for values in self._values:
            if isinstance(values, Select):
                if len(self._values) > 1:
                    raise ErrorSql('Error, Too more Select and values. count({0})'.format(len(self._values)))
                rr.append(values.tostring())
                continue
            if isinstance(values, (tuple, list)):
                if not values: continue
                vv = [tovalue(v, self._auto_escape) for v in values]
                rr.append(u'({0})'.format(', '.join(vv)))
                continue
            if not isinstance(values, basestring):
                values = str(values)
            values = values.strip()
            if re.compile(u'^\\(?\s*select\s+', re.IGNORECASE).match(values):
                if len(self._values) > 1:
                    raise ErrorSql('Error, Too more select and values. count({0})'.format(len(self._values)))
                rr.append(values)
                continue
            if not (values[0] == '(' and values[-1] == ')'):
                values = u'({0})'.format(values)
            rr.append(values)
        return ', '.join(rr)

    def select(self, select):
        self._select = select
        return self

    def _tostring(self):
        rr = [u'INSERT']
        if getattr(self, '_priority', None) in self.__class__.PRIORITY:
            rr.append(self._priority)
        if getattr(self, '_ignore', False):
            rr.append('IGNORE')
        rr.append('INTO')
        rr.append(self._table_string())
        rr.append(u'(')
        rr.append(self._fields_string())
        rr.append(u')')

        values = self._values_string()
        if values:
            if re.compile(u'^\\(?\s*select\s+', re.IGNORECASE).match(values):
                if values[0] == '(':
                    rr.append(values)
                else:
                    rr.append('(')
                    rr.append(values)
                    rr.append(')')
            else:
                rr.append('VALUES')
                rr.append(values)

        elif self.get_sets():
            rr.append(self._sets_string())

        elif getattr(self, '_select', None):
            sel = self._select
            if not isinstance(sel, basestring): sel = sel.tostring()
            rr.append('(')
            rr.append(sel)
            rr.append(')')
        else:
            # raise ErrorSql('Error, No values for insert.')
            pass

        if self.get_update():
            rr.append('ON DUPLICATE KEY UPDATE')
            rr.append(self._update_string())

        return u' '.join([x for x in rr])
