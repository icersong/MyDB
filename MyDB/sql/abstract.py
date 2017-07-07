# -*- coding:utf8 -*-
# -*- 中文 -*-

import re
from abc import abstractmethod
import _mysql

try:
    import ExException
except:
    import sys, traceback

    class ExException(Exception):
        def __init__(self, *args, **kvargs):
            super(ExException, self).__init__(*args, **kvargs)
            self.extract_tb = traceback.extract_tb(sys.exc_info()[-1])
            self.extract_stack = traceback.extract_stack()

        def tostring(self):
            traceinfo = ["Trace exceptions:"]
            traceinfo.extend(['  - ' + str(x)[1:-1] for x in self.extract_stack[:-1]])
            traceinfo.append("%s: %s" % (self.__class__.__name__, str([x for x in self.args if not isinstance(x, Exception)])[1:-1]))

            exceptions = [self]
            while exceptions[-1]:
                exceptions.extend([x for x in exceptions[-1].args if isinstance(x, Exception)] or [None])
            exceptions = exceptions[1:-1]

            traceinfo.extend(['  - ' + str(x)[1:-1] for x in self.extract_tb])

            for exception in exceptions:
                traceinfo.append("%s: %s" % (exception.__class__.__name__,
                                             str([x for x in exception.args if not isinstance(x, Exception)])[1:-1]))
                traceinfo.extend(['  - ' + str(x)[1:-1]
                                  for x in (isinstance(exception, self.__class__) and exception.extract_tb or [])])

            return '\n'.join(traceinfo)


class ErrorSql(ExException): pass


class ErrorSqlTableName(ErrorSql): pass


def tovalue(v, escape=False):
    """ convert variable to sql value string, """
    """ if value object has tosql methed, return tosql() result only """
    """ otherwaise (eg: basestring), return it as string with comma and escape it """
    if v is None: return 'NULL'
    if isinstance(v, basestring): return u"'{0}'".format(escape_string(v) if escape else v)
    if isinstance(v, (int, float)): return str(v)
    if hasattr(v, 'tosql'): return v.tosql()
    if hasattr(v, 'tostring'): v = v.tostring()
    return u"'{0}'".format(escape_string(v if escape else v))


class SqlBase(object):
    """ SQL Base string container, with default tosql method """
    def __init__(self, default=None, escape=False):
        self._value = default
        self._auto_escape = escape

    def set_auto_escape(self, flag=True):
        self._auto_escape = flag
        return self

    def tosql(self):
        v = self._value
        if v is None: return 'NULL'
        if isinstance(v, basestring): return v
        if hasattr(v, 'tosql'): return v.tosql()
        if hasattr(v, 'tostring'): return v.tostring()
        return str(v)


DEFALUT = SqlBase('DEFAULT')


class Formatter(object):

    parent = property(lambda self: self._parent)

    def __init__(self, parent=None):
        self._parent = parent

    def set_indent_front(self, indent):
        """
        设置当前区块前导
        """
        self._indent_front = indent
        return self

    def get_indent_front(self):
        """
        获得当前区块前导
        """
        if not hasattr(self, '_indent_front'):
            self._indent_front = self.parent and (self.parent.indent_front + self.parent.indent_block) or ""
        return self._indent_front

    # 当前区块前导缩进
    indent_front = property(get_indent_front)

    def set_indent_spaces(self, indent):
        """
        设置子区块缩进值
        """
        self._indent_spaces = indent
        return self

    def get_indent_spaces(self):
        """
        获得子区块缩进值
        """
        return self._indent_spaces if hasattr(self, '_indent_block') else "  "

    # 基础缩进值
    indent_spaces = property(get_indent_spaces)

    def push(self, *args):
        self._buffer.push(list(args))

    def tostring(self):
        ss = self.parent \
            and ["".join(x.insert(0, self.indent_spaces) or x.append("\n") or x)
                 for x in self._buffer] \
            or ["".join(x.append("\n") or x) for x in self._buffer]
        return self.indent_front.join(ss)

    def __str__(self):
        return self.tostring()

    def create(self):
        c = self.__class__(self)
        self.push(c)
        return c


