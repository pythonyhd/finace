# -*- coding: utf-8 -*-
from finace.utils.mysql_db import MysqlPool


class CleanRongTag(object):

    def __init__(self):
        self.mysql = MysqlPool()

    def run(self, btime):
        """融360清洗打标签"""
        # 更新城市编码
        self.update_area(btime)
        # 更新org_id
        self.update_org()

    def update_area(self, btime):
        sql = """
            update  drch_public_service.loans_new as a,drch_public_service.loans_city as b
            set a.province_code=b.provinces_code,a.province_name=b.provinces_name,
            a.city_code=b.city_code,a.city_name=b.city_name,a.district_code=b.district_code,a.district_name=b.district_name
            where a.loan_city=b.loans_city and a.btime=%s
        """
        self.mysql.update(sql, [btime])
        self.mysql.end("commit")

    def update_org(self):
        sql = """
            INSERT IGNORE INTO `drch_public_service`.`loans_org` (`name`) 
            select org_name as `name` from `drch_public_service`.loans_new 
            where org_id = 0
            GROUP BY org_name
        """
        self.mysql.update(sql)
        self.mysql.end("commit")

        sql = """
            update  drch_public_service.loans_new as a,
            drch_public_service.loans_org as b
            set a.org_id=b.id
            where a.org_name=b.`name` and a.org_id= 0

        """
        self.mysql.update(sql)
        self.mysql.end("commit")
