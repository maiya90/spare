#coding:utf8
"""
定义判断逻辑 q是关键字还是isbn号
"""
# isbn isbn13  13个0到3的数字组成
# isbn10 10个0到9的数字组成，含有一些特殊字符"-"

def is_isbn_or_key(word):
    """
    判断传过来的word参数是关键字还是isbn号
    """
    isbn_or_key = 'key'
    if len(word) == 13 and word.isdigit():
        isbn_or_key = 'isbn'
    short_word = word.replace('-', '')
    if '-' in word and len(short_word) == 10 and short_word.isdigit():
        isbn_or_key = 'isbn'
    return isbn_or_key