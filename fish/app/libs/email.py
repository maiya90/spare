#coding:utf8

"""
发送电子邮件
"""

from app import mail
from flask_mail import Message
from flask import current_app,render_template
from threading import Thread

# def send_email(to, subject, template, **kwargs):
#     #两种发送邮件方法：python提供的发送email接口
#     #               flask框架提供的插件 flask-mail
#     # msg = Message('测试邮件',sender='1421841934@qq.com',body='Test',recipients=['1421841934@qq.com'])
#     # mail.send(msg)
#     msg = Message('[余书]' + ' ' + subject,
#                   sender=current_app.config['MAIL_USERNAME'],
#                   recipients=[to])
#     msg.html = render_template(template, **kwargs)

def send_async_mail(app,msg):
    #将app核心对象推入localstack栈中
    with app.app_context():
        #开启多线程发送邮件 视图函数不必等待邮件发送后再执行下一步
        try:
            mail.send(msg)
        except Exception as e:
            pass


def send_mail(to, subject, template, **kwargs):
    # Python email
    # msg = Message('测试邮件', sender='aaa@qq.com', body='Test',
    #               recipients=['user@qq.com'])
    msg = Message('[鱼书]' + ' ' + subject,
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=[to])
    msg.html = render_template(template, **kwargs)
    app =current_app._get_current_object()  #获取app核心对象 因为开启了新线程
    t = Thread(target=send_async_mail,args=[app,msg])
    t.start()