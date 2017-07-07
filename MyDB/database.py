# -*- coding:utf8 -*-

################################################################
# Copyright (c) 2008 by icewater.song.
# Created: 2011-8-15 10:43:49
# Modified: 2012/10/15 0:14:10
# Author: icewater.song
# Description: DBFactory
# Version：1.0
# Purpose：DBFactory 数据库
################################################################

import time, new, threading, random
import MySQLdb
import MySQLdb.connections
import MySQLdb.cursors
from MySQLdb import ProgrammingError
from MySQLdb.cursors import BaseCursor, CursorStoreResultMixIn, CursorUseResultMixIn
try:
    import debug
except:
    from ._common import debug
try:
    from common.singleton import SingletonType
except:
    from ._common import SingletonType


def defaulterrorhandler(connection, cursor, errorclass, errorvalue):
    """
    If cursor is not None, (errorclass, errorvalue) is appended to
    cursor.messages; otherwise it is appended to
    connection.messages. Then errorclass is raised with errorvalue as
    the value.

    You can override this with your own error handler by assigning it
    to the instance.
    """
    error = errorclass, errorvalue
    if cursor:
        cursor.messages.append(error)
    else:
        connection.messages.append(error)
    connection.lasterror = error
    del cursor
    del connection
    raise errorclass(errorvalue)


MySQLdb.connections.Connection.lasterror = None
MySQLdb.connections.Connection.errorhandler = new.instancemethod(defaulterrorhandler, None, MySQLdb.connections.Connection)


def groupby(lst, **kwargs):
    d = {}
    for x in lst:
        key = kwargs['key'](x) if 'key' in kwargs else x
        if key not in d:
            d[key] = []
        d[key].append(x)
    return d.items()


class ErrorDatabase(Exception):
    pass


class Cursor(MySQLdb.cursors.Cursor):
    pass


class SSCursor(MySQLdb.cursors.SSCursor):
    pass


class DictCursor(MySQLdb.cursors.DictCursor):
    pass


class SSDictCursor(MySQLdb.cursors.SSDictCursor):
    pass


class CursorUseResultDynamicMixIn(CursorUseResultMixIn):

    """This is a MixIn class which causes the result set to be stored
    in the server and sent row-by-row to client side, i.e. it uses
    mysql_use_result(). You MUST retrieve the entire result set and
    close() the cursor before additional queries can be peformed on
    the connection."""

    def __init__(self, *args, **kvargs):
        self._dynamic_fetch_type = 0
        if "fetchtype" in kvargs:
            self._dynamic_fetch_type = kvargs['fetchtype']

    def fetchone(self, fetchtype=None):
        """Fetches a single row from the cursor."""
        self._check_executed()
        r = self._fetch_row(1, fetchtype)
        if not r:
            self._warning_check()
            return None
        self.rownumber = self.rownumber + 1
        return r[0]

    def fetchmany(self, size=None, fetchtype=None):
        """Fetch up to size rows from the cursor. Result set may be smaller
        than size. If size is not defined, cursor.arraysize is used."""
        self._check_executed()
        r = self._fetch_row(size or self.arraysize, fetchtype)
        self.rownumber = self.rownumber + len(r)
        if not r:
            self._warning_check()
        return r

    def fetchall(self, fetchtype=None):
        """Fetchs all available rows from the cursor."""
        self._check_executed()
        r = self._fetch_row(0, fetchtype)
        self.rownumber = self.rownumber + len(r)
        self._warning_check()
        return r

    def _fetch_row(self, size=1, fetchtype=None):
        if not self._result:
            return ()

        if fetchtype is None:
            fetchtype = self._dynamic_fetch_type
        if isinstance(fetchtype, list) or fetchtype is list:
            fetchtype = 0
        elif isinstance(fetchtype, dict) or fetchtype is dict:
            fetchtype = 1
        else:
            fetchtype = fetchtype and 1 or 0

        return self._result.fetch_row(size, fetchtype)

    def set_fetch_type(self, fetchtype):
        self._dynamic_fetch_type = fetchtype
        return self


class SSDynamicCursor(CursorUseResultDynamicMixIn, BaseCursor):
    def __init__(self, *args, **kvargs):
        CursorUseResultDynamicMixIn.__init__(self, *args, **kvargs)
        MySQLdb.cursors.BaseCursor.__init__(self, *args, **kvargs)


# ----------------
# 实现结果集用"."访问，如：rs[0].id
class Dict(dict):

    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        del self[key]


class SuperDictCursor(CursorStoreResultMixIn, BaseCursor):

    _fetch_type = 1

    def fetchone(self):
        return Dict(CursorStoreResultMixIn.fetchone(self))

    def fetchmany(self, size=None):
        return tuple(Dict(r) for r in CursorStoreResultMixIn.fetchmany(self, size))

    def fetchall(self):
        return tuple(Dict(r) for r in CursorStoreResultMixIn.fetchall(self))


