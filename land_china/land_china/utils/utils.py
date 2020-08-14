# -*- coding: utf-8 -*-
import datetime
import json
import time

import redis

from land_china import settings


class UtilsInfo(object):
    def __init__(self):
        self.redisdb = redis.Redis(host='%s' % settings.REDIS_HOST, port='%s' % settings.REDIS_PORT,
                                   password=settings.REDIS_PWD, db=settings.REDIS_DB)

    def queue_brpop(self, redis_key):
        """
            redis_key  redis对应的队列名称
            供详情页使用，获取详情页url
        """
        redis_batch_size = self.redisdb.llen(redis_key)
        if redis_batch_size:
            return self.redisdb.rpop(redis_key)

    def proxy(self):
        # 获取代理IP
        proxies_name = settings.PROXIES_NAME
        ip = self.redisdb.srandmember(proxies_name)
        if ip:
            proxy_dict = {
                "http": "http://%s" % ip.decode('utf-8'),
                "https": "https://%s" % ip.decode('utf-8'),
            }
            return proxy_dict
        else:
            time.sleep(3)
            print('代理池枯竭，等待重新拨号')
            return None

    def stringToHex(self, s):
        val = ""
        for k in s:
            if (val == ""):
                val = str(hex(ord(k)))
            else:
                val += str(hex(ord(k)))
        return val.replace("0x", "")

    def china_land(self, url):
        screendate = "1920,1080"  # 屏幕宽度和高度我们可以设置成固定值．
        cookie = "srcurl=" + self.stringToHex(url) + ";path=/;"
        url = url + "&security_verify_data=" + self.stringToHex(screendate)
        return url, cookie

    def insert_mongo(self, match_mongodb, collection_name, data, redis_data=None):
        """
            match_mongodb mongo 连接
            collection_name mongo 集合名称
            redis_data 插入redis
        """
        stmt = match_mongodb[collection_name]
        url = data['url']
        retData = stmt.find_one({'url': url})
        if retData:
            stmt.update({"url": data['url']}, data)
        else:
            data['_id'] = self.getSoleID(collection_name, match_mongodb)
            stmt.insert(data)

        if redis_data:
            """列表页数据插入redis 队列"""
            redis_url = redis_data["url"] + "&_gyspider=" + json.dumps(redis_data, ensure_ascii=False)
            redis_k = "%s_queue" % data['tag']
            self.redisdb.lpush(redis_k, redis_url)

    def getSoleID(self, col_name, db):
        ID = db['index_rule'].find_and_modify(query={u'_id': col_name}, \
                                              update={"$inc": {u'currentIdVal': 1}}, upsert=True)['currentIdVal']
        return int(ID)

    def getBetweenDay(self, start_t, end_t):
        # 已今天为准，向前推25天，因为前一段时间的数据有的时候也会出现新加的情况
        date_list = []
        begin_date = datetime.datetime.strptime(start_t, "%Y-%m-%d")
        end_t = datetime.datetime.strptime(end_t, "%Y-%m-%d")
        while begin_date <= end_t:
            date_str = begin_date.strftime("%Y-%m-%d")
            date_list.append(date_str)
            begin_date += datetime.timedelta(days=1)
        return date_list


if __name__ == '__main__':
    spider = UtilsInfo()
    url = "https://www.landchina.com/default.aspx?tabid=263"
    cookie = spider.china_land(url)
    print(cookie)
