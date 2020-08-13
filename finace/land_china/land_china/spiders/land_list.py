# -*- coding: utf-8 -*-
import base64
import getopt
import json
import os
import re
import subprocess
import sys
import time
import threading
from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from io import BytesIO

import requests
import scrapy
from fake_useragent import UserAgent
from retrying import retry

sys.path.append('/opt/drch_spider/spider/land_china')

from land_china import settings
from land_china.utils.filter import get_md5_value
from land_china.utils.mongodb import MongoDBUtils
from land_china.utils.utils import UtilsInfo
from land_china.settings import captcha_url


class LandlistSpider(object):
    url = 'http://www.landchina.com/default.aspx?tabid=263'
    headers = {'User-Agent': UserAgent().chrome}
    session = requests.session()
    utils = UtilsInfo()
    mongo_conn = MongoDBUtils(settings.MONGO_IP, settings.MONGO_PORT, settings.STORE_DB, settings.MONGO_USER,
                              settings.MONGO_PWD)
    match_mongo = mongo_conn.db
    base_item = {
        'site': 'landchina',
        'tag': 'landchina_list',
    }

    @retry(stop_max_attempt_number=10, wait_random_min=500, wait_random_max=10000)
    def start_requests(self, btime, page):
        verify_url, cookies = self.utils.china_land(self.url)
        proxies = self.utils.proxy()
        response = self.session.get(verify_url, headers=self.headers, proxies=proxies, timeout=65)
        image_data = re.search(r'src="data:image/bmp;base64,(.*?)"', response.text, re.S)
        if image_data:
            image_data = image_data.group(1)
            image_data = base64.b64decode(image_data)
            image_hex = self.captcha(image_data)
            captcha_url = 'https://www.landchina.com/?security_verify_img={}'.format(image_hex)
            res = self.session.get(captcha_url, headers=self.headers, proxies=proxies, timeout=65)
        self.headers['Cookies'] = cookies
        post_data = {'TAB_QueryConditionItem': '9f2c3acd-0256-4da2-a659-6949c4671a2a',
                     'TAB_QuerySortItemList': '282:False',
                     'TAB_QuerySubmitConditionData': '9f2c3acd-0256-4da2-a659-6949c4671a2a:%s~%s' % (btime, btime),
                     'TAB_QuerySubmitOrderData': '282:False',
                     'TAB_QuerySubmitPagerData': '%s' % page,  # 第几页
                     }
        response = self.session.post(self.url, data=post_data, headers=self.headers, proxies=proxies, timeout=65)
        if re.findall(r'TAB_contentTable', response.text):
            return response.text
        else:
            raise Exception('retry')

    @retry(stop_max_attempt_number=10, wait_random_min=500, wait_random_max=10000)
    def captcha(self, image_data):
        """验证码识别"""
        files = {'image_file': ('test.bmp', BytesIO(image_data), 'application')}
        response = requests.post(url=captcha_url, files=files, timeout=10)
        if response.status_code == 200:
            results = json.loads(response.text).get('value')
            image_hex = "".join([hex(ord(c)).replace('0x', '') for c in results])
            return image_hex
        else:
            raise Exception('retry')

    def get_count(self, btime, page=1):
        """获取翻页总页码"""
        html = self.start_requests(btime, page)
        selector = scrapy.Selector(text=html)
        if re.findall(r'TAB_contentTable', html):
            pages = selector.xpath('//td[@class="pager"]/text()').re_first(r'共(\d+)页')
            if pages:
                return pages
            else:
                return page
        else:
            print('页码提取失败')

    def parse_index(self, html):
        """列表页解析"""
        selector = scrapy.Selector(text=html)
        tables = selector.xpath('//table[@name="contentTable"]/tbody/tr[position()>1]')
        for land in tables:
            index = land.xpath('./td[1]/text()').get('')  # 序号
            region_first = land.xpath('./td[2]/span/@title').get('')  # 行政区
            region_second = land.xpath('string(./td[2])').get('')
            region = region_first if region_first else region_second
            located_first = land.xpath('./td[3]/a/text()').get('')  # 土地坐落
            located_second = land.xpath('./td[3]/a/span/@title').get('')
            located = located_first if located_first else located_second
            url = land.xpath('./td[3]/a/@href').get('')  # url
            url = 'https://www.landchina.com/' + url if url else ''
            acreage = land.xpath('./td[4]/text()').get('')  # 总面积
            purpose = land.xpath('./td[5]/text()').get('')  # 土地用途
            supply = land.xpath('./td[6]/text()').get('')  # 供应方式
            signing_time = land.xpath('./td[7]/text()').get('')  # 签定日期
            btime = time.strftime("%Y-%m-%d", time.localtime(int(time.time())))
            create_time = int(time.time())

            item = dict(
                index=index, region=region, located=located, acreage=acreage, purpose=purpose,
                supply=supply, signing_time=signing_time, url=url, btime=btime, create_time=create_time,
            )
            yield item

    def main(self):
        """单进程版本，测试使用"""
        start_t = time.strftime("%Y-%m-%d", time.localtime(int(time.time()) - 25 * 24 * 60 * 60))
        end_t = time.strftime("%Y-%m-%d", time.localtime(int(time.time())))
        dates = self.utils.getBetweenDay(start_t, end_t)
        dates.reverse()
        for btime in dates:
            pages = self.get_count(btime)
            for page in range(1, int(pages) + 1):
                print('抓取时间：{}>>>抓取页数：{}'.format(btime, page))
                index_html = self.start_requests(btime, page)
                first_items = self.parse_index(index_html)
                second_item = dict(page=page, stime=btime)
                for first_item in first_items:
                    item = {**first_item, **second_item, **self.base_item}
                    code = item['region'] + item['located'] + item['acreage'] + item['purpose'] + item['supply'] + item['stime']
                    item['code'] = get_md5_value(code)
                    retData = self.match_mongo[settings.STORE_TABLE].find_one({'code': item['code']})
                    if not retData:
                        self.utils.insert_mongo(self.match_mongo, settings.STORE_TABLE, item, item)

    def run(self, btime, page):
        """开启多线程加速爬取，对翻页页码开启多线程"""
        index_html = self.start_requests(btime, page)
        first_items = self.parse_index(index_html)
        second_item = dict(page=page, stime=btime)
        for first_item in first_items:
            item = {**first_item, **second_item, **self.base_item}
            code = item['region'] + item['located'] + item['acreage'] + item['purpose'] + item['supply'] + item['stime']
            item['code'] = get_md5_value(code)
            retData = self.match_mongo[settings.STORE_TABLE].find_one({'code': item['code']})
            if not retData:
                self.utils.insert_mongo(self.match_mongo, settings.STORE_TABLE, item, item)


