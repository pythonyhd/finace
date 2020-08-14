# -*- coding: utf-8 -*-
import hashlib
import math
import re
import time

from tqdm import tqdm

from finace.settings import MONGODB_HOST, MONGODB_PORT, MONGO_USER, MONGO_PWD, MONGO_DATA_BASE, MONGO_TABLE
from finace.utils.mongo_db import MongoClient
from finace.utils.mysql_db import MysqlPool


class CleanRongList(object):

    def __init__(self):
        self.mongo = MongoClient(host=MONGODB_HOST, port=MONGODB_PORT, user=MONGO_USER, password=MONGO_PWD,
                                 db_name=MONGO_DATA_BASE, table=MONGO_TABLE)
        self.proposers = {}
        self.mysql = MysqlPool()

    def run(self, query={}):
        """融360清洗MongoDB列表页基本数据，入口函数"""
        # 从MySQL里面loans_proposer表读取数据处理成字典，目的是为了跟loans_spec_new表做对应关系
        for p in self.mysql.get_all("select * from drch_public_service.loans_proposer"):
            name = str(p['name'], encoding='utf-8')
            self.proposers[name] = p['id']

        # 分页读取MongoDB数据
        mongo_count = self.mongo.count()
        limit = 20000
        mongo_page = int(math.ceil(mongo_count / limit))
        meter = tqdm(initial=0, total=mongo_count, ascii=True)
        for page in range(0, mongo_page + 1):
            for data in self.mongo.read(page, limit, query):
                self.clear(data)
                meter.update(1)
            self.mysql.end("commit")
        meter.close()

    def clear(self, item):
        result = {
            'code': self.get_md5_value(item.get('data_tag')),  # 惟一标识
            'name': item['org_name'],  # 贷款名称
            'loan_city': item['city_name'],  # 城市
            'real_loan_quota': item['loan_limit'],  # 贷款金额
            'real_loan_cycle': item['loan_term'],  # 贷款周期
            'loan_type': None,  # '贷款类型(自定义)',
            'loan_type_id': 0,  # '贷款类型id(自定义)',
            'spec_work': '',  # 申请人范围
            'make_loans_cycle': 0,  # 放款周期
            'pledge': "",  # 抵押
            'gross_interest': 0,  # 总利息
            'year_interest': 0,  # 年化利率
            'apply_num': 0,  # 申请人数，0为小于100
            'monthly_installment': 0,  # 月供，不是每个都有
            'org_name': item['org_name'].split("-")[0].strip().replace(".", ''),  # 机构名称
            'org_code': item['org_id'],  # 机构编码
            'org_id': 0,  # 自定义机构id
            'monthly_interest': 0,  # 月利率
            'monthly_cost': 0,  # 月费
            'nonrecurring_expense': 0,  # 一次性费用
            'btime': item['btime'],
            'create_time': int(time.time())
        }
        # 自己添加分类
        if "房" in result['name'] or "公积金" in result['name'] or "宅" in result['name'] or "装修" in result['name']:
            result['loan_type'] = "房贷"
            result['loan_type_id'] = 1
        elif "车" in result['name'] or "公积金" in result['name']:
            result['loan_type'] = "车贷"
            result['loan_type_id'] = 2
        elif "企业" in result['name'] or "经营" in result['name'] or "厂" in result['name'] or "商" in result['name']:
            result['loan_type'] = "经营贷"
            result['loan_type_id'] = 3
        else:
            result['loan_type'] = "其他消费贷"
            result['loan_type_id'] = 4

        # 放款周期
        spec_time = re.search(r'(\d+)', item.get('spec_time'))
        result['make_loans_cycle'] = spec_time.group(1) if spec_time else None

        # 总利息
        total_interest = re.search(r'(\d+\.?\d+)', item.get('total_interest'))
        result['gross_interest'] = total_interest.group(1) if total_interest else None

        # 申请人数
        apply_num = item.get('apply_num')
        if "少于" in apply_num:
            result['apply_num'] = 50  # 专家定的
        else:
            apply_num = re.search(r'(\d+)', item.get('apply_num'))
            result['apply_num'] = apply_num.group(1) if apply_num else None

        # 申请人范围
        spec_work = item.get('spec_work')
        if "无身份限制" in spec_work:
            result['spec_work'] = '上班族,个体户,无固定职业,企业主,学生'
        else:
            spec_works = []
            for spec in spec_work.split(" "):
                if spec != '可申请':
                    spec_works.append(spec)
            result['spec_work'] = ",".join(spec_works)

        # 月费
        monthly_cost = item.get('monthly_cost')
        ret = re.findall("\d+\.?\d+", monthly_cost)
        if ret:
            result['monthly_cost'] = ret[0]

        # 年化利率
        ret = re.findall("\d+\.?\d+", item['annual_interest_rate'])
        if ret:
            result['year_interest'] = ret[0]

        # 月利率
        monthly_interest_rate = item.get('monthly_interest_rate')
        ret = re.findall("\d+\.?\d+", monthly_interest_rate)
        if ret:
            result['monthly_interest'] = ret[0]
        # 如果月息(用月供除以贷款总额，注意贷款总额的单位是万元，如果月息一栏有现成数据，则用现成数据)
        if result['monthly_interest'] == 0:
            result['monthly_interest'] = float(result['monthly_installment']) / (float(result['real_loan_quota']) * 10000)

        # 月供
        ret = re.findall("\d+\.?\d+", item['monthly_installment'])
        if ret:
            result['monthly_installment'] = ret[0]
        else:
            gross_interest = 0
            if result['gross_interest']:
                gross_interest = float(result['gross_interest'])
            result['monthly_installment'] = (gross_interest * 10000 + float(result['real_loan_quota']) * 10000) / float(result['real_loan_cycle'])

        # 抵押
        pledge = []
        spec_house = item.get('spec_house')
        spec_car = item.get('spec_car')
        if "spec_house" in item:
            if spec_house:
                pledge.append(spec_house)
        if "spec_car" in item:
            if spec_car:
                pledge.append(spec_car)
        if pledge:
            result['pledge'] = "".join(pledge)

        # 什么客户可申请，插入MySQL单独的关联表
        for spec in result['spec_work'].split(","):
            result_spec = {
                'loans_code': result['code'],
                'proposer_id': self.proposers[spec],
                'proposer_name': spec,
            }
            self.insert_data(result_spec, 2)

        self.insert_data(result)

    def insert_data(self, result, stype=1):
        """插入MySQL不同的表"""
        if stype == 1:
            table = "loans_new"
        else:
            table = "loans_spec_new"
        self.mysql.insert_rong360(table, result)

    def get_md5_value(self, _str):
        """通用MD5方法"""
        if isinstance(_str, str):
            md5_obj = hashlib.md5()
            md5_obj.update(_str.encode())
            md5_code = md5_obj.hexdigest()
            return md5_code
        else:
            return None


if __name__ == '__main__':
    clear = CleanRongList()
    clear.run()
