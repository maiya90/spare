#coding:utf8

"""
从API获取数据
"""
from app.libs.httper import HTTP
from flask import current_app
"""
面向对象：
描述特征（类变量，实例变量）
行为 （方法）

"""
class YuShuBook:
    isbn_url = 'http://t.yushu.im/v2/book/isbn/{}'
    keyword_url = 'http://t.yushu.im/v2/book/search?q={}&count={}&start{}'

    def __init__(self):
        self.books = []
        self.total = 0

    def search_by_isbn(self,isbn):
        url = self.isbn_url.format(isbn)
        result = HTTP.get(url)     #get方法请求到数据为json，而后python会将其转为字典{}
        self.__fill_single(result)

    def __fill_single(self,data):
        #isbn号 单本书籍
        if data:
            self.total = 1
            self.books.append(data)

    def __fill_collection(self,data):
        #关键字搜索 多本书籍
        if data:
            self.total = data['total']
            self.books = data['books']

    def search_by_keyword(self,keyword,page=1):  #每次提取15个。从0开始
        url = self.keyword_url.format(keyword,current_app.config['PER_PAGE'],self.calculate_start(page))
        result = HTTP.get(url)
        self.__fill_collection(result)

    def calculate_start(self,page):
        return (page-1) * current_app.config['PER_PAGE']

    @property
    def first(self):
        #提取books里第一个元素
        return self.books[0] if self.total >= 1 else None

