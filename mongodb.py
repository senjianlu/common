#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: common/mongodb.py
# @DATE: 2024/08/11
# @TIME: 21:11:20
#
# @DESCRIPTION: 共通包 MongoDB 模块


import pymongo

from common.logger import LOGGER
from common.logger import CONFIG


def init_client(host: str = None,
                port: int = None,
                username: str = None,
                password: str = None):
    """
    @description: 初始化 MongoDB 客户端
    @param {type}
    @return:
    """
    # 1. 默认值
    host = host if host else CONFIG["mongodb"]["host"]
    port = port if port else CONFIG["mongodb"]["port"]
    username = username if username else CONFIG["mongodb"]["username"]
    password = password if password else CONFIG["mongodb"]["password"]
    # 2. 判断参数是否为空
    if host is None or port is None or username is None or password is None:
        LOGGER.error("MongoDB 客户端参数不完整！")
        return None
    # 3. 初始化连接
    client = pymongo.MongoClient("mongodb://{}:{}@{}:{}/".format(username, password, host, port))
    # 4. 打印日志
    LOGGER.info("MongoDB 连接成功！")
    return client
