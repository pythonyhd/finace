import logging
import re

import msgpack
import scrapy

from finace.config import rong_list_settings
from finace.utils.redis_db import RedisClient

logger = logging.getLogger(__name__)


class Rong360Spider(scrapy.Spider):
    name = 'rong360_list'
    redis_client = RedisClient().redis_client()

    custom_settings = rong_list_settings

    def start_requests(self):
        """融360生成redis队列"""
        while True:
            data = self.redis_client.rpop(self.name)
            if data:
                items = msgpack.unpackb(data, raw=False)
                city_name = items.get("city_name", "")
                loan_limit = items.get("loan_limit", "")
                loan_term = items.get("loan_term", "")
                city = items.get("city", "")
                url = items.get("url")
                meta_data = {'city_name': city_name, "loan_limit": loan_limit, 'loan_term': loan_term, 'city': city}
                yield scrapy.Request(url, meta={"first_item": meta_data})
            else:
                logger.info("队列为空")
                break

    def parse(self, response):
        """解析列表页，列表页翻页"""
        first_item = response.meta.get('first_item')
        # 数据解析
        selector = scrapy.Selector(text=response.text)
        tree_lis = selector.css('li[class=item] div[class=item_cont] div[class=item_info]')
        for tree in tree_lis:
            org_id = tree.xpath('./@ra-data-pl').get('')  # 详情页ID
            org_name = tree.xpath('normalize-space(./h4/a)').get('')  # 标题
            org_url = tree.css('.title a::attr(href)').get('')  # 详情url
            org_url = response.urljoin(org_url)
            spec_house = tree.xpath('.//li[@class="spec no-house" or @class="spec house"]/span[last()]/text()').get('')
            spec_work = tree.xpath('.//li[@class="spec work"]/span[last()]/text()').get('')  # 面向人群
            spec_car = tree.xpath(".//li[@class='spec car']/span[last()]/text()").get('')
            spec_time = tree.xpath(".//li[@class='spec time']/span[last()]/text()").get('')
            # 总利息 interest
            total_interest = tree.xpath('.//span[text()="总利息"]/following-sibling::span[1]/text()').get('')
            desc = ",".join(tree.xpath(".//ul[@class='meta_sep lixi']").getall()).replace(" ", "")
            ret = re.search(r'<liclass="spec"><spanclass="interest-title">月　供</span><spanclass="interest">(.*?)</span></li>', desc)
            monthly_installment = ret.group(1) if ret else ""  # 月供
            management_cost = re.search(r'每月另收贷款额的(.*?)为管理费', desc)
            management_cost = management_cost.group(1) if management_cost else ""  # 管理费
            monthly_interest_rate = re.search(r'月利率为(.*?)</span>', desc)
            monthly_interest_rate = monthly_interest_rate.group(1) if monthly_interest_rate else ""  # 月利率
            monthly_cost = re.search(r'月费(.*?)%', desc)
            monthly_cost = monthly_cost.group(1) if monthly_cost else ""
            monthly_cost = monthly_cost + str("%") if monthly_cost else ""  # 月费
            apply_num = tree.xpath('//p[@class="score"]/following-sibling::p[1]/span/text()').get("")  # 申请人数
            annual_interest_rate = tree.xpath('.//span[contains(.,"年化利率")]/text()').re_first(r' ：(.*?%)')  # 年化利率
            meta_reqs = tree.xpath('.//ul[@class="meta_sep reqs"]/li/text()').getall()
            second_item = dict(
                org_id=org_id, org_name=org_name, org_url=org_url, spec_house=spec_house, spec_work=spec_work,
                spec_car=spec_car, spec_time=spec_time, total_interest=total_interest, apply_num=apply_num,
                monthly_installment=monthly_installment, management_cost=management_cost,
                monthly_interest_rate=monthly_interest_rate, monthly_cost=monthly_cost,
                annual_interest_rate=annual_interest_rate, url=response.url, meta_reqs=meta_reqs,
            )
            item = {**first_item, **second_item}
            yield item

        # 翻页请求
        next_url = selector.xpath('//a[text()="下一页"]/@href').get('')
        if next_url:
            url = response.urljoin(next_url)
            yield scrapy.Request(url, meta={'first_item': first_item})