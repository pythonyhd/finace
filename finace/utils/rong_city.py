# -*- coding: utf-8 -*-
from pymongo import MongoClient

from finace import settings


class SpiderCity(object):
    """获取所有城市列表"""

    def __init__(self, ip=settings.MONGODB_HOST, port=settings.MONGODB_PORT, db_name=settings.MONGO_DATA_BASE,
                 user=settings.MONGO_USER, password=settings.MONGO_PWD):
        self.db_name = db_name
        self.connection = MongoClient(ip, port)
        db_auth = self.connection.admin
        db_auth.authenticate(user, password)
        self.db = self.connection[db_name]
        self.table = self.db[settings.MONGO_CITY]

    def find(self, *args):
        """
        指定查找，默认是pymongo.cursor.Cursor，需要遍历获取单条
        :param args: 字典
        :return:mongo的cursor对象
        """
        return self.table.find(*args)

    def find_all(self):
        """
        返回所有，默认是pymongo.cursor.Cursor，需要遍历获取单条
        :return: mongo的cursor对象
        """
        return self.table.find({})

    def count(self):
        """
        返回数据总量
        :return:
        """
        return self.table.find({}).count()

    def get(self):
        start_urls = []
        datas = self.find_all()
        for data in datas:
            url = data.get('url')
            name = data.get('name')
            item = dict(name=name, url=url)
            start_urls.append(item)
        return start_urls


if __name__ == '__main__':
    spider = SpiderCity()
    url_list = spider.get()
    print(url_list)