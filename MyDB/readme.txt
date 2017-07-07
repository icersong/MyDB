�������ݿ����Ӳ���
MyDB.SetConfig(<dict_config>)

�����Ƿ����־����
MyDB.set_debuglevel(True|False)

������ͷŵ�ǰ�߳��Ѿ���������ӣ�ͨ����ÿ������������������Ա��ͷ�������Դ
MyDB.clear()

��ʼ��MyDB����Ŀ����ʱ��ִ�г�ʼ��
MyDB.initialize()

���һ������
MyDB.connection([database],[transaction])

���һ���α�
MyDB.cursor([database],[transaction])

ִ��ָ����sql
MyDB.query(sql, *args,**kwargs)

�����ύ
MyDB.commit(database=None, transaction=None)

����ع�
MyDB.rollback(database=None, transaction=None)

�ر�����
MyDB.close(database=None, transaction=None)

datebase: Ϊ��ʼ�������������֣�Ĭ��Ϊdefault�����ֻ����һ�����ݿ���Ĭ�ϼ���
transaction����ʾ��ͬһ���߳���Ҫ���ò�ͬ����������Ҫ���ò�ͬ�������������֣�
        ��ͬһ���߳��У����δ����clear��close�ͷ�����ǰ����ͬ�������ֻ��ȡͬһ������
---------------------------------------------------------------
SQLƴװ��
---------------------------------------------------------------

���SelectClassʵ��
MyDB.select(tablename)

���InsertClassʵ��
MyDB.insert(tablename)

���UpdateClassʵ��
MyDB.update(tablename)

���DeleteClassʵ��
MyDB.delete(tablename)

���ConditionClassʵ��, ��ͬ��MyDB.condition(...)
MyDB.where(condition=None, *args, **kwargs)

���ConditionClassʵ��, ��ͬ��MyDB.condition(...)
MyDB.having(condition=None, *args, **kwargs)

���ConditionClassʵ��
MyDB.condition(condition=None, *args, **kwargs)

���FieldClassʵ��
MyDB.field(*args)
*args: fieldname[, aliasname] | field string

���JoinClassʵ��
MyDB.join(*args, **kwargs)
eg: MyDB.join('LEFT', [tablename, aliasname], condition)
eg: MyDB.join('LEFT', tablename, joinfield, ontable, onfiled)

���TableCreatorClassʵ��
MyDB.table(tablename)

ת��vardata�ַ���
MyDB.real_escape_string(vardata)

ת��vardata�ַ���
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
���argsģʽ
    ģʽ1��field|expression
    ģʽ2��field|expression, aliasname
    ģʽ3��tablename, fieldname, aliasname

sql.fields(*args)
���args[n]ģʽ,ָargs�б��е�����һ������
    ģʽ1��'field|expression as aliasname, ...'
    ģʽ2��[field|expression, aliasname]
    ģʽ3��[tablename, fieldname, aliasname]

sql.join(table, *args) leftjoin|rightjoin|innerjoin|...
table: 'tablename as aliasname'|[tablename|SelectInstance, aliasname]
���argsģʽ
    ģʽ1�������ַ�����"ON"����������ַ���
    ģʽ2��ConditionClassʵ��
    ģʽ3��fieldname, ontable, onfield

sql.where(*args, **kwargs) whereOr(*args, **kwargs)
���argsģʽ
    ģʽ1��ֻ��һ�������ַ���
    ģʽ2����һ��Ϊ�����ַ������ڶ�����ʼΪ����, kwargsΪ�ֵ����
           �磺where('{0}+{1} > {name}', '100', '200', name='300')
                ��ͬ�� where('100+200 > 300')
    ģʽ3��ֻ��һ��Conditionʵ��
��ε���where��ʾ�á�AND��������֮ǰ��������ϵ������whereOr��ʾ��OR������

sql.having(*args, **kwargs) havingOr(*args, **kwargs)
����ģʽ�μ�where|whereOr

sql.group(*args):
���args[n]ģʽ
    ģʽ1��expression
    ģʽ2��[tablename, fieldname]

sql.order(*args):
���args[n]ģʽ
    ģʽ1��expression ��ʾ�ֶ�Ĭ������
    ģʽ2��[expression, 'ASC'|'DESC']
    ģʽ3��[tablename, filedname, 'ASC'|'DESC']

sql.limit(*args)
���argsģʽ
    ģʽ1��ֻ��һ��������limit args[0]
    ģʽ1��������������limit args[0], args[1]

sql.page(page, rspp)
page: ҳ�룬��ʼҳΪ0
rspp��ÿҳ�������

sql.distinct()
�ȼ��� SELECT DISTIONCT ...

sql.into(tablename)
�ȼ��� SELECT ... INTO tablename FROM ...

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
��Ϊ��ʱ�ȼ��� INSERT INTO <flag>

sql.ignore(flag)
flag: True|False
ΪTrueʱ�ȼ��� INSERT INTO IGNORE

sql.field(*args) sql.fields(*args)
�����μ�Select�е�����

sql.value(value=None)
valueΪNoneʱ����ʾ����һ�л��߿�ʼһ����
value��None����ÿ����һ�Σ���ʾ�Ե�ǰ������һ�����ݣ���ָ������ƶ�һ��
�˷�����Ҫ����������ͬ������������value=NoneΪ��������һ��

sql.values(*args)
���*argsģʽ
    ģʽ1��ֻ��һ������������Ϊ�ַ��������ʾԭʼһ�л���� sql ���ݣ� �磺"(1,2,3),(4,5,6),..."
    ģʽ2������һ����������飬����Ϊargs��ÿһ������Ϊһ�����ݣ��磺(1,2),"(3,4)",[5,6],...

sql.set(*args, **kwargs)
���ģʽ
    ģʽ1��string
    ģʽ2��key, value
    ģʽ3��key = value, ...

sql.select(select)
selectΪ��ѯ���ʽ����Selectʵ��

����ģʽ���ȼ�
values > set > select

sql.update(*args, **kwargs)
sql.duplicate(*args, **kwargs)
���ģʽ
    ģʽ1��string
    ģʽ2��key, value
    ģʽ3��key = value, ...

---------------------------------------------------------------
UpdateClass

sql = MyDB.update(tablename)
sql.set_auto_escape(flag)
sql.set(*args, **kwargs)
sql.where(*args, **kwargs)
sql.whereOr(*args, **kwargs)

sql.set_auto_escape(flag=True)
flag: True|False
ΪTrueʱ����set����key=value���룬���Զ�escape(value)

sql.set(*args, **kwargs)
���ģʽ
    ģʽ1��string
    ģʽ2��key, value
    ģʽ3��key = value, ...

sql.where() whereOr()
�μ�SelectClass

---------------------------------------------------------------
DeleteClass

sql = MyDB.delete(tablename)
sql.where(*args, **kwargs)
sql.whereOr(*args, **kwargs)

