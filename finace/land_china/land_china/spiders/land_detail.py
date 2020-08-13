# -*- coding: utf-8 -*-
import base64
import getopt
import json
import os
import re
import subprocess
import sys
import time
from io import BytesIO

import requests
import scrapy
from retrying import retry

sys.path.append('/opt/drch_spider/spider/land_china')

from land_china import settings
from land_china.settings import captcha_url, DETAIL_TABLE
from land_china.spiders.exprs import xpath_list
from land_china.utils.filter import get_md5_value
from land_china.utils.mongodb import MongoDBUtils
from land_china.utils.utils import UtilsInfo


class LandDetailSpider(object):
    """中国土地市场网，详情页抓取"""
    url = 'http://www.landchina.com/'
    utils = UtilsInfo()
    mongo_conn = MongoDBUtils(settings.MONGO_IP, settings.MONGO_PORT, settings.STORE_DB, settings.MONGO_USER,
                              settings.MONGO_PWD)
    match_mongo = mongo_conn.db
    session = requests.session()
    headers = {
        "Host": "www.landchina.com",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0",
        "Accept": "text/css,*/*;q=0.1",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }

    @retry(stop_max_attempt_number=10, wait_random_min=500, wait_random_max=10000)
    def start_request(self, url):
        """
            从redis队列里面获取url，url不是永久链接，时间太久会失效
            直接请求详情页，也会出现验证码
        """
        verify_url, cookies = self.utils.china_land(self.url)
        proxies = self.utils.proxy()
        response = self.session.get(url, headers=self.headers, proxies=proxies, timeout=20)
        image_data = re.search(r'src="data:image/bmp;base64,(.*?)"', response.text, re.S)
        if image_data:
            image_data = image_data.group(1)
            image_data = base64.b64decode(image_data)
            image_hex = self.captcha(image_data)
            captcha_url = 'https://www.landchina.com/?security_verify_img={}'.format(image_hex)
            res = self.session.get(captcha_url, headers=self.headers, proxies=proxies, timeout=20)
        self.headers['Cookies'] = cookies
        response = self.session.get(url, headers=self.headers, proxies=proxies, timeout=20)
        response.encoding = 'GBK'
        if "电子监管号" in response.text:
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

    def parse(self, html, list_data, url):
        """
            list_data 列表页抓取的数据字典
            html 详情页HTML
        """
        selector = scrapy.Selector(text=html)
        item = dict()
        item['site'] = list_data.get('site')
        item['url'] = url
        # 详情页解析
        # -------------------解析分期支付约定-----------------------------
        fqzf = {"payment_issue": '支付期号', 'agreed_payment_date': "约定支付日期", 'agreed_payment_money': "约定支付金额(万元)",
                'desc': "备注"}
        fqzf_reult = []
        fqzfyd = selector.xpath("//div[@id='p1']//td/span[contains(text(),'分期支付约定:')]/parent::td/following-sibling::td[1]/table/tbody/tr[not(@class)]")
        if len(fqzfyd) <= 2:
            fqzf_reult.append({"payment_issue": '', 'agreed_payment_date': "", 'agreed_payment_money': "", 'desc': ""})
        else:
            for i in range(len(fqzfyd) - 2):
                result_f = {}
                for k, v in fqzf.items():
                    result_f[k] = ""
                    cid = selector.xpath("//div[@id='p1']//td/span[contains(text(),'%s')]/@id" % v).extract()
                    if cid:
                        cid = cid[0]
                        vid = cid.replace("_r1_", "_r2_").replace("_ctrl", "_%s_ctrl" % i)
                        result_f[k] = "".join(selector.xpath("//span[@id='%s']/text()" % vid).extract())
                fqzf_reult.append(result_f)
        item['fqzf'] = fqzf_reult
        for expr in xpath_list:
            value = ""
            for e in expr['expr']:
                value = "".join(selector.xpath(e).extract())
                if value:
                    continue
            item[expr['key']] = value

        if item.get("supervise_number"):
            item['create_time'] = int(time.time())
            if "code" in list_data:
                item['code'] = list_data['code']
            else:
                code = list_data['region'] + list_data['located'] + list_data['acreage'] + list_data['purpose'] + list_data['supply'] + item['stime']
                item['code'] = get_md5_value(code)
            item['stime'] = list_data.get('stime')
            item['btime'] = time.strftime("%Y-%m-%d", time.localtime(int(time.time())))
            retData = self.match_mongo[DETAIL_TABLE].find_one({"supervise_number": item['supervise_number']})
            if not retData:
                self.utils.insert_mongo(self.match_mongo, DETAIL_TABLE, item)
            return True
        return False

    def main(self):
        """单进程，主入口函数"""
        while True:
            data = self.utils.queue_brpop('landchina_list_queue')
            if data:
                data = str(data, encoding='utf-8')
                url = data.split("&_gyspider=")[0]
                retData = self.match_mongo[DETAIL_TABLE].find_one({"url": url})
                if not retData:
                    list_data = json.loads(data.split("&_gyspider=")[1])
                    try:
                        html = self.start_request(url)
                        self.parse(html, list_data, url)
                    except:
                        pass
                else:
                    print("数据已存在MongoDB")
            else:
                break


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
        spider = LandDetailSpider()
        spider.main()
    else:
        print("beyond max is %s..." % num)
