from flask import render_template,request,redirect,url_for,flash
from . import web
from app.models.user import User,db
from app.models import base
#from app.models import db
from app.forms.auth import RegisterForm, LoginForm, EmailForm, ResetPasswordForm,ChangePasswordForm
from flask_login import login_user,logout_user,current_user
from app.libs.email import send_mail

@web.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        # user = User() #将数据库表模型Use实例化
        # user.set_attrs(form.data)  #调用model基类模型Base方法 form.data包含客户端提交来的参数
        # db.session.add(user)
        # db.session.commit()
        with db.auto_db_commit():
            user = User()
            user.set_attrs(form.data)
            db.session.add(user)
        return redirect(url_for('web.login'))

        #user.nickname = form.nickname.data
        #user.email = form.email.data
    return render_template('auth/register.html',form=form)

@web.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(email=form.email.data).first() #通过用户的邮箱把用户全部信息取出
        if user and user.check_password(form.password.data): #判断用户是否存在于数据库和检查密码是否相同
            login_user(user)  #login_user会将用户user里的id号封装在cookie中 (主要内容是将用户信息放入session中,并为该session生成标识符)
            #login_user(user,remember=True)  cookie保留365天，可实现免登录功能
            next = request.args.get('next')
            if not next or not next.startswith('/'):
                next = url_for('web.index')
            return redirect(next)
        else:
            flash('账户不存在或密码错误')
    return render_template('auth/login.html',form=form)

@web.route('/reset/password', methods=['GET', 'POST'])
def forget_password_request():
    form = EmailForm(request.form)
    if request.method == 'POST':
        if form.validate():
            account_email = form.email.data
            user = User.query.filter_by(email=account_email).first_or_404()
            send_mail(form.email.data, '重置你的密码',
                      'email/reset_password.html', user=user,
                      token=user.generate_token())
            flash('一封邮件已发送到邮箱' + account_email + '，请及时查收')
            # return redirect(url_for('web.login'))
    return render_template('auth/forget_password_request.html', form=form)
            # first_or_404：假如该email不存在于数据库，程序抛出HtppException异常
            # first():假如该email不存在于数据库,user被赋予空值，程序继续执行

@web.route('/reset/password/<token>', methods=['GET', 'POST'])
def forget_password(token):
    form = ResetPasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        success = User.reset_password(token,form.password1.data)
        if success:
            flash('你的密码已更新,请使用新密码登录')
            return redirect(url_for('web.login'))
        else:
            flash('密码重置失败')
    return render_template('auth/forget_password.html', form=form)



@web.route('/change/password', methods=['GET', 'POST'])
def change_password():
    form = ChangePasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        with db.auto_db_commit():
            current_user.password = form.new_password1.data
        flash('密码已更新成功')
        return redirect(url_for('web.personal_center'))
    return render_template('auth/change_password.html', form=form)


@web.route('/logout')
def logout():
    logout_user()  #将浏览器cookie清空，实现注销用户
    return redirect(url_for('web.index'))


