#coding:utf8
"""
定义网络请求方法
"""

import requests

class HTTP:
    @staticmethod
    def get(url,return_json=True):
        #return_json 判断get返回数据是否是json格式
        r = requests.get(url)
        if r.status_code != 200:
            return {} if return_json else ""
        return r.json() if return_json else r.text
        #当response返回的是json格式，用r.json打印响应内容





        # if r.status_code == 200:
        #     if return_json:
        #         return r.json()  #提取requests对象中json数据
        #     else:
        #         return r.text
        # else:
        #     if return_json:
        #         return {}
        #     else:
        #         return ""
