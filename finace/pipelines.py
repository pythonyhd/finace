import time

import pymongo


class FinacePipeline:
    def process_item(self, item, spider):
        item['spider_time'] = int(time.time())
        item['spider_name'] = spider.name
        btime = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        item['btime'] = btime
        city = item.get('city')
        loan_limit = item.get('loan_limit')
        loan_term = item.get('loan_term')
        org_id = item.get('org_id')
        org_name = item.get('org_name')
        item['data_tag'] = "%s|%s|%s|%s|%s|%s" % (city, loan_limit, loan_term, btime, org_id, org_name)
        return item


class MongodbIndexPipeline(object):
    """ 存储到mongodb数据库并且创建索引 """

    def __init__(self, mongo_host, mongo_port, mongo_user, mongo_pwd, mongo_db):
        self.client = pymongo.MongoClient(mongo_host, mongo_port)
        db_auth = self.client.admin
        db_auth.authenticate(mongo_user, mongo_pwd)
        self.db = self.client[mongo_db]

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_host=crawler.settings.get('MONGODB_HOST'),
            mongo_port=crawler.settings.get('MONGODB_PORT'),
            mongo_user=crawler.settings.get('MONGO_USER'),
            mongo_pwd=crawler.settings.get('MONGO_PWD'),
            mongo_db=crawler.settings.get('MONGO_DATA_BASE')
        )

    def process_item(self, item, spider):
        if spider.name == "rong360_city":
            collection = self.db[spider.name]
            collection.create_index([('url', 1), ('name', -1)])  # 1表示升序，-1降序
            name = item.get('name')
            retData = collection.find_one({'name': name})
            if retData:
                collection.update_one({"name": name}, {'$set': item}, upsert=True)
            else:
                collection.insert_one(item)
        else:
            collection = self.db[spider.name + "_new"]
            data_tag = item.get('data_tag')
            retData = collection.find_one({'data_tag': data_tag})
            if retData:
                collection.update_one({"data_tag": data_tag}, {'$set': item}, upsert=True)
            else:
                # item['_id'] = self.getSoleID(spider.name + "_new", self.db)
                collection.insert_one(item)
        return item

    def getSoleID(self, col_name, db):
        ID = db['index_rule'].find_and_modify(query={u'_id': col_name}, update={"$inc": {u'currentIdVal': 1}}, upsert=True)[
            'currentIdVal']
        return int(ID)
