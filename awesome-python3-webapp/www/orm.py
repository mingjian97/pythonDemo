import asyncio
import aiomysql
import logging
logging.basicConfig(level=logging.INFO)

__autor__="mingjian"

def log(sql, args=()):
    logging.info('SQL: %s' % sql)

#创建全局的数据库连接池,每个http请求都从池中获得数据库连接
@asyncio.coroutine
def create_pool(loop,**kw):
    logging.info('create database connection...')
    #全局__pool用于存储整个连接池
    
    global __pool
    __pool = yield from aiomysql.create_pool(
        host=kw.get('host','localhost'),
        port=kw.get('port',3306),
        user=kw['user'],
        password=kw['password'],
        db=kw['database'],
        charset=kw.get('charset','utf8'),
        autocommit=kw.get('autocommit',True),
        maxsize=kw.get('maxsize',10),
        minsize=kw.get('minsize',1),
        #接收一个event_loop实例
        loop=loop
    )    
        
@asyncio.coroutine
def select(sql,args,size=None):
    log(sql,args)
    global __pool
    with (yield from __pool) as conn:
        cur = yield from conn.cursor(aiomysql.DictCursor)
        yield from cur.execute(sql.replace('?','%s'),args or ())
        if size:
            rs=yield from cur.fetchmany(size)
        else:
            rs=yield from cur.fetchall()
        yield from cur.close()
        logging.info('rows returned: %s'%len(rs))
        return rs

@asyncio.coroutine
def execute(sql,args):
    log(sql)
    with (yield from __pool) as conn:
        try:
            cur=yield from conn.cursor()
            yield from cur.execute(sql.replace('?','%s'),args)
            affected=cur.rowcount
            yield from cur.close()
        except BaseException as e:
            raise
        return affected

# 根据参数数量生成SQL占位符'?'列表
def create_args_string(num):
    L=[]
    for n in range(num):
        L.append('?')
    # 以', '为分隔符，将列表合成字符串
    return ', '.join(L)

class ModelMetaclass(type):
     # __new__控制__init__的执行，所以在其执行之前
     
    def __new__(cls,name,bases,attrs):
        
        if name=='Model':
            return type.__new__(cls,name,bases,attrs)
        
        tableName=attrs.get('__table__',None) or name
        logging.info("found model:%s (table: %s)"%(name,tableName))
        mappings=dict()
        fields=[]
        primaryKey=None
        for k,v in attrs.items():
            if isinstance(v,Field):
                logging.info('  found mapping: %s==>%s'%(k,v))
                mappings[k]=v
                if v.primary_key:
                    if primaryKey:
                        raise RuntimeError('Duplicate primary key for field:%s'%k)
                    primaryKey=k
                else:
                    fields.append(k)
        if not primaryKey:
            raise RuntimeError('Primary key not found')
        for k in mappings.keys():
            attrs.pop(k)
        escaped_fields=list(map(lambda f: '`%s`' % f, fields))
        # ``反引号功能同repr()
        attrs['__mappings__']=mappings #保存属性和列的映射关系
        attrs['__table__']=tableName
        attrs['__primary_key__']=primaryKey #主属性名
        attrs['__fields__']=fields #除主属性以外的属性名
        
        attrs['__select__'] = 'select `%s`, %s from `%s`' % (primaryKey, ', '.join(escaped_fields), tableName)
        attrs['__insert__'] = 'insert into `%s` (%s,`%s`) values (%s)'%(tableName,', '.join(escaped_fields),primaryKey,create_args_string(len(escaped_fields)+1))
        attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (tableName, ', '.join(map(lambda f: '`%s`=?' % (mappings.get(f).name or f), fields)), primaryKey)
        attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (tableName, primaryKey)
        return type.__new__(cls,name,bases,attrs)