if __name__ == '__main__':
    file_name = os.path.basename(sys.argv[0]).split(".")[0]
    opts, args = getopt.getopt(sys.argv[1:], "n:")
    num = 1
    for op, value in opts:
        if op == "-n":
            num = int(value)
    child = subprocess.Popen(['pgrep', '-f', '[python] ' + file_name + ".py"], stdout=subprocess.PIPE, shell=False)
    response = child.communicate()[0]
    pids = [int(pid) for pid in response.split()]
    if len(pids) <= num:
        spider = LandlistSpider()
        # 单进程
        # spider.main()
        # 多线程加速
        start_t = time.strftime("%Y-%m-%d", time.localtime(int(time.time()) - 25 * 24 * 60 * 60))
        end_t = time.strftime("%Y-%m-%d", time.localtime(int(time.time())))
        dates = spider.utils.getBetweenDay(start_t, end_t)
        dates.reverse()
        with ThreadPoolExecutor(max_workers=5) as executor:
            for btime in dates:
                pages = spider.get_count(btime)
                task_list = []
                for page in range(1, int(pages) + 1):
                    print('线程名称：{}--搜索时间：{}--总页数：{}--正在抓取第：{}页'.format(threading.current_thread().getName(), btime, pages, page))
                    obj = executor.submit(spider.run, btime, page)
                    task_list.append(obj)

                for future in as_completed(task_list):
                    future.result()
    else:
        print("beyond max is %s..." % num)
