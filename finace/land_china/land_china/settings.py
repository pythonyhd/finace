# -*- coding: utf-8 -*-


# redis配置
REDIS_HOST = '172.16.0.4'
REDIS_PORT = 6379
REDIS_PWD = 'drch@rdbc1'
REDIS_DB = 0
PROXIES_NAME = 'proxies'


# MongoDB配置
MONGO_IP = "172.16.0.7"
MONGO_PORT = 27017
MONGO_USER = 'lianpengtao'
MONGO_PWD = 'lpt1qaz2wsx'
STORE_DB = 'drcnet_spider'  # 数据库名
STORE_TABLE = 'landchina_list'  # 土地交易列表页表名
DETAIL_TABLE = 'landchina_info'  # 土地交易详情页表名


# 验证码识别
captcha_url = 'http://172.16.0.8:9090/landchina/cnn/'
