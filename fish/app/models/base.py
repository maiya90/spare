#coding:utf8
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy,BaseQuery
from sqlalchemy import Column,Integer,SmallInteger
from contextlib import contextmanager

class SQLAlchemy(_SQLAlchemy): #定义一个子类，继承_SQLAlchemy
    #每次提交失败后，可进行事务回滚
    @contextmanager
    def auto_db_commit(self):
        try:
            yield
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
class Query(BaseQuery):
    def filter_by(self, **kwargs):
        if 'status' not in kwargs.keys():
            kwargs['status'] = 1
        return super(Query, self).filter_by(**kwargs)

db = SQLAlchemy(query_class=Query)

class Base(db.Model):
    __abstract__ = True
    create_time = Column('create_time',Integer) #类变量，假如设置default 则会每个对象的时间戳都一样
    status = Column(SmallInteger,default=1)  #软删除，数据实际没有从数据库删除，让status为0代表数据被删除了

    def __init__(self):  #每实例化一个模型对象，就会自动生成时间戳
        self.create_time = int(datetime.now().timestamp())

    @property
    def create_datetime(self):
        if self.create_time:
            return datetime.fromtimestamp(self.create_time) #时间戳转换成字符串日期时间
        else:
            return None


    def set_attrs(self,attrs_dict):
        #遍历attrs_dict字典
        #假如字典中的key有和模型类(数据库表)属性相同的，则把value赋值给模型类属性
        for key,value in attrs_dict.items():
            if hasattr(self,key) and key != 'id':   #判断self对象是否含有key属性
                setattr(self,key,value) #对self对象中的key属性赋予value值


    def delete(self):
        self.status = 0