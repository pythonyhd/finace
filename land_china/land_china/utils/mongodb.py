# -*- coding: utf-8 -*-
from pymongo import MongoClient


class MongoDBUtils(object):
    """ 连接 MongoDB"""

    def __init__(self, ip, port=27017, db_name="", user="", password=""):
        self.db_name = db_name
        self.connection = MongoClient(ip, port)
        db_auth = self.connection.admin
        db_auth.authenticate(user, password)
        self.db = self.connection[db_name]