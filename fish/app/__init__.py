#coding:utf8

from flask import Flask
from app.models.book import db
from flask_login import LoginManager
from flask_mail import Mail

login_manager = LoginManager()
mail = Mail()

def creat_app():
    app = Flask(__name__)
    app.config.from_object("app.secure")
    app.config.from_object("app.setting")
    register_blueprint(app)

    login_manager.init_app(app)
    login_manager.login_view = 'web.login'  #将login的endpoint赋值给login_view
    login_manager.login_message = '请先登陆或注册'
    # @login_manager.user_loader
    # def load_user(user_id):
    #     return None
    db.init_app(app)
    db.create_all(app=app)

    mail.init_app(app)

    return app


def register_blueprint(app):   #将蓝图注册到app实例对象中
    from app.web import web
    app.register_blueprint(web)
