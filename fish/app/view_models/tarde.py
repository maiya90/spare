#coding:utf8
"""
处理gift和wish
"""
from app.view_models.book import BookViewModel


class TradeInfo:
    def __init__(self,goods):
        self.total = 0
        self.trades = []
        self.__parse(goods)

    #处理一组数据
    def __parse(self,goods):
        self.total = len(goods)
        self.trades = [self.__map_to_trade(single) for single in goods]

    #处理单个数据
    def __map_to_trade(self,single):
        if single.create_datetime:
            time = single.create_datetime.strftime('%Y-%m-%d')
        else:
            time = '未知'
        return dict(user_name = single.user.nickname, #通过gift，wish的user属性拿到User模型的用户名字
                    time = time,
                    id = single.id)


class MyTrades:
    def __init__(self, trades_of_mine, trades_count_list):
        self.trades = []

        self.__trades_of_mine = trades_of_mine
        self.__trades_count_list = trades_count_list

        self.trades = self.__parse()


    def __parse(self):
        temp_trades = []
        for trade in self.__trades_of_mine: #trade为一个模型对象
            my_trade = self.__matching(trade)
            temp_trades.append(my_trade)
        return temp_trades

    def __matching(self, trade):
        count = 0
        for trade_count in self.__trades_count_list:
            if trade.isbn == trade_count['isbn']:
                count = trade_count['count']
        r = {
            'wishes_count': count,
            'book': BookViewModel(trade.book),
            'id': trade.id
        }
        return r
