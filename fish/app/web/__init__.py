#coding:utf8

from flask import Blueprint,render_template

web = Blueprint("web",__name__)  ##两个参数 第一个为蓝图名称，第二个表示蓝图所在模块

@web.app_errorhandler(404)
#监控web蓝图下返回404的异常
def Not_found(e):  #e包含了异常信息
    return render_template('404.html'),404

from app.web import book
from app.web import auth
from app.web import drift
from app.web import gift
from app.web import main
from app.web import wish