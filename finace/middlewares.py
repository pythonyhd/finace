# -*- coding: utf-8 -*-
import base64
import logging
import random
import time

import redis
from fake_useragent import UserAgent
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.python import global_object_name
from scrapy.utils.response import response_status_message

from finace import settings
from finace.settings import user_pass

logger = logging.getLogger(__name__)


class RandomUserAgentMiddleware(object):
    """利用fake_useragent生成随机请求头"""

    def __init__(self, user_type):
        self.user_type = user_type
        self.user_agent = UserAgent()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(user_type=crawler.settings.get('RANDOM_USER_AGENT', 'chrome'))

    def process_request(self, request, spider):
        def get_user_agent():
            return getattr(self.user_agent, self.user_type)

        request.headers.setdefault(b'User-Agent', get_user_agent())


class RandomProxyMiddlerware(object):
    """VPS随机IP"""

    def __init__(self, proxy_redis_host, proxy_redis_port, proxy_redis_password, proxy_redis_db):
        self.redis_proxy = redis.StrictRedis(host=proxy_redis_host, port=proxy_redis_port,
                                             password=proxy_redis_password, db=proxy_redis_db)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            proxy_redis_host=crawler.settings.get('REDIS_PROXIES_HOST'),
            proxy_redis_port=crawler.settings.get('REDIS_PROXIES_PORT'),
            proxy_redis_password=crawler.settings.get('REDIS_PROXIES_PASSWORD'),
            proxy_redis_db=crawler.settings.get('REDIS_PROXIES_DB'),
        )

    def process_request(self, request, spider):
        ip_port = self.redis_proxy.srandmember(settings.PROXIES_NAME)
        if ip_port:
            proxies = {
                'http': 'http://{}'.format(ip_port.decode('utf-8')),
                'https': 'https://{}'.format(ip_port.decode('utf-8')),
            }
            if request.url.startswith('http://'):
                request.meta['proxy'] = proxies.get("http")
                logger.debug('http链接,ip:{}'.format(request.meta.get('proxy')))
            else:
                request.meta['proxy'] = proxies.get('https')
                logger.debug('https链接,ip:{}'.format(request.meta.get('proxy')))
        else:
            logger.info('代理池枯竭--IP数量不足--等待重新拨号')
            time.sleep(10)


class ProxyMiddleware(object):
    """本地免费代理池"""

    def process_request(self, request, spider):
        PROXIES = [{'ip_port': random.choice(user_pass), 'user_pass': 'martindu:fy1812!!'}]
        proxy = random.choice(PROXIES)
        if request.url.startswith('http://'):
            request.meta['proxy'] = "http://%s" % proxy['ip_port']
            encoded_user_pass = base64.b64encode(proxy['user_pass'].encode('utf-8'))
            request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass.decode()
        else:
            request.meta['proxy'] = "https://%s" % proxy['ip_port']
            encoded_user_pass = base64.b64encode(proxy['user_pass'].encode('utf-8'))
            request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass.decode()