def UNICODE(sstr):
    if isinstance(sstr, unicode):
        return sstr

    if not isinstance(sstr, str):
        try:
            sstr = str(sstr)
        except Exception, e:
            if hasattr(sstr, '__str__'):
                sstr = sstr.__str__()
            else:
                raise e

    if isinstance(sstr, str):
        ee = []
        for c in ('UTF8', 'GB18030'):
            try:
                return sstr.decode(c)
            except Exception, e:
                ee.append(e)

        raise ErrorSql(ee)

    assert(isinstance(sstr, unicode))

    return sstr


def _parse_table_name(table, doraise=True):
    """
    分析table表达式
    返回：table, alias
    """

    if isinstance(table, Abstract):
        return table, None

    elif isinstance(table, basestring):
        # 标准 table & alias
        ptable = '`?(?P<table>[a-z_][\w:]+)`?'
        palias = '`?(?P<alias>[a-z_][\w:]+)`?'
        p = re.compile(u'^\s*{0}(\s+as\s+{1})?\s*$'.format(ptable, palias), re.IGNORECASE)
        m = p.match(table)
        if m:
            d = m.groupdict()
            return d['table'], d['alias']

        # 子查询 table & alias
        # (select ...) as alias
        ptable = '(?P<table>\\(.+\\))'
        palias = '`?(?P<alias>[a-z_][\w:]+)`?'
        p = re.compile(u'^\s*{0}\s*as\s+{1}\s*$'.format(ptable, palias), re.IGNORECASE)
        m = p.match(table)
        if m:
            d = m.groupdict()
            return UNICODE(d['table']), d['alias']

        # select ... or (select ...)
        p = re.compile('^\s*(\\(?\s*)*select\s+.*\\)?\s*$', re.IGNORECASE)
        m = p.match(table)
        if m:
            table = table.strip()
            return u'({0})'.format(UNICODE(table)), None

        raise ErrorSqlTableName(u'Unknown table string. {0}'.format(UNICODE(table)))

    elif isinstance(table, (list, tuple)):
        assert(table)
        t, a = _parse_table_name(table[0])
        if len(table) > 1 and table[1]:
            a = table[1].strip().strip('`')
        if t:
            return t, a

    elif doraise:
        raise ErrorSqlTableName(u'Can not parse table, {0}'.format(table))

    return None, None


def escape_string(vardata):
    if isinstance(vardata, unicode):
        for valuecode in ('UTF8', 'GB2312'):
            try:
                vardata = vardata.encode(valuecode)
                vardata = _mysql.escape_string(vardata)
                return vardata.decode(valuecode)
            except:
                continue
        raise ErrorSql(u'Error. escape string "{0}"'.format(vardata))
    return _mysql.escape_string(vardata) if isinstance(vardata, str) else vardata


class Abstract(object):

    _auto_escape = None

    def __init__(self, *args, **kvargs):
        self._tables = []

        if args or kvargs:
            self.table(*args, **kvargs)

    def set_auto_escape(self, flag=True):
        self._auto_escape = flag
        return self

    def escape(self, vardata):
        return escape_string(vardata) if self._auto_escape else vardata

    def table(self, table, alias=None):
        t, a = _parse_table_name(table)
        if alias:
            a = alias.strip().strip('`')

        self._tables.append([t, a])

        return self

    def _table_string(self):
        assert(len(self._tables))
        ss = []
        for t, a in self._tables:
            if isinstance(t, basestring):
                if t[0] == '(' and t[-1] == ')':
                    if not a:
                        raise ErrorSql('Every derived table must have its own alias.')
                    ss.append(u'{0} AS `{1}`'.format(t, a))
                else:
                    ss.append(a and u'`{0}` AS `{1}`'.format(t, a) or u'`{0}`'.format(t))
                continue
            if isinstance(t, Abstract):
                if not a:
                    raise ErrorSql('Every derived table must have its own alias.')
                ss.append(u'({0}) AS `{1}`'.format(t.tostring(), a))
                continue
            raise ErrorSql('Unknown table info (', t, ', ', a, ')')

        return ', '.join(ss)

    def __str__(self, strtype=None):
        return self._tostring()

    def tostring(self):
        return self._tostring()

    def toString(self):
        return self._tostring()

    @abstractmethod
    def _tostring(self):
        pass
