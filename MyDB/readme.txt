设置数据库连接参数
MyDB.SetConfig(<dict_config>)

设置是否打开日志开关
MyDB.set_debuglevel(True|False)

清除并释放当前线程已经缓冲的连接，通常在每个请求处理结束后会调用以便释放连接资源
MyDB.clear()

初始化MyDB，项目启动时候执行初始化
MyDB.initialize()

获得一个连接
MyDB.connection([database],[transaction])

获得一个游标
MyDB.cursor([database],[transaction])

执行指定的sql
MyDB.query(sql, *args,**kwargs)

事务提交
MyDB.commit(database=None, transaction=None)

事务回滚
MyDB.rollback(database=None, transaction=None)

关闭连接
MyDB.close(database=None, transaction=None)

datebase: 为初始化参数集的名字，默认为default，如果只连接一个数据库则默认即可
transaction：表示在同一个线程中要采用不同的连接则需要采用不同的连接名来区分，
        在同一个线程中，如果未调用clear或close释放连接前，用同样的名字会获取同一个连接
---------------------------------------------------------------
SQL拼装器
---------------------------------------------------------------

获得SelectClass实例
MyDB.select(tablename)

获得InsertClass实例
MyDB.insert(tablename)

获得UpdateClass实例
MyDB.update(tablename)

获得DeleteClass实例
MyDB.delete(tablename)

获得ConditionClass实例, 等同于MyDB.condition(...)
MyDB.where(condition=None, *args, **kwargs)

获得ConditionClass实例, 等同于MyDB.condition(...)
MyDB.having(condition=None, *args, **kwargs)

获得ConditionClass实例
MyDB.condition(condition=None, *args, **kwargs)

获得FieldClass实例
MyDB.field(*args)
*args: fieldname[, aliasname] | field string

获得JoinClass实例
MyDB.join(*args, **kwargs)
eg: MyDB.join('LEFT', [tablename, aliasname], condition)
eg: MyDB.join('LEFT', tablename, joinfield, ontable, onfiled)

获得TableCreatorClass实例
MyDB.table(tablename)

转义vardata字符串
MyDB.real_escape_string(vardata)

转义vardata字符串
MyDB.escape_string(vardata)

---------------------------------------------------------------
SelectClass

sql = MyDB.select(tablename)
sql.field(*args)
sql.fields(*args)
sql.join|leftjoin|rightjoin|innerjoin (*args)
sql.where(...)
sql.whereOr(...)
sql.having(...)
sql.havingOr(...)
sql.group(*args)
sql.order(*args)
sql.limit(*args)
sql.page(page, rspp)
sql.distinct()
sql.into(tablename)
sql.tostring()

sql.field(*args)
变参args模式
    模式1：field|expression
    模式2：field|expression, aliasname
    模式3：tablename, fieldname, aliasname

sql.fields(*args)
变参args[n]模式,指args列表中的任意一个参数
    模式1：'field|expression as aliasname, ...'
    模式2：[field|expression, aliasname]
    模式3：[tablename, fieldname, aliasname]

sql.join(table, *args) leftjoin|rightjoin|innerjoin|...
table: 'tablename as aliasname'|[tablename|SelectInstance, aliasname]
变参args模式
    模式1：条件字符串，"ON"后面的条件字符串
    模式2：ConditionClass实例
    模式3：fieldname, ontable, onfield

sql.where(*args, **kwargs) whereOr(*args, **kwargs)
变参args模式
    模式1：只有一个条件字符串
    模式2：第一个为条件字符串，第二个开始为参数, kwargs为字典参数
           如：where('{0}+{1} > {name}', '100', '200', name='300')
                等同于 where('100+200 > 300')
    模式3：只有一个Condition实例
多次调用where表示用“AND”连接与之前的条件关系，调用whereOr表示“OR”连接

sql.having(*args, **kwargs) havingOr(*args, **kwargs)
参数模式参见where|whereOr

sql.group(*args):
变参args[n]模式
    模式1：expression
    模式2：[tablename, fieldname]

sql.order(*args):
变参args[n]模式
    模式1：expression 表示字段默认升序
    模式2：[expression, 'ASC'|'DESC']
    模式3：[tablename, filedname, 'ASC'|'DESC']

sql.limit(*args)
变参args模式
    模式1：只有一个参数，limit args[0]
    模式1：有两个参数，limit args[0], args[1]

sql.page(page, rspp)
page: 页码，起始页为0
rspp：每页输出行数

sql.distinct()
等价于 SELECT DISTIONCT ...

sql.into(tablename)
等价于 SELECT ... INTO tablename FROM ...

---------------------------------------------------------------
InsertClass

sql = MyDB.insert(tablename)
sql.priority(flag)
sql.ignore(flag)
sql.field(*args)
sql.fields(*args)
sql.value(value=None)
sql.values(*args)
sql.set(*args, **kwargs)
sql.select(select)
sql.update(*args, **kwargs)
sql.duplicate(*args, **kwargs)

sql.priority(flag)
flag: 'PRIORITY_LOW', 'DELAYED', 'PRIORITY_HIGH'
不为空时等价于 INSERT INTO <flag>

sql.ignore(flag)
flag: True|False
为True时等价于 INSERT INTO IGNORE

sql.field(*args) sql.fields(*args)
参数参见Select中的描述

sql.value(value=None)
value为None时，表示结束一行或者开始一新行
value不None，则每调用一次，表示对当前行设置一列数据，并指针向后移动一列
此方法需要调用与列相同数量次数后，以value=None为参数调用一次

sql.values(*args)
变参*args模式
    模式1：只有一个参数，并且为字符串，则表示原始一行或多行 sql 数据， 如："(1,2,3),(4,5,6),..."
    模式2：含有一个或过个数组，则认为args中每一个参数为一行数据，如：(1,2),"(3,4)",[5,6],...

sql.set(*args, **kwargs)
变参模式
    模式1：string
    模式2：key, value
    模式3：key = value, ...

sql.select(select)
select为查询表达式或者Select实例

数据模式优先级
values > set > select

sql.update(*args, **kwargs)
sql.duplicate(*args, **kwargs)
变参模式
    模式1：string
    模式2：key, value
    模式3：key = value, ...

---------------------------------------------------------------
UpdateClass

sql = MyDB.update(tablename)
sql.set_auto_escape(flag)
sql.set(*args, **kwargs)
sql.where(*args, **kwargs)
sql.whereOr(*args, **kwargs)

sql.set_auto_escape(flag=True)
flag: True|False
为True时，若set采用key=value输入，则自动escape(value)

sql.set(*args, **kwargs)
变参模式
    模式1：string
    模式2：key, value
    模式3：key = value, ...

sql.where() whereOr()
参见SelectClass

---------------------------------------------------------------
DeleteClass

sql = MyDB.delete(tablename)
sql.where(*args, **kwargs)
sql.whereOr(*args, **kwargs)

