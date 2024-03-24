#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: ~/Projects/common/rabbitmq.py
# @DATE: 2024/02/25 周日
# @TIME: 11:24:59
#
# @DESCRIPTION: RabbitMQ 连接模块


import pika
import requests

from common.config import CONFIG
from common.logger import LOGGER


def init_connection(host: str = CONFIG["rabbitmq"]["host"],
                    port: int = CONFIG["rabbitmq"]["port"],
                    username: str = CONFIG["rabbitmq"]["username"],
                    password: str = CONFIG["rabbitmq"]["password"]):
    """
    @description: 初始化 RabbitMQ 连接
    @param {type} 
    @return: 
    """
    # 1. 判断参数是否为空
    if host is None or port is None or username is None or password is None:
        LOGGER.error("RabbitMQ 连接参数不完整！")
        return None
    # 2. 连接 RabbitMQ
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=host,
                port=port,
                credentials=pika.PlainCredentials(
                    username=username,
                    password=password
                )
            )
        )
    except Exception as e:
        LOGGER.error(msg="连接 RabbitMQ 失败！错误信息：{}".format(e))
        return None
    return connection

def get_queue_list(api_host: str = CONFIG["rabbitmq"]["api"]["host"],
                   api_username: str = CONFIG["rabbitmq"]["api"]["username"],
                   api_password: str = CONFIG["rabbitmq"]["api"]["password"]):
    """
    @description: 获取队列列表
    @param {type}
    @return:
    """
    # 1. 发送请求
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
    # 2. 判断响应是否成功
    if not response_json:
        LOGGER.error("RabbitMQ -> 获取队列列表失败，响应为空")
        return []
    # 3. 返回结果
    return response_json