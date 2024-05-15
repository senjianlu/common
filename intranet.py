#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: common/intranet.py
# @DATE: 2024/05/15
# @TIME: 19:48:53
#
# @DESCRIPTION: 内网测试模块


import ssl

from common.config import CONFIG
from common.logger import LOGGER


def test_postgresql():
    """
    @description: 测试 PostgreSQL 连接
    @param {type}
    """
    # 1. 读取配置
    intranet_hosts = CONFIG["postgresql"]["intranet_hosts"] if "intranet_hosts" in CONFIG["postgresql"] else []
    if not intranet_hosts:
        LOGGER.error("内网测试 -> PostgreSQL 内网配置为空")
        return
    # 2. 测试连接
    import psycopg2
    intranet_host = None
    for host in intranet_hosts:
        try:
            conn = psycopg2.connect(
                host=host,
                port=CONFIG["postgresql"]["port"],
                user=CONFIG["postgresql"]["username"],
                password=CONFIG["postgresql"]["password"],
                dbname=CONFIG["postgresql"]["database"]
            )
            conn.close()
            LOGGER.info(f"内网测试 -> PostgreSQL 连接测试成功，host: {host}")
            intranet_host = host
            break
        except Exception as e:
            LOGGER.error(f"内网测试 -> PostgreSQL 连接测试失败，host: {host}，错误信息: {e}")
    # 3. 更新内网 host
    if intranet_host:
        from common.Base import update_intranet_host
        update_intranet_host(intranet_host)
        LOGGER.info(f"内网测试 -> PostgreSQL 内网 host 更新成功，host: {intranet_host}")
    else:
        LOGGER.error("内网测试 -> PostgreSQL 无可用内网 host")

def test_rabbitmq(is_ssl_enabled: bool = False):
    """
    @description: 测试 RabbitMQ 连接
    @param {type}
    """
    # 1. 读取配置
    intranet_hosts = CONFIG["rabbitmq"]["intranet_hosts"] if "intranet_hosts" in CONFIG["rabbitmq"] else []
    if not intranet_hosts:
        LOGGER.error("内网测试 -> RabbitMQ 内网配置为空")
        return
    # 2. 测试连接
    import pika
    intranet_host = None
    for host in intranet_hosts:
        # 2.1 SSL 设置
        ssl_options = None
        if is_ssl_enabled:
            # 暂时不验证证书
            # context = ssl.create_default_context(cafile=CONFIG["rabbitmq"]["ssl"]["ca_certificate"])
            context = ssl._create_unverified_context()
            context.load_cert_chain(CONFIG["rabbitmq"]["ssl"]["client_certificate"],
                                    CONFIG["rabbitmq"]["ssl"]["client_key"])
            ssl_options = pika.SSLOptions(context, host)
        # 2.2 连接 RabbitMQ
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=host,
                    port=CONFIG["rabbitmq"]["port"],
                    credentials=pika.PlainCredentials(
                        username=CONFIG["rabbitmq"]["username"],
                        password=CONFIG["rabbitmq"]["password"]
                    ),
                    ssl_options=ssl_options
                )
            )
            connection.close()
            LOGGER.info(f"内网测试 -> RabbitMQ 连接测试成功，host: {host}")
            intranet_host = host
            break
        except Exception as e:
            LOGGER.error(f"内网测试 -> RabbitMQ 连接测试失败，host: {host}，错误信息: {e}")
    # 3. 更新内网 host
    if intranet_host:
        from common.rabbitmq import update_intranet_host
        update_intranet_host(intranet_host)
        LOGGER.info(f"内网测试 -> RabbitMQ 内网 host 更新成功，host: {intranet_host}")
    else:
        LOGGER.error("内网测试 -> RabbitMQ 无可用内网 host")

def test_redis():
    """
    @description: 测试 Redis 连接
    @param {type}
    """
    # 1. 读取配置
    intranet_hosts = CONFIG["redis"]["intranet_hosts"] if "intranet_hosts" in CONFIG["redis"] else []
    if not intranet_hosts:
        LOGGER.error("内网测试 -> Redis 内网配置为空")
        return
    # 2. 测试连接
    import redis
    intranet_host = None
    for host in intranet_hosts:
        try:
            conn = redis.StrictRedis(
                host=host,
                port=CONFIG["redis"]["port"],
                db=CONFIG["redis"]["db"],
                password=CONFIG["redis"]["password"],
                decode_responses=True
            )
            conn.ping()
            LOGGER.info(f"内网测试 -> Redis 连接测试成功，host: {host}")
            intranet_host = host
            break
        except Exception as e:
            LOGGER.error(f"内网测试 -> Redis 连接测试失败，host: {host}，错误信息: {e}")
    # 3. 更新内网 host
    if intranet_host:
        from common.redis import update_intranet_host
        update_intranet_host(intranet_host)
        LOGGER.info(f"内网测试 -> Redis 内网 host 更新成功，host: {intranet_host}")
    else:
        LOGGER.error("内网测试 -> Redis 无可用内网 host")
