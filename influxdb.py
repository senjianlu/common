#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: common/influxdb.py
# @DATE: 2024/06/14
# @TIME: 22:36:59
#
# @DESCRIPTION: InfluxDB 连接模块


from influxdb_client import InfluxDBClient

from common.config import CONFIG
from common.logger import COMMON_LOGGER as LOGGER


# 内网 host
INTRANET_HOST = None


def update_intranet_host(host: str):
    """
    @description: 更新内网 host
    @param {type}
    host: 内网 host
    @return:
    """
    global INTRANET_HOST
    INTRANET_HOST = host

def init_connection(host: str = None,
                    port: int = None,
                    token: str = None,
                    org: str = None):
    """
    @description: 初始化 InfluxDB 连接
    @param {type}
    @return:
    """
    # 1. 默认值
    host = host if host else CONFIG["influxdb"]["host"]
    port = port if port else CONFIG["influxdb"]["port"]
    token = token if token else CONFIG["influxdb"]["token"]
    org = org if org else CONFIG["influxdb"]["org"]
    # 2. 内网 host
    if INTRANET_HOST:
        host = INTRANET_HOST
    # 3. 判断参数是否为空
    if host is None or port is None or token is None or org is None:
        LOGGER.error("InfluxDB 连接参数不完整！")
        return None
    # 4. 初始化连接
    connection = InfluxDBClient(url="http://{}:{}".format(host, port), token=token, org=org)
    connection.ready()
    # 5. 打印日志
    LOGGER.info("InfluxDB 连接初始化成功")
    # 5. 返回
    return connection