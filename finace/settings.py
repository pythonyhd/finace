

BOT_NAME = 'finace'

SPIDER_MODULES = ['finace.spiders']
NEWSPIDER_MODULE = 'finace.spiders'


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
scrapy 基本配置
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
ROBOTSTXT_OBEY = False
LOG_LEVEL = "INFO"
RANDOM_USER_AGENT = "chrome"

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
数据存储 相关配置
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# 存储到mongodb
# MONGODB_HOST = '172.16.0.7'
MONGODB_HOST = '127.0.0.1'
MONGO_USER = 'lianpengtao'
# MONGO_PWD = 'lpt1qaz2wsx'
MONGO_PWD = 'lpt1qaz2wsx!@'
MONGODB_PORT = 27017
MONGO_DATA_BASE = 'drcnet_spider'  # 数据库名
MONGO_CITY = "rong360_city"  # 获取城市列表信息
MONGO_TABLE = "rong360_list_new"  # 需要清洗的原始数据表

# MySQL相关配置
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PWD = "123456"
MYSQL_DBNAME = "drch_public_service"
MYSQL_CHARSET = "utf8"

# redis 基础配置
REDIS_HOST = '172.16.0.4'
REDIS_PORT = 6379
REDIS_PASSWORD = "drch@rdbc1"
REDIS_DB = 1
REDIS_PARAMS = {
    "password": "drch@rdbc1",
    "db": 1,
}

# redis 代理池配置
REDIS_PROXIES_HOST = '172.16.0.4'
REDIS_PROXIES_PORT = 6379
REDIS_PROXIES_PASSWORD = 'drch@rdbc1'
REDIS_PROXIES_DB = 0
PROXIES_NAME = 'proxies'

user_pass = [
    '139.198.4.181:443',
]