class BaseConnection(MySQLdb.connections.Connection):

    __config = None

    def __init__(self, **kvargs):
        assert(kvargs)

        self.id = random.randint(1000, 9999)
        self.name = kvargs.get('name') or 'default'
        self.debuglevel = 'debuglevel' in kvargs and kvargs['debuglevel']
        self.debug('connect.')

        config = dict((k, v) for k, v in kvargs.items() if k not in ["name", "debuglevel"])
        super(BaseConnection, self).__init__(**config)

        # self.cursor().execute("SET NAMES 'UTF8';")
        # debug(self.character_set_name())
        self.set_character_set('UTF8')

    def debug(self, *args):
        if self.debuglevel or DBFactory().debuglevel:
            debug('BaseConnection:{0}:{1}'.format(self.name, self.id), *args)

    def error(self, *args):
        debug('Error! BaseConnection:{0}:{1}'.format(self.name, self.id), *args)

    def cursor(self, cursorclass=None):

        if isinstance(cursorclass, dict):
            return DictCursor(self)

        if isinstance(cursorclass, list):
            return Cursor(self)

        if isinstance(cursorclass, MySQLdb.cursors.BaseCursor):
            return cursorclass(self)

        return SSDynamicCursor(self)

    def close(self):
        self.debug('close.')
        super(BaseConnection, self).close()


class Connection(object):
    """连接池中的连接描述"""

    CONNECTIONARGS = ('host', 'port', 'user', 'passwd', 'db', 'charset', 'debuglevel')
    debuglevel = None
    counter = 0

    def __init__(self, **kwargs):
        self.__class__.counter += 1
        self.id = self.__class__.counter
        self.name = kwargs.get('name') or 'default'
        self.debug('create')
        # connect to database
        self.config = kwargs
        self.connection = BaseConnection(**dict((k, v) for k, v in kwargs.items() if k in self.CONNECTIONARGS))
        self.debuglevel = kwargs.get('debuglevel')
        self.created = time.time()

    def debug(self, *args):
        if self.debuglevel or DBFactory().debuglevel:
            debug('Connection:{}:{}'.format(self.name, self.id), *args)

    def error(self, *args):
        debug('Error! Connection:{}:{}'.format(self.name, self.id), *args)

    def isvalid(self):
        """ 获取连接有效状态，True当前连接有效，False当前连接失效 """
        if not self.connection:
            return False
        if self.connection.lasterror and not isinstance(self.connection.lasterror[1], ProgrammingError):
            return False
        return True

    def close(self):
        """ 关闭并销毁当前连接 """
        try:
            if self.connection:
                self.debug('close.')
                self.connection.close()
        except Exception, e:
            self.error('close.\n {0}'.format(ErrorDatabase(e).tostring()))
        finally:
            self.connection = None

    def commit(self):
        self.debug('commit.')
        self.connection.commit()

    def rollback(self):
        self.debug('rollback.')
        if self.isvalid():
            self.connection.rollback()

    def __getattr__(self, attr):
        try:
            return getattr(self.connection, attr)
        except Exception, e:
            self.error(e)
            self.close()


class ConnectionPool(object):

    timeout = 3600
    maxconn = 99
    debuglevel = None

    def __init__(self, **kwargs):
        self.name = kwargs.get('name') or 'default'
        self.config = kwargs
        self.debuglevel = kwargs.get('debuglevel')
        self.maxconn = kwargs.get('maxconn', 99)
        if not isinstance(self.maxconn, int): self.maxconn = int(self.maxconn, 10)
        self.timeout = kwargs.get('timeout', 3600)
        if not isinstance(self.timeout, int): self.timeout = int(self.timeout, 10)
        self.lock = threading.RLock()   # 连接池锁
        self.connections = []

    def debug(self, *args):
        if self.debuglevel or DBFactory().debuglevel:
            debug('ConnectionPool:{0}'.format(self.name), *args)

    def error(self, *args):
        debug('Error! ConnectionPool:{0}'.format(self.name), *args)

    def _connect(self):
        '''创建一个新连接'''
        config = self.config
        config['debuglevel'] = self.debuglevel
        config['autocommit'] = config.get('autocommit', False) in (True, 'true', '1')
        return Connection(**config)

    def _clean(self):
        """ 清除连接池前面无效或超时的连接 """
        now = time.time()
        for i, connection in enumerate(self.connections):
            if not connection.isvalid():
                self.debug('drop invalid connection {0}.'.format(connection.id))
                connection.close()
                continue
            if now - connection.created > self.timeout:
                self.debug('drop timeout connection {0}.'.format(connection.id))
                connection.close()
                continue
            self.connections.remove(connection)
            break

    def getConnection(self):
        ''' 获取一个有效连接 '''
        connection = None
        with self.lock:
            # get from pool
            self._clean()
            if self.connections:
                connection = self.connections.pop(0)

        # new connection
        if not connection:
            connection = self._connect()

        # debug log pool size
        self.debug('left size={0}, return connection:{1}:{2}.'.format(
            len(self.connections), connection.name, connection.id))

        return connection

    @property
    def connection(self):
        return self.getConnection()

    def pushback(self, connection):
        ''' 归还一个连接 '''
        # check connection status
        if not connection.isvalid():
            self.debug('connection:{0}:{1} invalid, drop while pushback.'.format(
                connection.name, connection.id))
            connection.close()
            return None

        # clear connection status
        try:
            connection.rollback()
        except Exception, e:
            self.error('connection:{0}:{1} rollback error, while pushback.'.format(
                connection.name, connection.id), e)
            connection.close()
            return None

        # 放回连接池
        with self.lock:
            self.connections.append(connection)
            if len(self.connections) > self.maxconn: self._clean()
            if len(self.connections) > self.maxconn: self.connections.pop(0).close()
        self.debug('pushback connection:{0}:{1} success. pool size is {2}'.format(
            connection.name, connection.id, len(self.connections)))

    def clear(self):
        ''' 清除/断开所有连接 '''
        if self.connections:
            self.debug('Clean connections.')
            for c in self.connections: c.close()
            self.connections = []
        self.debug('Skip clean connections.')


