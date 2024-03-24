#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: common/gost.py
# @DATE: 2024/03/24
# @TIME: 16:52:13
#
# @DESCRIPTION: GOST 转发控制


from common.logger import LOGGER
from common.logger import CONFIG
from common.logic import gost_config
from common.logic import gost_service


# 全局变量
ADSPOWER_HOST = CONFIG["gost"]["host"]


def check_api_status():
    """
    @description: 检查 API 状态
    """
    # 1. 请求配置
    config = gost_config.get_config()
    # 2. 检查配置
    if not config:
        LOGGER.error("GOST 转发控制 -> API 配置获取失败")
        return False
    # 3. 其他情况
    LOGGER.info("GOST 转发控制 -> API 状态正常")
    return True

def add_port_forward(from_host: str,
                     from_port: int,
                     from_protocol: str,
                     to_host: str,
                     to_port: int,
                     to_protocol: str,
                     name: str = None,
                     from_auth_username: str = None,
                     from_auth_password: str = None,
                     to_auth_username: str = None,
                     to_auth_password: str = None):
    # 1. 检查 API 状态
    if not check_api_status():
        LOGGER.error("GOST 转发控制 -> API 状态异常，无法添加转发规则")
        return False
    # 2. 检查参数
    if not from_host or not from_port or not from_protocol or not to_host or not to_port or not to_protocol:
        LOGGER.error("GOST 转发控制 -> 参数缺失，无法添加转发规则")
        return False
    # 3. 修改参数
    name = "port-forward-{}-{}-{}-to-{}-{}-{}-service".format(from_protocol, from_host, from_port, to_protocol, to_host, to_port) if not name else name
    # 4. 检查是否存在
    if gost_service.is_exist(name):
        LOGGER.error("GOST 转发控制 -> 转发规则已存在，无法添加")
        return False
    # 5. 构建转发规则
    # 5.1 构建节点
    to_node = {
        "name": "{}-node".format(name),
        "addr": "{}:{}".format(to_host, to_port),
        "connector": {
            "type": to_protocol,
            "auth": {
                "username": to_auth_username,
                "password": to_auth_password
            } if to_auth_username and to_auth_password else {}
        }
    }
    # 5.1 构建转发器
    forwarder = {
        "nodes": [to_node],
    }
    # 5.2 构建服务
    service = {
        "name": "{}".format(name),
        "addr": "{}:{}".format(from_host, from_port),
        "handler": {
            "type": from_protocol,
        },
        "listener": {
            "type": from_protocol,
        },
        "forwarder": forwarder
    }
    # 5. 添加转发规则
    if not gost_service.add(
            name=service["name"],
            addr=service["addr"],
            handler=service["handler"],
            listener=service["listener"],
            forwarder=service["forwarder"]):
        LOGGER.error("GOST 转发控制 -> 添加转发规则失败")
        return False
    # 6. 返回结果
    LOGGER.info("GOST 转发控制 -> 添加转发规则成功")
    return True

def delete_port_forward(from_host: str = None,
                        from_port: int = None,
                        from_protocol: str = None,
                        to_host: str = None,
                        to_port: int = None,
                        to_protocol: str = None,
                        name: str = None):
    """
    @description: 删除端口转发
    """
    # 1. 检查 API 状态
    if not check_api_status():
        LOGGER.error("GOST 转发控制 -> API 状态异常，无法删除转发规则")
        return False
    # 2. 检查参数
    if not from_host and not from_port and not from_protocol and not to_host and not to_port and not to_protocol and not name:
        LOGGER.error("GOST 转发控制 -> 参数缺失，无法删除转发规则")
        return False
    # 3. 修改参数
    name = "port-forward-{}-{}-{}-to-{}-{}-{}-service".format(from_protocol, from_host, from_port, to_protocol, to_host, to_port) if not name else name
    # 4. 检查是否存在
    if not gost_service.is_exist(name):
        LOGGER.error("GOST 转发控制 -> 转发规则不存在，无法删除")
        return False
    # 5. 删除转发规则
    if not gost_service.delete(name):
        LOGGER.error("GOST 转发控制 -> 删除转发规则失败")
        return False
    # 6. 返回结果
    LOGGER.info("GOST 转发控制 -> 删除转发规则成功")
    return True