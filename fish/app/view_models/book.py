#coding:utf8
"""
对原始数据进行相应的调整
"""
"""
面向对象：
1.描述特征 （类变量 实例变量）
2.行为（封装的方法）
"""
class BookViewModel:
    #处理单本书籍数据 isbn号搜索
    def __init__(self,book):
        self.title = book['title']
        self.publisher = book['publisher']
        self.pages = book['pages']
        self.author = '、'.join(book['author'])
        self.price = book['price']
        self.summary = book['summary']
        self.isbn = book['isbn']
        self.image = book['image']
        self.pubdate = book['pubdate']
        self.binding = book['binding']

    @property
    #将书籍的作者 出版社信息 价格用/连接起来
    def intro(self):
        intros = filter(lambda x:True if x else False ,[self.author,self.publisher,self.price])
        return '/'.join(intros)

class BookCollection:
    #处理书籍集合的数据 关键字搜索
    def __init__(self):
        self.total = 0
        self.books = []
        self.keyword = ''

    def fill(self,yushu_book,keyword):
        self.total = yushu_book.total
        self.keyword = keyword
        self.books = [BookViewModel(book) for book in yushu_book.books]


















class _BookViewModel:
    @classmethod
    def package_single(cls,data,keyword):
        #isbn号搜索 出现单本书
        returned = {
            'book': [],
            'total': 0,
            'keyword': keyword
        }
        if data:
            returned['total'] = 1
            returned['book'] = [cls.__cut_book_data(data)]
        return returned

    @classmethod
    def package_collection(cls,data,keyword):
        #关键字搜索 出现多本书
        returned = {
            'books' : [],
            'total' : 0,
            'keyword' : keyword
        }
        if data:
            returned['total'] = data['books']
            returned['books'] = [cls.__cut_book_data(book) for book in data['books']]
        return returned

    @classmethod
    def __cut_book_data(cls,data):
        #对原始数据进行裁剪，多余去掉
        book = {
            'title' : data['title'],
            'publisher' : data['publisher'],
            'pages' : data['pages'] or '',   #or :自左向右计算整个布尔表达式，如果有为真的值，那么立刻返回第一个为真的值，如果整个表达式为假，则返回最后一个为假的值
            'author' : '、'.join(data['author']),
            'price' : data['price'],
            'summary' : data['summary'] or '',
            'image' : data['image']
        }
        return book

