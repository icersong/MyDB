# -*- coding:UTF8 -*-

from collections import OrderedDict
from abstract import ErrorSql
try:
    import strval
except:
    from .._common import strval


class TableCreatorBase(object):
    def __init__(self, name):
        self.name = name


class Field(TableCreatorBase):

    def __init__(self, name):
        super(Field, self).__init__(name)

    def tostring(self):
        ss = ['`' + self.name + '`']

        # 字段长度处理
        # -- size
        if hasattr(self, 'size') and self.size:
            from common import intval
            self.size = intval(self.size)
        else:
            self.size = None
        # -- decimals
        if hasattr(self, 'decimals') and self.decimals:
            self.size = intval(self.decimals)
        else:
            self.decimals = None

        # 别名处理
        if not hasattr(self, 'autoincrement') and hasattr(self, 'increment'):
            self.autoincrement = self.increment
            delattr(self, 'increment')

        # True|False属性规范处理
        for key in ('unsigned', 'primary', 'key', 'unique', 'binary', 'zerofill',
                    'autoincrement', 'ascii', 'unicode', 'notnull'):
            v = getattr(self, key, None)
            setattr(self, key, (v and str(v).lower() or None) not in [None, '0', 'false'])

        # 字段类型处理 INT/VARCHAR/...
        ftype = self.type.upper()
        if ftype == 'BOOLEAN':
            ss.append('TINYINT(1) UNSIGNED ZEROFILL')
        elif ftype in ('TINYINT', 'SMALLINT', 'MEDIUMINT', 'INT', 'INTEGER', 'BIGINT'):
            ss.append(ftype)
            if self.size is not None and self.size > 0:
                if self.size > 32:
                    raise ErrorSql(u"Too large size({0}) for {1} type.".format(self.size, ftype))
                ss.append('(' + str(self.size) + ')')
            if self.unsigned:
                ss.append('UNSIGNED')
            if self.zerofill:
                ss.append('ZEROFILL')
        elif ftype in ('REAL', 'DOUBLE', 'FLOAT', 'DECIMAL', 'NUMERIC'):
            ss.append(ftype)
            if self.size is not None and self.size > 0 and self.decimals is not None:
                if self.size > 64:
                    raise ErrorSql(u"Too large size({0}) for {1} type.".format(self.size, ftype))
                ss.append('(' + str(self.size) + ',' + str(self.decimals) + ')')
            if self.unsigned:
                ss.append('UNSIGNED')
            if self.zerofill:
                ss.append('ZEROFILL')
        elif ftype == 'CHAR':
            if self.size is not None and self.size > 0:
                ss.append(ftype + '(' + str(self.size) + ')')
            else:
                ss.append(ftype)
            for k in ('binary', 'ascii', 'unicode'):
                if getattr(self, k):
                    ss.append(k.upper())
                    break
        elif ftype in ('STRING', 'VARCHAR'):
            if self.size and self.size > 0 and self.size < 65535 / 3:
                ss.append('VARCHAR(' + str(self.size) + ')')
            else:
                ss.append('TEXT')
                ftype = 'TEXT'
        elif ftype in ('TINYTEXT', 'TEXT', 'MEDIUMTEXT', 'LONGTEXT'):
            ss.append(ftype)
            if self.binary:
                ss.append('BINARY')
        elif ftype == 'DATETIME':
            if 'CURRENT_TIMESTAMP' in (getattr(self, 'default', '') or ''):
                ss.append('TIMESTAMP')
            else:
                ss.append(ftype)
        elif ftype in ('DATE', 'TIME', 'TIMESTAMP', 'DATETIME', 'TINYBLOB',
                'BLOB', 'MEDIUMBLOB', 'LONGBLOB'):
            ss.append(ftype)
        elif ftype == 'interger':
            ss.append('INTEGER' + self.size > 0 and ('(' + str(self.size) + ')') or '')
        else:
            import ExException
            raise ExException('Field (' + self.name + ') not support field type(' + ftype + ')!')

        if self.notnull:
            ss.append('NOT NULL')

        # default value
        if hasattr(self, 'default'):
            default = self.default
            if ftype in ('INT', 'INTEGER', 'FLOAT', 'DOUBLE'):
                if not self.autoincrement and (default or isinstance(default, (int, float))):
                    ss.append("DEFAULT " + strval(default))
            elif ftype in ['DATETIME', 'DATE', 'TIME', 'TIMESTAMP']:
                if default and default.strip():
                    if default[0] in '0123456789':
                        ss.append(u"DEFAULT '{0}'".format(default))
                    else:
                        ss.append(u"DEFAULT {0}".format(default))
            else:
                ss.append(u"DEFAULT {0}".format('null' if default is None
                        else u"'{0}'".format(default)))

        # autoincrement
        if self.autoincrement: ss.append('AUTO_INCREMENT')
        # unique key
        if self.unique: ss.append('UNIQUE KEY')
        #  elif self.key: ss.append('KEY')
        # common
        if hasattr(self, 'comment'):
            ss.append(u"COMMENT '{0}'".format(self.comment))

        return ' '.join(ss)


