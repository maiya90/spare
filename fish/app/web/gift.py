
from . import web
from flask_login import login_required,current_user
# from app.models.gift import db,Gift
from flask import current_app,flash,redirect,url_for,render_template
from app.view_models.gift import MyGifts
from app.models.base import db
from app.models.gift import Gift
from app.view_models.tarde import MyTrades
from ..libs.enums import PendingStatus
from ..models.drift import Drift


@web.route('/my/gifts')
@login_required   #限制用户访问，需登录后才能访问 调用get_user方法，查询cookie中uid
def my_gifts():
    uid = current_user.id
    gifts_of_mine = Gift.get_user_gifts(uid)    #根据当前用户id获取其对应的赠送清单
    isbn_list = [wish.isbn for wish in gifts_of_mine]   #获取赠送清单中全部书籍的isbn号
    wish_count_list = Gift.get_wish_counts(isbn_list) #根据isbn号查询Wish表有哪些人想要这本书
    view_model = MyTrades(gifts_of_mine, wish_count_list)
    return render_template('my_wish.html', wishes=view_model.trades)


@web.route('/gifts/book/<isbn>')
@login_required
def save_to_gifts(isbn):
    #假如事务提交失败了，需进行回滚 rollback
    if current_user.can_save_to_list(isbn):
        # try:
        #     gift = Gift()
        #     gift.uid = current_user.id  #current_user指代当前登陆的用户 通过def get_user(uid):获取当前用户信息
        #     # current_user.beans += 0.5
        #     current_user.beans += current_app.config['BEANS_UPLOAD_ONE_BOOK']
        #     db.session.add(gift)
        #     db.session.commit()
        # except  Exception as e:
        #     db.session.rollback()  #假如commit或者前面流程报错，则进行事务回滚
        #     raise e  #抛出异常
        with db.auto_db_commit():
            gift =Gift()
            gift.isbn = isbn
            gift.uid = current_user.id
            current_user.beans += current_app.config['BEANS_UPLOAD_ONE_BOOK']
            db.session.add(gift)
    else:
        flash('这本书已添加至你的赠送清单或已存在于你的心愿清单，请不要重复添加')
    return redirect(url_for('web.book_detail', isbn=isbn))

@web.route('/gifts/<gid>/redraw')
@login_required
def redraw_from_gifts(gid):
    #撤销赠送清单
    gift = Gift.query.filter_by(id=gid,launched=False).first_or_404()
    drift = Drift.query.filter_by(gift_id=gid,pending=PendingStatus.Waiting).first()
    if drift:
        flash('该书籍处于交易状态，请先前往鱼漂处理该交易')
    else:
        with db.auto_db_commit():
            current_user.beans -= current_app.config['BEANS_UPLOAD_ONE_BOOK']
            gift.delete()
    return redirect(url_for('web.my_gifts'))