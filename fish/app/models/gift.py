from flask import current_app

from app.models.base import db,Base
from sqlalchemy import Column,Integer,String,Boolean,ForeignKey,desc,func
from sqlalchemy.orm import relationship

from app.spider.yushu_book import YuShuBook
from collections import namedtuple

"""
用来创建user和book的对应关系
保存赠送清单的信息
"""
EachGiftWishCount = namedtuple('EachGiftWishCount',['count','isbn'])

class Gift(Base):
    id = Column(Integer,primary_key=True)
    user = relationship('User')   #Gift模型与User模型进行关联
    uid = Column(Integer,ForeignKey('user.id'))
    isbn = Column(String(15),nullable=False)  ##Gift模型与Book 模型进行关联
    # 是否已经赠送出去
    launched = Column(Boolean,default=False)

    #不能在Gift模型中直接返回BookViewModel，因为模型只负责处理原始数据，
    # 所有的处理ViewModel都应该放到视图函数里面进行。
    @property
    def book(self):
        yushu_book = YuShuBook()
        yushu_book.search_by_isbn(self.isbn)
        return yushu_book.first

    @classmethod
    def get_user_gifts(cls,uid):
        gifts = Gift.query.filter_by(uid=uid,launched=False).order_by(
            desc(Gift.create_time)).all()
        return gifts

    @classmethod
    def get_wish_counts(cls,isbn_list):
        from app.models.wish import Wish
        #根据传入的isbn列表，到Wish表中并计算出每个礼物的心愿数量(多少人想要)
        #mysql in
        #db.session,query 全局搜索，即跨表查询
        #查询结果count_list格式：[(wish的数量,isbn1),(wish的数量,isbn2),...]
        count_list = db.session.query(func.count(Wish.id), Wish.isbn).filter(
            Wish.launched == False,
            Wish.isbn.in_(isbn_list),
            Wish.status == 1).group_by(
            Wish.isbn).all()

        count_list = [{'count': w[0], 'isbn': w[1]} for w in count_list]
        return count_list
        # 不要将tuple返回到外部，应该返回有意义的字典或者对象


    #对象表示一个礼物，具体
    #类对象表示礼物这个总提事务，不是一个，包含多对象的礼物
    @classmethod
    def recent(cls):
        #对最近礼物进行筛选
        #链式调用： query主体函数 +子函数 + all()触发调用
        recent_gift = Gift.query.filter_by(
            launched=False).group_by(
            Gift.isbn).order_by(
            desc(Gift.create_time)).limit(
            current_app.config['RECENT_BOOK_COUNT']).distinct().all()
        return recent_gift

    #鱼漂页面判断该书籍是否是自己赠送的
    #自己不能向自己索要书籍
    def is_yourself_gift(self,uid):
        return True if self.uid == uid else False







