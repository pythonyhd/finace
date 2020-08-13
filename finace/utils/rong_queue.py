# -*- coding: utf-8 -*-
import sys
import msgpack

sys.path.append("/opt/drch_spider/spider/finace")
from finace.utils.redis_db import RedisClient
from finace.utils.rong_city import SpiderCity


class RongSpider(object):
    redis_client = RedisClient().redis_client()
    city = SpiderCity()
    name = 'rong360_list'

    def rong_queue(self):
        """数据入到redis队列"""
        items = spider.city.get()
        loan_limits = ['0.3', '1.0', '3.0', '5.0', '10.0', '20.0', '50.0', '100.0']
        loan_terms = ['3', '6', '12', '24', '36', '60', '120']
        for loan_limit in loan_limits:
            for loan_term in loan_terms:
                for city_item in items:
                    city = city_item.get("url")
                    city_name = city_item.get('name')
                    url = "https://www.rong360.com/{}/search.html?loan_limit={}&loan_term={}&application_type=9".format(city, loan_limit, loan_term)
                    item = dict(city=city, city_name=city_name, loan_limit=loan_limit, loan_term=loan_term, url=url)
                    item = msgpack.packb(item, use_bin_type=True)
                    self.redis_client.lpush(self.name, item)

    def get_queue(self):
        """从队列获取数据"""
        # brpop命令会阻塞队列，等待新的任务进来，rpop直接取值，队列空了直接退出
        data = self.redis_client.brpop(self.name)
        if data:
            items = msgpack.unpackb(data)
            print(items)


if __name__ == '__main__':
    spider = RongSpider()
    spider.rong_queue()  # 添加到队列
    # spider.get_queue()