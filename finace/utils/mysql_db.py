# -*- coding: utf-8 -*-
import pymysql
from DBUtils.PooledDB import PooledDB

from finace.settings import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PWD, MYSQL_DBNAME, MYSQL_CHARSET


class MysqlPool(object):
    __pool = None

    def __init__(self):
        self._conn = MysqlPool.__get_connect()
        self._cursor = self._conn.cursor()

    @staticmethod
    def __get_connect():
        """
        @summary: 静态方法，从连接池中取出连接
        @return pymysql.connection
        """
        if MysqlPool.__pool is None:
            __pool = PooledDB(
                creator=pymysql,
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USER,
                passwd=MYSQL_PWD,
                db=MYSQL_DBNAME,
                use_unicode=False,
                charset=MYSQL_CHARSET,
                cursorclass=pymysql.cursors.DictCursor,
            )
        return __pool.connection()

    def get_all(self, sql, param=None):
        """
        @summary: 执行查询，并取出所有结果集
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list(字典对象)/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchall()
        else:
            result = False
        return result

    def get_one(self, sql, param=None):
        """
        @summary: 执行查询，并取出第一条
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchone()
        else:
            result = False
        return result

    def get_many(self, sql, num, param=None):
        """
        @summary: 执行查询，并取出num条结果
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param num:取得的结果条数
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchmany(num)
        else:
            result = False
        return result

    def insert_one(self, sql, value):
        """
        @summary: 向数据表插入一条记录
        @param sql:要插入的ＳＱＬ格式
        @param value:要插入的记录数据tuple/list
        @return: insertId 受影响的行数
        """
        self._cursor.execute(sql, value)
        return self.__get_insert_id()

    def insert(self, table, item):
        """
        @summary: 向数据表插入数据
        @param table:要插入的表名
        @param item:要插入的记录数据item
        @return: insertId 受影响的行数
        """
        fields = ", ".join(list(item.keys()))
        sub_char = ", ".join(["%s"] * len(item))
        values = tuple(list(item.values()))
        sql = "insert into %s(%s) values (%s)" % (table, fields, sub_char)
        self._cursor.execute(sql, values)

    def insert_rong360(self, table, item):
        """
        @summary: 定向清洗融360数据
        @param table:要插入的表名
        @param item:要插入的记录数据item
        @return: insertId 受影响的行数
        """
        fields = ", ".join(list(item.keys()))
        sub_char = ", ".join(["%s"] * len(item))
        values = tuple(list(item.values()))
        sql = "insert IGNORE into %s(%s) values (%s)" % (table, fields, sub_char)
        self._cursor.execute(sql, values)

    def insert_many(self, table, items):
        """
        @summary: 向数据表插入多条数据
        @param table:要插入的表名
        @param item:要插入的记录数据item
        @return: insertId 受影响的行数
        """
        item = items[0]
        fields = ", ".join(list(item.keys()))
        sub_char = ", ".join(["%s"] * len(item))
        value_list = []
        for item in items:
            value = tuple(list(item.values()))
            value_list.append(value)

        sql = "insert into %s(%s) values (%s)" % (table, fields, sub_char)
        self._cursor.executemany(sql, value_list)

    def update_one(self, table, update_item, condition):
        """
        @summary: 更新数据表记录
        @param table: 表名
        @param update_item: 要更新的字段
        @param condition: 筛选要更新的字段
        @return:
        """
        fields = ", ".join(['{}="{}"'.format(key, value) for key, value in update_item.items()])
        filter_condition = " and ".join(['{}="{}"'.format(key, value) for key, value in condition.items()])

        sql = "update %s set %s where %s" % (table, fields, filter_condition)

        self._cursor.execute(sql)

    def __get_insert_id(self):
        """
        获取当前连接最后一次插入操作生成的id,如果没有则为０
        """
        self._cursor.execute("SELECT @@IDENTITY AS id")
        result = self._cursor.fetchall()
        return result[0]['id']

    def __query(self, sql, param=None):
        """
        执行SQL语句
        @param sql: 要执行的SQL语句
        @param param:
        @return: 结果
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        return count

    def update(self, sql, param=None):
        """
        @summary: 更新数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要更新的  值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)

    def delete(self, sql, param=None):
        """
        @summary: 删除数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要删除的条件 值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)

    def begin(self):
        """
        @summary: 开启事务
        """
        self._conn.autocommit(0)

    def end(self, option='commit'):
        """
        @summary: 结束事务
        """
        if option == 'commit':
            self._conn.commit()
        else:
            self._conn.rollback()

    def dispose(self, isEnd=1):
        """
        @summary: 释放连接池资源
        """
        if isEnd == 1:
            self.end('commit')
        else:
            self.end('rollback')
        self._cursor.close()
        self._conn.close()


if __name__ == '__main__':
    pool = MysqlPool()