'''
定义所有orm映射的基类Model
odel从dict继承，拥有字典的所有功能，
同时实现特殊方法__getattr__和__setattr__，
能够实现属性操作
'''
class Model(dict,metaclass=ModelMetaclass):
    
    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    # _getattr_用于查询不在__dict__系统中的属性
    # __dict__分层存储属性，每一层的__dict__只存储每一层新加的属性。子类不需要重复存储父类的属性。
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r'"Model" object has no attribute "%s" ' % key)

    def __setattr__(self, key, value):
        self[key] = value

    def getValue(self, key):
        return getattr(self, key, None)

    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                logging.debug('using default value for %s : %s ' % (key, str(value)))
                setattr(self, key, value)
        return value
    '''
    classmethod 修饰符对应的函数不需要实例化，
    不需要 self 参数，
    但第一个参数需要是表示自身类的 cls 参数，
    可以来调用类的属性，类的方法，实例化对象等。
    '''    
    @classmethod
    @asyncio.coroutine
    def find(cls,pk):
        #'find object by primary key.'
        rs=yield from select('%s where `%s`=?'%(cls.__select__,cls.__primary_key__),pk)
        if len(rs)==0:
            return None
        # 将rs[0]转换成关键字参数元组，rs[0]为dict
        return cls(**rs[0])
    
    @classmethod
    @asyncio.coroutine
    def findAll(cls,where=None,args=None,**kw):
        # find objects by where clause. 
        sql=[cls.__select__]
        if where:
            sql.append('where')
            sql.append(where)
        if args is None:
            args=[]
        orderBy=kw.get('orderBy',None)
        if orderBy:
            sql.append('order by')
            sql.append(orderBy)
        #sql中limit用于限制查询结果返回的数量，常用于分页
        #limit n 等同于 limit 0,n 
        limit = kw.get('limit',None)
        if limit is not None:
            sql.append('limit')
            if isinstance(limit,int):
                sql.append('?')
                args.append(limit)
            elif isinstance(limit,tuple) and len(limit)==2:
                sql.append('?,?')
                args.extend(limit)
            else:
                raise ValueError('Invalid limit value:%s'%str(limit))
        rs=yield from select(' '.join(sql),args)
        return [cls(**r) for r in rs]
        
    @classmethod
    @asyncio.coroutine
    def findNumber(cls,selectField,where=None,args=None):
        #select number by select and where
        # 这里的 _num_ 为别名，任何客户端都可以按照这个名称引用这个列，就像它是个实际的列一样
        sql=['select %s _num_ from `%s`'%(selectField,cls.__table__)]
        if where:
            sql.append('where')
            sql.append(where)
        rs=yield from select(' '.join(sql),args,1)
        if len(rs)==0:
            return None
        #rs[0]表示一行数据，是一个字典，而rs是一个列表
        return rs[0]['_num_']
        
    @asyncio.coroutine
    def save(self):
        args=list(map(self.getValueOrDefault,self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        rows=yield from execute(self.__insert__,args)
        if rows!=1:
            logging.warn("failed to insert record: affected rows:%s"%rows)
    
    @asyncio.coroutine
    def update(self):
        args=list(map(self.getValue,self.__fields__))
        args.append(self.getValue(self.__primary_key__))
        rows=yield from execute(self.__update__,args)
        if rows!=1:
            logging.warn("failed to insert record:affected rows:%s"%rows)
    
    @asyncio.coroutine
    def remove(self):
        args=[self.getValue(self.__primary_key__)]
        rows=yield from execute(self.__delete__,args)
        if rows!=1:
            logging.warn("failed to insert record:affected rows:%s"%rows)
'''
定义Field类，负责保存（数据库）表的字段名和字段类型
'''
class Field(object):
    # 表的字段包括名字，类型，是否为主键，默认值
    def __init__(self,name,column_type,primary_key,default):
        self.name=name
        self.column_type=column_type
        self.primary_key=primary_key
        self.default=default
        
    def __str__(self):
        return '<%s,%s:%s>'%(self.__class__.__name__,self.column_type,self.name)
    
'''
映射varchar的StringField类
'''
class StringField(Field):
    # ddl表示数据定义语言，
    def __init__(self,name=None,primary_key=False,default=None,ddl='varchar(100)'):
        super().__init__(name,ddl,primary_key,default)

class BooleanField(Field):
    def __init__(self,name=None,default=False):
        super().__init__(name,'boolean',False,default)

class IntegerField(Field):
    def __init__(self,name=None,primary_key=False,default=0):
        super().__init__(name,'bigint',primary_key,default)

class FloatField(Field):
    def __init__(self,name=None,primary_key=False,default=0.0):
        super().__init__(name,'real',primary_key,default)
        
class TextField(Field):
    def __init__(self,name=None,default=None):
        super().__init__(name,'text',False,default)
        