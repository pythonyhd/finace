# -*- coding: utf-8 -*-
import redis

from finace.settings import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DB


class RedisClient(object):
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=REDIS_DB):
        self.redis_pool = redis.ConnectionPool(host=host, port=port, password=password, db=db)
        self.redis = redis.Redis(connection_pool=self.redis_pool)

    def redis_client(self):
        return self.redis


if __name__ == '__main__':
    redis = RedisClient(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=REDIS_DB)
    client = redis.redis_client()
