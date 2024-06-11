#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: ~/Projects/common/rabbitmq.py
# @DATE: 2024/02/25 周日
# @TIME: 11:24:59
#
# @DESCRIPTION: RabbitMQ 连接模块


import ssl
import pika
import requests

from common.config import CONFIG
from common.logger import COMMON_LOGGER as LOGGER


# 内网 host
# INTRANET_HOST = None
# RabbitMQ 配置组 key 和内网 host 字典
RABBITMQ_CONFIG_GROUP_KEY_2_INTRANET_HOST_DICT = {}


def update_intranet_host(rabbitmq_config_group_key: str, host: str):
    """
    @description: 更新内网 host
    @param {type}
    host: 内网 host
    @return:
    """
    global INTRANET_HOST
    RABBITMQ_CONFIG_GROUP_KEY_2_INTRANET_HOST_DICT[rabbitmq_config_group_key] = host

def init_connection(rabbitmq_config_group_key: str = "rabbitmq",
                    host: str = None,
                    port: int = None,
                    username: str = None,
                    password: str = None,
                    is_ssl_enabled: bool = False):
    """
    @description: 初始化 RabbitMQ 连接
    @param {type} 
    @return: 
    """
    # 1. 默认值
    host = host if host else CONFIG[rabbitmq_config_group_key]["host"]
    port = port if port else CONFIG[rabbitmq_config_group_key]["port"]
    username = username if username else CONFIG[rabbitmq_config_group_key]["username"]
    password = password if password else CONFIG[rabbitmq_config_group_key]["password"]
    # 2. 内网 host
    if rabbitmq_config_group_key in RABBITMQ_CONFIG_GROUP_KEY_2_INTRANET_HOST_DICT:
        host = RABBITMQ_CONFIG_GROUP_KEY_2_INTRANET_HOST_DICT[rabbitmq_config_group_key]
    # 3. 判断参数是否为空
    if host is None or port is None or username is None or password is None:
        LOGGER.error("RabbitMQ 连接参数不完整！")
        return None
    # 4. 判断是否需要开启 SSL
    ssl_options = None
    if is_ssl_enabled:
        # 暂时不验证证书
        # context = ssl.create_default_context(cafile=CONFIG["rabbitmq"]["ssl"]["ca_certificate"])
        context = ssl._create_unverified_context()
        context.load_cert_chain(CONFIG["rabbitmq"]["ssl"]["client_certificate"], CONFIG["rabbitmq"]["ssl"]["client_key"])
        ssl_options = pika.SSLOptions(context, host)
    # 5. 连接 RabbitMQ
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=host,
                port=port,
                credentials=pika.PlainCredentials(
                    username=username,
                    password=password
                ),
                ssl_options=ssl_options
            )
        )
    except Exception as e:
        LOGGER.error(msg="连接 RabbitMQ 失败！错误信息：{}".format(e))
        return None
    return connection

def get_queue_list(rabbitmq_config_group_key: str = "rabbitmq",
                   api_host: str = None,
                   api_username: str = None,
                   api_password: str = None):
    """
    @description: 获取队列列表
    @param {type}
    @return:
    """
    # 1. 默认值
    api_host = api_host if api_host else CONFIG[rabbitmq_config_group_key]["api"]["host"]
    api_username = api_username if api_username else CONFIG[rabbitmq_config_group_key]["api"]["username"]
    api_password = api_password if api_password else CONFIG[rabbitmq_config_group_key]["api"]["password"]
    # 2. 发送请求
    url = "{}/api/queues".format(api_host.strip("/"))
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(
            url,
            auth=(api_username, api_password),
            headers=headers,
            timeout=30
        )
        response_json = response.json()
    except Exception as e:
        LOGGER.error("RabbitMQ -> 获取队列列表失败，错误信息：{}".format(e))
        return []
    # 3. 判断响应是否成功
    if not response_json:
        LOGGER.error("RabbitMQ -> 获取队列列表失败，响应为空")
        return []
    # 4. 返回结果
    return response_json