#coding:utf8
from app.libs.enums import PendingStatus
from math import floor
from sqlalchemy import String,Integer,Column,Boolean,Float
from flask import current_app
from app.libs.helpers import is_isbn_or_key
from app.models.drift import Drift
from app.models.gift import Gift
from app.models.wish import Wish
from app.spider.yushu_book import YuShuBook
from app.models.base import db,Base
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from app import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


#Base 基类模型 UserMixin：内部封装了get_id等方法，获取用户id并在login_user中写进cookie作为身份依属
class User(UserMixin,Base):
    id = Column(Integer,primary_key=True)
    nickname = Column(String(24),nullable=False)
    phone_number = Column(String(18),unique=True)
    _password = Column('password',String(128),nullable=False)
    email = Column(String(50),unique=True,nullable=False)
    confirmed = Column(Boolean, default=False)
    beans = Column(Float, default=0)
    send_counter = Column(Integer, default=0)
    receive_counter = Column(Integer, default=0)
    wx_open_id = Column(String(50))
    wx_name = Column(String(32))



#对传过来的密码进行加密   base模型里的动态赋值password不会写入数据库
    @property    #读取加密后的密码
    def password(self):
        return self._password

    @password.setter
    def password(self,raw):  #raw：原始密码
        self._password = generate_password_hash(raw)    #将加密后的password赋值给_password写入数据库

    def check_password(self,raw):
        return check_password_hash(self._password,raw) #加密后的密码与原始密码比对 相同为True

    #判断鱼豆是否足够
    def can_send_drift(self):
        if self.beans < 1:
            return False
        #获取该用户已经赠送出去书籍的数量
        success_gifts_count = Gift.query.filter_by(uid=self.id,
                                                   launched=True).count()
        success_receive_count = Drift.query.filter_by(requester_id=self.id,
                                                      pending=PendingStatus.Success).count()
        #索取两本书后必须要赠送一本才能继续索取
        return True if \
            floor(success_gifts_count / 2) >= floor(success_receive_count) \
            else False

    def can_save_to_list(self, isbn):
        if is_isbn_or_key(isbn) != 'isbn':  #判断isbn格式是否正确
            return False
        yushu_book = YuShuBook()
        yushu_book.search_by_isbn(isbn)  #判断该isbn号对应是否有书籍
        if not yushu_book.first:
            return False
        #不允许一个用户同时赠送和想要多本相同的书
        #一个用户不可能同时成为赠送者和索要者
        #不在赠送清单和也不在心愿清单才能添加
        gifting = Gift.query.filter_by(uid=self.id, isbn=isbn,launched=False).first()
        wishing = Wish.query.filter_by(uid=self.id, isbn=isbn,launched=False).first()
        if not gifting and not wishing:
            return True
        else:
            return False

    #生成token 其中携带用户id
    def generate_token(self, expiration=600):
        #将序列化器Seriailzer进行实例化 第一个参数为无规则常量
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token,new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))  #判断data的token 可能token为伪造的
        except:
            return False
        uid = data.get('id')
        with db.auto_db_commit():
            user = User.query.get(uid)
            user.password = new_password
        return True

    @property
    def Summary(self):
        return dict(
            nickname = self.nickname,
            beans = self.beans,
            email = self.email,
            send_receive = str(self.send_counter) + '/' +str(self.receive_counter)
        )


@login_manager.user_loader   #装饰器让login_required调用实现权限控制
    #接收字符串表示的唯一用户标识符,如果能找到该用户,则返回该用户对象 否则返回None
def get_user(uid):  #从会话中存储的用户 ID 重新加载用户对象
    return User.query.get(int(uid))