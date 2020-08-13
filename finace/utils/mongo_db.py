# -*- coding: utf-8 -*-
import pymongo


class MongoClient(object):
    def __init__(self, host, port, user, password, db_name, table):
        client = pymongo.MongoClient(host=host, port=port)
        db_auth = client.admin
        db_auth.authenticate(user, password)
        db = client[db_name]
        self.table = db[table]

    def count(self):
        """
        返回数据总量
        :return: 数据总条数
        """
        return self.table.find({}).count()

    def read(self, page, limit):
        """
        分页读取MongoDB数据
        :param page: 页码
        :param limit: 限制
        :return: mongo对象
        """
        return self.table.find().skip(page * limit).limit(limit)
