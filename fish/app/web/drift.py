from . import web
from app.forms.book import DriftForm
from app.libs.email import send_mail
from app.libs.enums import PendingStatus
from app.models.base import db
from app.models.drift import Drift
from app.models.gift import Gift
from app.models.user import User
from app.models.wish import Wish

from . import web
from flask_login import login_required, current_user
from flask import flash, redirect, url_for, render_template, request, current_app
from sqlalchemy import desc, or_

from ..view_models.drift import DriftCollection


@web.route('/drift/<int:gid>', methods=['GET', 'POST'])
@login_required
def send_drift(gid):
    current_gift = Gift.query.get_or_404(gid)

    if current_gift.is_yourself_gift(current_user.id):
        flash('这本书属于你自己的, 不能向自己索要书籍')
        return redirect(url_for('web.book_detail', isbn=current_gift.isbn))

    can = current_user.can_send_drift()
    if not can:
        return render_template('not_enough_beans.html', beans=current_user.beans)

    form = DriftForm(request.form)
    if request.method == 'POST' and form.validate():
        save_drift(form, current_gift)
        # send_mail()
        send_mail(current_gift.user.email, '有人想要一本书', 'email/get_gift.html',
                  wisher=current_user,
                  gift=current_gift)
        return redirect(url_for('web.pending'))

    gifter = current_gift.user.Summary
    return render_template('drift.html',gifter=gifter, user_beans=current_user.beans, form=form)


@web.route('/pending')
@login_required
def pending():
    #检索所有的交易记录 对drift模型进行查询
    drifts = Drift.query.filter(
        or_(Drift.requester_id == current_user.id,
            Drift.gifter_id == current_user.id)) \
        .order_by(desc(Drift.create_time)).all()
    #print(drifts)
    views = DriftCollection(drifts,current_user.id)
    return render_template('pending.html',drifts=views.data)

@web.route('/drift/<int:did>/reject')
@login_required
def reject_drift(did):
    # 拒绝请求 为书籍赠送者操作
    with db.auto_db_commit():
        drift = Drift.query.filter_by(gifter_id=current_user.id,id=did).first_or_404()
        drift.pending = PendingStatus.Reject
        requester = User.query.get_or_404(drift.requester_id)
        requester.beans += 1
    return redirect(url_for('web.pending'))


@web.route('/drift/<int:did>/redraw')
@login_required
def redraw_drift(did):
    #撤销请求 为书籍索要者操作
    #注意超权现象 用户登陆后修改传过来的did 来操作别人的数据
    #解决：判断当前用户身份和did归属性
    with db.auto_db_commit():
        drift = Drift.query.filter_by(requester_id=current_user.id,id=did).first_or_404()
        drift.pending = PendingStatus.Redraw
        current_user.beans += 1
    return redirect(url_for('web.pending'))



@web.route('/drift/<int:did>/mailed')
@login_required
def mailed_drift(did):
    with db.auto_db_commit():
        drift = Drift.query.filter_by(gifter_id=current_user.id,id=did).first_or_404()
        drift.pending = PendingStatus.Success
        current_user.beans += 1

        gift = Gift.query.filter_by(id=drift.gift_id).first_or_404()
        gift.launched = True

        wish = Wish.query.filter_by(isbn=drift.isbn,uid=drift.requester_id,launched=False).first_or_404()
        wish.launched = True
    return redirect(url_for('web.pending'))

#将书籍和邮寄相关信息存储到drift数据库
def save_drift(drift_form, current_gift):
    with db.auto_db_commit():
        drift = Drift()
        # drift.message = drift_form.message.data
        drift_form.populate_obj(drift)

        #保存请求者 赠送者信息到数据库
        drift.gift_id = current_gift.id
        drift.requester_id = current_user.id
        drift.requester_nickname = current_user.nickname
        drift.gifter_nickname = current_gift.user.nickname
        drift.gifter_id = current_gift.user.id

        #保存书籍信息到数据库
        book = current_gift.book
        drift.book_title = book['title']
        drift.book_author = book['author']
        drift.book_img = book['image']
        drift.isbn = book['isbn']

        current_user.beans -= 1

        db.session.add(drift)