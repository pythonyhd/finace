# -*- coding: utf-8 -*-
import datetime

from finace.clean.rong_clean import CleanRongList
from finace.clean.update_tag import CleanRongTag
from finace.utils.mysql_db import MysqlPool


class CleanoutRong360:
    def __init__(self):
        self.mysql = MysqlPool()

    def run(self):
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        btime = str(yesterday)

        # 融360清洗入口函数，今天清洗昨天的数据
        CleanRongList().run({"btime": btime})
        CleanRongTag().run(btime)

        self.mysql.dispose()


if __name__ == '__main__':
    clear = CleanoutRong360()
    clear.run()