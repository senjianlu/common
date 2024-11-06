#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: common/common_db.py
# @DATE: 2024/11/01
# @TIME: 17:40:43
#
# @DESCRIPTION: 本地数据库模块


import os
import sqlite3

from sqlalchemy.ext.declarative import declarative_base


# 本地数据库路径
LOCAL_DB_PATH = os.path.join(os.path.dirname(__file__), "common_database/common.db")
# 基类
LOCAL_BASE = declarative_base()


def init():
    """
    @description: 初始化数据库
    @param {type}
    @return: 数据库连接
    """
    # 1. 获取数据库文件路径
    db_path = os.path.join(os.path.dirname(__file__), LOCAL_DB_PATH)
    # 2. 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    return conn, cursor

def close(conn, cursor):
    """
    @description: 关闭数据库
    @param {type}
    conn: 数据库连接
    @return:
    """
    cursor.close()
    conn.close()


# 临时测试
# if __name__ == "__main__":
#     conn, cursor = init()
#     cursor.execute("SELECT * FROM sqlite_master WHERE type='table'")
#     print(cursor.fetchall())
#     close(conn, cursor)
    