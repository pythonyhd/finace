# -*- coding: utf-8 -*-
from scrapy import cmdline


# 融360-自动获取城市列表
# cmdline.execute("scrapy crawl rong360_city".split())
# 融360-贷款抓取
cmdline.execute("scrapy crawl rong360_list".split())