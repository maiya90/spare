from app.models.base import db,Base
from sqlalchemy import Column,Integer,String,Boolean,ForeignKey,desc,func
from sqlalchemy.orm import relationship
from app.spider.yushu_book import YuShuBook


class Wish(Base):
    id = Column(Integer,primary_key=True)
    user = relationship('User')  #Gift模型与User模型进行关联
    uid = Column(Integer,ForeignKey('user.id'))
    isbn = Column(String(15),nullable=False) ##Gift模型与Book 模型进行关联
    launched = Column(Boolean,default=False)

    @property
    def book(self):
        yushu_book = YuShuBook()
        yushu_book.search_by_isbn(self.isbn)
        return yushu_book.first

    @classmethod
    def get_user_wishes(cls,uid):
        wishes = Wish.query.filter_by(uid=uid,launched=False).order_by(
            desc(Wish.create_time)).all()
        return wishes

    @classmethod
    def get_gift_counts(cls,isbn_list):
        from app.models.gift import Gift
        #根据传入的isbn列表，到Wish表中并计算出每个礼物的心愿数量(多少人想要)
        #mysql in
        #db.session,query 全局搜索，即跨表查询
        #查询结果count_list格式：[(wish的数量,isbn1),(wish的数量,isbn2),...]
        count_list = db.session.query(func.count(Gift.id), Gift.isbn).filter(Gift.launched == False,
                                                                             Gift.isbn.in_(isbn_list),
                                                                             Gift.status == 1).group_by(Gift.isbn).all()

        # 不要将tuple返回到外部，应该返回有意义的字典或者对象
        count_list = [{'count': w[0], 'isbn': w[1]} for w in count_list]
        return count_list


