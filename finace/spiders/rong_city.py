import time

import scrapy

from finace.config import rong_city_settings


class RongCitySpider(scrapy.Spider):
    name = 'rong360_city'
    start_urls = ['https://www.rong360.com/cityNavi.html']
    custom_settings = rong_city_settings

    def parse(self, response):
        """获取城市列表"""
        create_time = int(time.time())
        flag = int(1)
        local_ip = '172.16.0.5'
        selector = scrapy.Selector(text=response.text)
        city_list = selector.xpath('//div[@id="TabWordList"]/div/div[@class="citys city_list"]/a')
        for city in city_list:
            name = city.xpath('./span/text()').get('')
            url = city.xpath('./@domain').get('')
            item = dict(name=name, url=url, create_time=create_time, flag=flag, local_ip=local_ip)
            yield item