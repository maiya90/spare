#coding:utf8

from wtforms import Form,StringField,IntegerField,PasswordField,ValidationError
from wtforms.validators import Length,NumberRange,DataRequired,Email,EqualTo
import email_validator
from app.models.user import User

class RegisterForm(Form):
    email =StringField(validators=[DataRequired(),Length(8,64),
                                   Email(message='电子邮件不符合规范')])
    nickname = StringField(validators=[
        DataRequired(), Length(2, 10, message='昵称至少需要两个字符，最多10个字符')])

    password = PasswordField(validators=[DataRequired(message='密码不可以为空，请输入密码'),
                            Length(6, 32)])

    def validate_email(self,field):   #filed为wtforms根据validate_email传入的前端发来的email对象
        if User.query.filter_by(email=field.data).first():  #first取匹配到的第一条数据
            raise ValidationError('该电子邮箱已被注册')

    def validate_nickname(self,field): #判断昵称是否已经存在于数据库
        if User.query.filter_by(nickname=field.data).first():
            raise ValidationError('该昵称已存在')

class LoginForm(Form):
    email =StringField(validators=[DataRequired(),Length(8,64),
                                   Email(message='电子邮件不符合规范')])
    password = PasswordField(validators=[DataRequired(message='密码不可以为空，请输入密码'),
                            Length(6, 32)])

class EmailForm(Form):
    #忘记密码时对用户邮箱进行格式校验
    email = StringField(validators=[DataRequired(), Length(8, 64),
                                    Email(message='电子邮件不符合规范')])


class ResetPasswordForm(Form):
    #对用户输入的新密码进行格式校验
    password1 = PasswordField(validators=[
        DataRequired(),
        Length(6, 32, message='密码长度至少需要在6到32个字符之间'),
        EqualTo('password2', message='两次输入的密码不相同')])
    #对确认密码进行格式校验
    password2 = PasswordField(validators=[
        DataRequired(), Length(6, 32)])

class ChangePasswordForm(Form):
    old_password = PasswordField(validators=[DataRequired()])
    new_password1 = PasswordField(validators=[
        DataRequired(), Length(6, 32, message='密码长度至少需要在6到32个字符之间'),
        EqualTo('new_password2', message='两次输入的密码不一致')])
    new_password2 = PasswordField(validators=[DataRequired()])