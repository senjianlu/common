#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: common/stash.py
# @DATE: 2024/11/01
# @TIME: 17:40:43
#
# @DESCRIPTION: 暂存模块


import os
import sqlite3

from sqlalchemy.ext.declarative import declarative_base


# 本地暂存路径
STASH_DIR_PATH = os.path.join(os.path.dirname(__file__), "stash")
# 本地数据库路径
STASH_DATABASE_PATH = os.path.join(STASH_DIR_PATH, "common.db")


def init_database(db_path = STASH_DATABASE_PATH):
    """
    @description: 初始化数据库
    @param {type}
    @return: 数据库连接
    """
    # 1. 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # 2. 返回连接
    return conn, cursor

def close_database(conn, cursor):
    """
    @description: 关闭数据库
    @param {type}
    conn: 数据库连接
    @return:
    """
    cursor.close()
    conn.close()


# 临时测试
if __name__ == "__main__":
    conn, cursor = init_database()
    cursor.execute("SELECT * FROM sqlite_master WHERE type='table'")
    print(cursor.fetchall())
    close_database(conn, cursor)
    