class Key(TableCreatorBase):

    def __init__(self, name=None, unique=False, fields=None, references=None):
        """ name: key name; unique: True|False; references: (table, field) """
        super(Key, self).__init__(name)
        self._fields = fields or []
        self._unique = unique and unique not in ('false', '0')
        self._references = references
        self._constraint = None
        self._ondelete = None
        self._onupdate = None

    def references(self, table, fields):
        self._references = (table, fields)

    def ondelete(self, action):
        self._ondelete = action

    def onupdate(self, action):
        self._onupdate = action

    def unique(self, unique=True):
        self._unique = unique and unique not in ('false', '0')

    def field(self, field):
        name = isinstance(field, Table) and field.name or str(field)
        self._fields.append(name)
        return self

    def fields(self, *args):
        self._fields = list(args)

    def constraint(self, flag=False):
        self._constraint = flag

    def tostring(self):
        ss = self._constraint and [self._constraint] or []
        if self._references:
            if self.name: ss.append(u'`{0}`'.format(self.name))
            ss.append('FOREIGN KEY')
            ss.append(u'(`{0}`)'.format(u'`,`'.join(self._fields)))
            ss.append('REFERENCES')
            ss.append(u'{0}(`{1}`)'.format(self._references[0], '`,`'.join(self._references[1])))
            if self._ondelete:
                ss.append('ON DELETE')
                ss.append(self._ondelete.upper())
            if self._onupdate:
                ss.append('ON UPDATE')
                ss.append(self._onupdate.upper())
        else:
            if self._unique: ss.append('UNIQUE')
            ss.append('KEY')
            if self.name: ss.append('`{0}`'.format(self.name))
            ss.append('(`{0}`)'.format('`,`'.join(self._fields)))
        return ' '.join(ss)


class Table(TableCreatorBase):

    def __init__(self, name):
        super(Table, self).__init__(name)
        self.fields = OrderedDict()
        self._keys = []
        self.ifnotexists = False

    def field(self, name):
        if name not in self.fields:
            self.fields[name] = Field(name)
        return self.fields[name]

    def key(self, *args, **kwargs):
        self._keys.append(Key(*args, **kwargs))
        return self._keys[-1]

    def __str__(self):
        return self._tostring()

    def toString(self):
        return self._tostring()

    def tostring(self):
        return self._tostring()

    def _tostring(self):
        # table head
        sql = ['CREATE TABLE {0} `{1}`(\n  '.format(
            self.ifnotexists and 'IF NOT EXISTS' or '', self.name)]
        # {ss}
        ss = []
        # fields
        ss.extend(field.tostring() for field in self.fields.values())
        # primary keys
        keys = [name for name, field in self.fields.items() if field.primary]
        if keys: ss.append('PRIMARY KEY (`{0}`)'.format('`,`'.join(keys)))
        # index keys, but not unique keys or primary keys
        ss.extend(['KEY (`{0}`)'.format(name)
                   for name, field in self.fields.items()
                   if field.key and not field.unique])
        # specified keys
        ss.extend(key.tostring() for key in self._keys)
        # table content
        sql.append(',\n  '.join(ss))
        # table tail
        sql.append("\n) ENGINE=InnoDB CHARACTER SET 'utf8' COLLATE 'utf8_unicode_ci'")
        sql.append(hasattr(self, 'comment') and "\n COMMENT '" + self.comment + "'" or '')

        return ''.join(sql)
