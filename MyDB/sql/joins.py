# -*- coding:utf8 -*-
import re
from abstract import ErrorSql, _parse_table_name, Abstract
from conditions import Condition


class ErrorSqlJoin(ErrorSql):
    pass


class Join():
    """
        jointable: "tablename [AS tablealias]" | [table, alias]

        Full Join String
        Empty, Full Join String
        Join Type, Join String not with join type
        Join Type, jointable, joinfeild | condition
        Join Type, jointable, joinfeild, ontable
        Join Type, jointable, joinfeild, ontable, onfield
   """
    JOIN_TYPES = ('', 'LEFT', 'RIGHT', 'INNER', 'OUTER', 'FULL')

    def __init__(self, *args, **kvargs):
        self._type = None
        self._table = None
        self._alias = None
        self._field = None
        self._ontable = None
        self._onfield = None
        self._condition = None
        self._joinstring = None

        argn = len(args)

        if len(kvargs) == 0:
            assert(argn)
            if argn == 1:
                fulljoinstring = args[1]
                p = re.compile('^\s*([a-zA-Z_][\w:]*)\s+')
                m = p.search(fulljoinstring)
                assert(m)
                s = m.groups()[0].upper()
                assert(s in self.JOIN_TYPES or s == 'JOIN')
                self._joinstring = fulljoinstring
            if argn == 2 and not args[0]:
                fulljoinstring = args[1]
                p = re.compile('^\s*([a-zA-Z_][\w:]*)\s+')
                m = p.search(fulljoinstring)
                s = m and m.groups()[0].upper()
                if s and (s in self.JOIN_TYPES or s == 'JOIN'):
                    self._joinstring = fulljoinstring

        assert(argn + len(kvargs) > 1)

        if argn > 0:
            assert(args[0].strip().upper() in self.JOIN_TYPES)
            self._type = args[0].strip().upper()

        if argn > 1:
            # args[1]: string or list
            # [table, alias] | join string
            table, alias = _parse_table_name(args[1])
            if table:
                self._table = table
                self._alias = alias
            else:
                self._joinstring = args[1]
                return self

