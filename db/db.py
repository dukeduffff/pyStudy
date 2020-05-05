#!/usr/bin/python3
#coding=utf-8

import pymysql
import random
import string


def ran():
    salt = ''.join(random.sample(string.ascii_letters + string.digits, 8))
    return salt


# 打开mysql数据库链接

connect = pymysql.connect(
    host='mydocker',
    port=3306,
    user='root',
    password='22372901',
    database='test',
    charset='utf8'
)

cursor = connect.cursor()

# for i in range(1000):
#     cursor.execute("insert into user(NAME, CITY) values ('%s', '北京')" % i)
#
# for i in range(1000, 2000):
#     cursor.execute("insert into user(NAME, CITY) values ('%s', '上海')" % i)

for i in range(10000):
    cursor.execute("insert into words(word) values('%s')" % ran())
data = cursor.fetchone()

connect.commit()

print("value:%s" % data)

connect.close()