class ThreadingConnections(object):

    debuglevel = None

    def __init__(self, **kwargs):
        self.debuglevel = kwargs.get('debuglevel')
        self._connections = {}  # {'datbase':{'trancection':}, ...}

    def debug(self, *args):
        if self.debuglevel or DBFactory().debuglevel:
            debug('ThreadingConnections', *args)

    def error(self, *args):
        debug('Error! ThreadingConnections', *args)

    def get(self, database=None, transaction=None):
        if not database: database = 'default'
        if database not in self._connections:
            return None
        conn = self._connections[database].get(transaction)
        if conn and not conn.isvalid():
            self.remove(conn)
            return None
        return conn

    def set(self, database, transaction, connection):
        if not database: database = 'default'
        if database not in self._connections:
            self._connections[database] = {}
        self._connections[database][transaction] = connection
        return connection

    def remove(self, connection):
        cs = self._connections.get(connection.name, {})
        for name, conn in cs.items():
            if conn is connection:
                self.debug('remove({}, {})'.format(connection.name, name))
                del(cs[name])
                return

    @property
    def connections(self):
        return reduce(lambda a, b: a + b, [x.values() for x in self._connections.values()], [])

    def clear(self):
        try:
            db = DBFactory()
            for dbname, trs in self._connections.items():
                for trname, connection in trs.items():
                    self.debug('ThreadingConnections::clear({}, {}).'.format(dbname, trname))
                    db.pushback(connection)
        except Exception, e:
            import ExException
            self.error(ExException(e).tostring())
        finally:
            self._connections = {}


class DBFactory():

    __metaclass__ = SingletonType

    __configs = {}

    auto_connect = True

    def __init__(self, debuglevel=None):
        self.debuglevel = debuglevel
        self.debug("DBFactory initialize... ")
        self.localdata = threading.local()      # 用于存储线程连接
        self.pools = {}                         # 全局连接池
        self.configs = {}
        # threading.currentThread().ident

    def set_debuglevel(self, level):
        self.debuglevel = level

    def debug(self, *args):
        if self.debuglevel:
            debug('DBFactory', *args)

    def error(self, *args):
        debug('Error! DBFactory', *args)

    def set_config(self, config):
        if not config.get('name'):
            config['name'] = 'default'
        if 'debuglevel' not in config:
            config['debuglevel'] = self.debuglevel
        self.configs[config['name']] = config
        return self

    def initialize(self):
        for name, config in self.configs.items():
            self.debug('Initialize ConnectionPool by name "{0}"'.format(name))
            self.pools[name] = ConnectionPool(**dict((str(k), v) for k, v in config.items()))

    def get_pool(self, database):
        """ 获取指定数据库配置的连接池 """
        if database not in self.pools:
            if database in self.configs:
                # 自动初始化连接池
                self.debug('Initialize ConnectionPool by name "{0}"'.format(database))
                self.pools[database] = ConnectionPool(**self.configs[database])
            else:
                self.error('Connection pool "{0}" not initialized.'.format(database))
                raise ErrorDatabase('Unknown connection name "{0}"'.format(database))
        return self.pools[database]

    def connection(self, database=None, transaction=None):
        """ 为当前线程/任务获取指定链接 """
        database = database or 'default'

        connection = self.cache.get(database, transaction)
        if not connection:
            connection = self.get_pool(database).getConnection()
            self.cache.set(database, transaction, connection)
        return connection

    def pushback(self, connection):
        name = connection.name
        self.cache.remove(connection)
        self.get_pool(name).pushback(connection)

    @property
    def cache(self):
        """ 获取当前线程缓存 """
        if not hasattr(self.localdata, 'connections'):
            self.debug('Create ThreadingConnections().')
            self.localdata.connections = ThreadingConnections(debuglevel=self.debuglevel)
        return self.localdata.connections


if __name__ == '__main__':
    pass