#            if isinstance(args[1], list) or isinstance(args[1], tuple):
#                table, alias = _parse_table_name(args[1])
#                self._table = args[1][0].strip().strip('`')
#                self._alias = args[1][1] and args[1][1].strip().strip('`')
#            else:
#                table, alias = _parse_table_name(args[1])
#                if table:
#                    self._table = table
#                    self._alias = alias
#                else:
#                    self._joinstring = args[1]
#                    return self

        if argn > 2:
            # field|condition
            if isinstance(args[2], Condition):
                self._condition = args[2]
            elif re.compile('^`?[\w:]+`?$').match(args[2]):
                self._field = args[2]
            else:
                self._condition = args[2]

        if argn > 3:
            self._ontable = args[3]

        if argn > 4:
            self._onfield = args[4]

        if 'type' in kvargs:
            assert(isinstance(kvargs['type'], basestring))
            self._type = kvargs['type'].strip()
        if 'table' in kvargs and kvargs['table']:
            table, alias = _parse_table_name(kvargs['table'])
            self._table = table
            self._alias = alias
        if 'field' in kvargs and kvargs['joinfeild']:
            self._field = kvargs['joinfeild'].strip().strip('`')
        if 'ontable' in kvargs and kvargs['ontable']:
            self._ontable = kvargs['ontable'].strip().strip('`')
        if 'onfield' in kvargs and kvargs['onfield']:
            self._onfield = kvargs['onfield'].strip().strip('`')
        if 'condition' in kvargs and 'condition' in kvargs:
            self._condition = kvargs['condition'].strip()
        if 'maintable' in kvargs:
            self._maintable = kvargs['maintable']

    def table(self, name=None):
        if name:
            if isinstance(name, list) or isinstance(name, tuple):
                assert(len(name) == 2)
                self._table = name[0].strip().strip('`')
                if name[1]:
                    self._alias = name[1].strip().strip('`')
            else:
                tname, alias = _parse_table_name(name)
                self._table = tname
                if alias:
                    self._alias = alias
        return self._table

    def field(self, name=None):
        if name:
            self._field = name.strip().strip('`')
        return self._field

    def ontable(self, name=None):
        if name:
            self._ontable = name.strip().strip('`')
        return self._ontable

    def onfield(self, name=None):
        if name:
            self._onfield = name.strip().strip('`')
        return self._onfield

    def alias(self, name=None):
        if name:
            self._alias = name.strip().strip('`')
        return self._alias

    def jointype(self, name=None):
        if name:
            self._type = name
        return self._type

    @property
    def condition(self):
        if not self._condition: self._condition = Condition()
        return self._condition

    def toString(self):
        assert(self._table)

        ss = []
        if self._type is not None:
            ss.append(self._type)
            ss.append('JOIN')

        if self._joinstring:
            ss.append(self._joinstring)
            return ' '.join(ss)

        if isinstance(self._table, str) or isinstance(self._table, unicode):
            if self._table[0] == '(' and self._table[-1] == ')':
                ss.append(self._table)
            else:
                ss.append('`' + self._table + '`')
        else:
            assert(isinstance(self._table, Abstract))
            assert(self._alias)
            ss.append('(')
            ss.append(self._table.tostring())
            ss.append(')')

        if self._alias:
            ss.append('AS')
            ss.append('`' + self._alias + '`')
        ss.append('ON')

        if self._condition:
            # 替换 $0 -> 主表
            s = str(self._condition)
            if self._ontable:
                p = re.compile('(.*)\\$0\\.`?([\w:]+)`?')
                s = p.sub('\\1`' + self._ontable + '`.`\\2`', s)

            # 替换 $1 -> 连接表
            tname = self._alias or self._table
            p = re.compile('(.*)\\$\\.`?([\w:]+)`?')
            s = p.sub('\\1`' + tname + '`.`\\2`', s)

            ss.append(s)
        else:
            assert(self._field)
            tname = self._alias and self._alias or self._table
            ss.append('`' + tname + '`.`' + self._field + '`')
            ss.append('=')
            ontable = self._ontable
            onfield = self._onfield and self._onfield or self._field
            ss.append('`' + ontable + '`.`' + onfield + '`')

        return ' '.join(ss)

    def __str__(self):
        return self.toString()


class JoinMixIn():

    def _join(self, *args, **kvargs):
        if not hasattr(self, '_join_list'):
            self._join_list = []

        assert(len(args))

        joins = [x for x in args if isinstance(x, Join)]
        if joins:
            self._join_list.extend(joins)
            return joins[0] if len(joins) else joins
        join = Join(*args, **kvargs)
        self._join_list.append(join)
        return join

    def join(self, *args, **kvargs):
        return self._join('', *args, **kvargs)

    def leftJoin(self, *args, **kvargs):
        return self._join('LEFT', *args, **kvargs)

    def leftjoin(self, *args, **kvargs):
        return self._join('LEFT', *args, **kvargs)

    def rightJoin(self, *args, **kvargs):
        return self._join('RIGHT', *args, **kvargs)

    def rightjoin(self, *args, **kvargs):
        return self._join('RIGHT', *args, **kvargs)

    def innerJoin(self, *args, **kvargs):
        return self._join('INNER', *args, **kvargs)

    def innerjoin(self, *args, **kvargs):
        return self._join('INNER', *args, **kvargs)

    def outerJoin(self, *args, **kvargs):
        return self._join('OUTER', *args, **kvargs)

    def outerjoin(self, *args, **kvargs):
        return self._join('OUTER', *args, **kvargs)

    def fullJoin(self, *args, **kvargs):
        return self._join('FULL', *args, **kvargs)

    def fulljoin(self, *args, **kvargs):
        return self._join('FULL', *args, **kvargs)

    def _join_string(self):
        if hasattr(self, '_join_list'):
            return ' '.join([isinstance(x, basestring) and str or hasattr(x, '__str__') and x.__str__() or str(x)
                             for x in self._join_list])
        return None
