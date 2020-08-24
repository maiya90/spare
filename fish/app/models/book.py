#coding:utf8
from sqlalchemy import String,Integer,Column
from app.models.base import db,Base



class Book(Base):
    id = Column(Integer,primary_key=True,autoincrement=True)
    title = Column(String(50),nullable=False)
    author = Column(String(30),default="未名")
    binding = Column(String(20))
    publisher = Column(String(50))
    price = Column(String(20))
    page = Column(Integer)
    pubdate = Column(String(20))
    isbn = Column(String(15),nullable=False,unique=True)
    summary = Column(String(1000))
    image = Column(String(50))