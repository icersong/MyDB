#!/usr/bin/env python
# -*- coding: utf-8 -*-

from MySQLdb import *

from database import DBFactory, ErrorDatabase
from sql.select import Select as select
from sql.insert import Insert as insert
from sql.update import Update as update
from sql.delete import Delete as delete
from sql.conditions import Condition as condition
from sql.conditions import Condition as having
from sql.conditions import Condition as where
from sql.fields import Field as field
from sql.joins import Join as join
from sql.table import Table as table
from sql.conditions import and_, or_

import warnings

warnings.filterwarnings("ignore", "^Unknown table '[0-9a-zA-Z_]+'$")
warnings.filterwarnings("ignore", "Table '[0-9a-zA-Z_]+' already exists.*")


def SetConfig(config):
    """
    config: dict as MySQLdb.connect parameters
    """
    return DBFactory().set_config(config)


def set_debuglevel(level):
    DBFactory().set_debuglevel(level)


def initialize():
    DBFactory().initialize()


# 无论指定名称的连接是否存在都会创建一个新的连接
# 注，每次WEB请求的开始建议创建新连接，以保证连接的有效性
def connect(database=None, transaction=None):
    return None


# 获取指定名称的连接，如果不存在则创建一个新连接
def connection(database=None, transaction=None, autoconnect=True, doraise=True):
    conn = DBFactory().connection(database, transaction)
    if not conn and doraise:
        raise ErrorDatabase('Can not get active connection by name "%s"' % (database))
    return conn


def cursor(database=None, transaction=None, cursorclass=None):
    return connection(database, transaction).cursor(cursorclass)


def query(sqlstr, *args, **kwargs):
    """
    sqlstr: 标准的SQL字符串或者SQL拼装类
    name: 链接名称，必须为字符串，位置不限
    cursorclass: 返回数据的游标类，可以是[] 或者 {}
        None: Cursor
        {} : DictCursor
        [] : Cursor
    """
    database = None
    cursorclass = None
    for x in args:
        if isinstance(x, (str, unicode)):
            database = x
        else:
            cursorclass = x
    database = kwargs.get('database', database)
    transaction = kwargs.get('transaction')
    doraise = kwargs.get('doraise', True)
    autoconnect = kwargs.get('autoconnect', True)
    cursorclass = kwargs.get('cursorclass', cursorclass)
    cursor = connection(database, transaction, autoconnect, doraise).cursor(cursorclass)

    try:
        if not isinstance(sqlstr, (str, unicode)):
            sqlstr = sqlstr.tostring()
        cursor.execute(sqlstr)
    except Exception, e:
        raise ErrorDatabase(sqlstr, e)
    return cursor


def fetchone(sql, *args, **kwargs):
    cursor = query(sql, **kwargs)
    one = cursor.fetchone(*args)
    cursor.close()
    return one


def fetchall(sql, *args, **kwargs):
    cursor = query(sql, **kwargs)
    rs = cursor.fetchall(*args)
    cursor.close()
    return rs


def commit(database=None, transaction=None):
    db = DBFactory()
    for conn in db.cache.connections:
        conn.commit()
        db.pushback(conn)


def rollback(database=None, transaction=None, doraise=False):
    db = DBFactory()
    for conn in db.cache.connections:
        conn.rollback()
        db.pushback(conn)


def reset():
    """ 清除当前线程缓冲连接 """
    DBFactory().cache.clear()


def clear():
    """ 清除当前线程缓冲连接 """
    DBFactory().cache.clear()


def close():
    """ 清除当前线程缓冲连接 """
    DBFactory().cache.clear()


################################################################
# SQL 拼装器获取函数
####


def real_escape_string(vardata, database=None, transaction=None):
    return connection(database, transaction).escape_string(vardata)


def escape_string(vardata, database=None, transaction=None):
    if isinstance(vardata, unicode):
        errors = []
        for valuecode in ('UTF8', 'GB2312'):
            try:
                vardata = vardata.encode(valuecode)
                vardata = connection(database, transaction).escape_string(vardata)
                break
            except Exception, e:
                errors.append(e)
        else:
            raise ErrorDatabase('Error. escape string "{0}", {1}'.format(vardata, errors))

        return vardata.decode(valuecode)

    return connection(database, transaction).escape_string(vardata)


def escape(vardata, database=None, transaction=None):
    return escape_string(vardata)


def set_auto_escape(flag=True):
    from sql import set_auto_escape as _set_auto_escape
    _set_auto_escape(flag)


__all__ = [
    'SetConfig',
    'set_debuglevel',
    'initialize',
    'clear',
    'connect',
    'connection',
    'cursor',
    'query',
    'commit',
    'rollback',
    'select',
    'insert',
    'update',
    'delete',
    'where',
    'having',
    'condition',
    'having',
    'field',
    'join',
    'table',
    'real_escape_string',
    'real_escape',
    'set_auto_escape',
    'and_',
    'or_',

    'BINARY', 'Binary', 'Connect', 'Connection', 'DATE',
    'Date', 'Time', 'Timestamp', 'DateFromTicks', 'TimeFromTicks',
    'TimestampFromTicks', 'DataError', 'DatabaseError', 'Error',
    'FIELD_TYPE', 'IntegrityError', 'InterfaceError', 'InternalError',
    'MySQLError', 'NULL', 'NUMBER', 'NotSupportedError', 'DBAPISet',
    'OperationalError', 'ProgrammingError', 'ROWID', 'STRING', 'TIME',
    'TIMESTAMP', 'Warning', 'apilevel', 'connect', 'connections',
    'constants', 'converters', 'cursors', 'debug', 'escape', 'escape_dict',
    'escape_sequence', 'escape_string', 'get_client_info',
    'paramstyle', 'string_literal', 'threadsafety', 'version_info']
