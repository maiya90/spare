#coding:utf8
"""
视图函数search
"""

from app.libs.helpers import is_isbn_or_key
from app.spider.yushu_book import YuShuBook
from flask import jsonify,request,render_template,flash
from . import web   #从当前同级目录中导入蓝图web
from app.forms.book import SearchForm
from app.view_models.book import BookViewModel
from app.view_models.book import BookCollection
import json
from app.models.gift import Gift
from app.models.wish import Wish
from flask_login import current_user

from ..view_models.tarde import TradeInfo


@web.route('/book/search')
def search():
    """
    q:普通关键字， isbn (搜索类别)
    page：分页使用，默认为1
    """
    # q = request.args['q']
    # page = request.args['page']
    form = SearchForm(request.args)
    books = BookCollection()
    if form.validate():
        q = form.q.data.strip() #去掉前后空格
        page = form.page.data #从form中取值，避免没有传page值为空 wtf验证参数设置默认值为1
        isbn_or_key = is_isbn_or_key(q)
        yushu_book = YuShuBook()

        if isbn_or_key == 'isbn':
            yushu_book.search_by_isbn(q)
        else:
            yushu_book.search_by_keyword(q,page)

        books.fill(yushu_book,q)
        #return jsonify(books.__dict__)
        # #books为一个对象，jsonify不能序列化一个对象，调用__dict__转成字典格式
        ##假如books内嵌的一个类实例对象中又内嵌一个类实例对象，调用一次__dict__不能解决问题
        #return json.dumps(books,default=lambda o: o.__dict__)  #将处理后的dict数据转化成json数据
    else:
        flash('搜索的关键字不符合要求，请重新输入关键字')
    return render_template('search_result.html',books = books)

@web.route('/book/<isbn>/detail')
def book_detail(isbn):
    has_in_gifts = False
    has_in_wishes = False

    #取书籍详情数据展示
    yushu_book = YuShuBook()
    yushu_book.search_by_isbn(isbn)
    book = BookViewModel(yushu_book.first)

    #取赠送者信息和索要者信息
    if current_user.is_authenticated:
        # 如果未登录，current_user将是一个匿名用户对象
        if Gift.query.filter_by(uid=current_user.id, isbn=isbn,
                                launched=False).first():
            has_in_gifts = True
        if Wish.query.filter_by(uid=current_user.id, isbn=isbn,
                                launched=False).first():
            has_in_wishes = True

    book = BookViewModel(yushu_book.first)

    # if has_in_gifts:
    # 取赠送者信息和索要者信息
    trade_wishes = Wish.query.filter_by(isbn=isbn, launched=False).all()
    trade_gifts = Gift.query.filter_by(isbn=isbn, launched=False).all()
    trade_wishes_model = TradeInfo(trade_wishes)
    trade_gifts_model = TradeInfo(trade_gifts)
    return render_template('book_detail.html', book=book, has_in_gifts=has_in_gifts,
                           has_in_wishes=has_in_wishes,
                           wishes=trade_wishes_model,
                           gifts=trade_gifts_model)

    #return render_template("book_detail.html",book=book,wishes=[],gifts=[])





# @web.route('/test')
# def test():
#     r={'age': 18,
#        'name': 'nnnn'
#
#     }
#     flash('hello my')
#     return render_template('test.html',data = r)