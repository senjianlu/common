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
from common.logic import gost_chain


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

def get_config():
    """
    @description: 获取配置
    """
    return gost_config.get_config()

def get_port_forward_service_list(from_host: str = None,
                                  from_port: int = None,
                                  from_protocol: str = None,
                                  to_host: str = None,
                                  to_port: int = None,
                                  to_protocol: str = None):
    """
    @description: 获取端口转发服务列表
    """
    # 1. 检查 API 状态
    if not check_api_status():
        LOGGER.error("GOST 转发控制 -> API 状态异常，无法获取转发规则")
        return None
    # 2. 检查参数
    if (not from_host or not from_port) and (not to_host or not to_port):
        LOGGER.error("GOST 转发控制 -> 参数缺失，无法获取转发规则")
        return None
    # 3. 拼凑 name_like
    service_name_like = ""
    if from_host and from_port:
        service_name_like += (from_protocol + "-") if from_protocol else ""
        service_name_like += (from_host + "-") if from_host else ""
        service_name_like += (str(from_port) + "-") if from_port else ""
        service_name_like += "to-"
    if to_host and to_port:
        service_name_like += (to_protocol + "-") if to_protocol else ""
        service_name_like += (to_host + "-") if to_host else ""
        service_name_like += (str(to_port) + "-") if to_port else ""
        service_name_like += "service"
    # 4. 获取转发规则
    service_list = gost_service.get_by_name_like(service_name_like)
    # 5. 返回结果
    LOGGER.info("GOST 转发控制 -> 获取转发规则成功")
    return service_list

def add_port_forward_service_without_chain(from_host: str,
                                           from_port: int,
                                           from_protocol: str,
                                           to_host: str,
                                           to_port: int,
                                           to_protocol: str,
                                           base_name: str = None,
                                           from_auth_username: str = None,
                                           from_auth_password: str = None,
                                           to_auth_username: str = None,
                                           to_auth_password: str = None):
    """
    @description: 添加端口转发服务（不通过转发链，直接转发）
    """
    # 1. 检查 API 状态
    if not check_api_status():
        LOGGER.error("GOST 转发控制 -> API 状态异常，无法添加转发规则")
        return False
    # 2. 检查参数
    if not from_host or not from_port or not from_protocol or not to_host or not to_port or not to_protocol:
        LOGGER.error("GOST 转发控制 -> 参数缺失，无法添加转发规则")
        return False
    # 3. 修改参数
    base_name = "port-forward-{}-{}-{}-to-{}-{}-{}".format(from_protocol, from_host, from_port, to_protocol, to_host, to_port) if not base_name else base_name
    service_name = base_name + "-service"
    node_name = base_name + "-node"
    # 4. 检查是否存在
    if gost_service.is_exist(service_name):
        LOGGER.error("GOST 转发控制 -> 转发规则已存在，无法添加")
        return False
    # 5. 构建转发规则
    # 5.1 构建节点
    to_node = {
        "name": node_name,
        "addr": "{}:{}".format(to_host, to_port),
        "connector": {
            "type": to_protocol,
            "auth": {}
        }
    }
    if to_auth_username is not None and to_auth_password is not None:
        to_node["connector"]["auth"] = {
            "username": to_auth_username,
            "password": to_auth_password
        }
    else:
        del to_node["connector"]["auth"]
    # 5.2 构建转发器
    forwarder = {
        "nodes": [to_node],
    }
    # 5.3 构建服务
    service = {
        "name": service_name,
        "addr": "{}:{}".format(from_host, from_port),
        "handler": {
            "type": from_protocol,
            "auth": {}
        },
        "listener": {
            "type": "tcp",
        },
        # 与转发链模式不同的地方
        "forwarder": forwarder
    }
    if from_auth_username is not None and from_auth_password is not None:
        service["handler"]["auth"] = {
            "username": from_auth_username,
            "password": from_auth_password
        }
    else:
        del service["handler"]["auth"]
    # 6. 添加转发规则（只需要添加服务）
    if not gost_service.add(
            name=service["name"],
            addr=service["addr"],
            handler=service["handler"],
            listener=service["listener"],
            forwarder=service["forwarder"]):
        LOGGER.error("GOST 转发控制 -> 添加转发规则失败")
        return False
    # 7. 返回结果
    LOGGER.info("GOST 转发控制 -> 添加转发规则成功")
    return True

def delete_port_forward_service_without_chain(service_name: str = None):
    """
    @description: 删除端口转发服务（不涉及转发链，只需删除服务）
    """
    # 1. 检查 API 状态
    if not check_api_status():
        LOGGER.error("GOST 转发控制 -> API 状态异常，无法删除转发规则")
        return False
    # 2. 检查参数
    if not service_name:
        LOGGER.error("GOST 转发控制 -> 参数缺失，无法删除转发规则")
        return False
    # 3. 检查是否存在
    if not gost_service.is_exist(service_name):
        LOGGER.error("GOST 转发控制 -> 转发规则不存在，无法删除")
        return False
    # 4. 删除转发规则（只需要删除服务）
    if not gost_service.delete(service_name):
        LOGGER.error("GOST 转发控制 -> 删除转发规则失败")
        return False
    # 5. 返回结果
    LOGGER.info("GOST 转发控制 -> 删除转发规则成功")
    return True

def add_port_forward_service_with_chain(from_host: str,
                                        from_port: int,
                                        from_protocol: str,
                                        to_host: str,
                                        to_port: int,
                                        to_protocol: str,
                                        base_name: str = None,
                                        from_auth_username: str = None,
                                        from_auth_password: str = None,
                                        to_auth_username: str = None,
                                        to_auth_password: str = None):
    """
    @description: 添加端口转发服务（通过转发链，需要同时创建转发链）
    """
    # 1. 检查 API 状态
    if not check_api_status():
        LOGGER.error("GOST 转发控制 -> API 状态异常，无法添加转发规则")
        return False
    # 2. 检查参数
    if not from_host or not from_port or not from_protocol or not to_host or not to_port or not to_protocol:
        LOGGER.error("GOST 转发控制 -> 参数缺失，无法添加转发规则")
        return False
    # 3. 修改参数
    base_name = "port-forward-{}-{}-{}-to-{}-{}-{}".format(from_protocol, from_host, from_port, to_protocol, to_host, to_port) if not base_name else base_name
    service_name = base_name + "-service"
    chain_name = base_name + "-chain"
    hop_name = base_name + "-hop"
    node_name = base_name + "-node"
    # 4. 检查是否存在
    if gost_service.is_exist(service_name):
        LOGGER.error("GOST 转发控制 -> 转发规则已存在，无法添加")
        return False
    # 5. 构建转发规则
    # 5.1 构建节点
    to_node = {
        "name": node_name,
        "addr": "{}:{}".format(to_host, to_port),
        "connector": {
            "type": to_protocol,
            "auth": {}
        }
    }
    if to_auth_username is not None and to_auth_password is not None:
        to_node["connector"]["auth"] = {
            "username": to_auth_username,
            "password": to_auth_password
        }
    else:
        del to_node["connector"]["auth"]
    # 5.2 构建转发链
    chain = {
        "name": chain_name,
        "hops": [
            {
                "name": hop_name,
                "nodes": [to_node]
            }
        ]
    }
    # 5.3 构建服务
    service = {
        "name": service_name,
        "addr": "{}:{}".format(from_host, from_port),
        "handler": {
            "type": from_protocol,
            "auth": {},
            # 与非转发链模式不同的地方
            "chain": chain["name"]
        },
        "listener": {
            "type": "tcp",
        },
    }
    if from_auth_username is not None and from_auth_password is not None:
        service["handler"]["auth"] = {
            "username": from_auth_username,
            "password": from_auth_password
        }
    else:
        del service["handler"]["auth"]
    # 5. 添加转发规则
    # 5.1 添加转发链
    if not gost_chain.add(
            name=chain["name"],
            hops=chain["hops"]):
        LOGGER.error("GOST 转发控制 -> 添加转发链失败")
        return False
    # 5.2 添加服务
    if not gost_service.add(
            name=service["name"],
            addr=service["addr"],
            handler=service["handler"],
            listener=service["listener"],
            forwarder=None):
        LOGGER.error("GOST 转发控制 -> 添加转发规则失败")
        return False
    # 6. 返回结果
    LOGGER.info("GOST 转发控制 -> 添加转发规则成功")
    return True

def delete_port_forward_service_with_chain(service_name: str = None):
    """
    @description: 删除端口转发服务（涉及转发链，需要同时删除转发链）
    """
    # 1. 检查 API 状态
    if not check_api_status():
        LOGGER.error("GOST 转发控制 -> API 状态异常，无法删除转发规则")
        return False
    # 2. 检查参数
    if not service_name:
        LOGGER.error("GOST 转发控制 -> 参数缺失，无法删除转发规则")
        return False
    # 3. 检查是否存在
    if not gost_service.is_exist(service_name):
        LOGGER.error("GOST 转发控制 -> 转发规则不存在，无法删除")
        return False
    # 4. 删除转发规则
    service = gost_service.get(service_name)
    chain_name = service.get("handler", {}).get("chain")
    # 4.1 删除转发链
    if not gost_chain.delete(chain_name):
        LOGGER.error("GOST 转发控制 -> 删除转发链失败")
        return False
    # 4.2 删除服务
    if not gost_service.delete(service_name):
        LOGGER.error("GOST 转发控制 -> 删除转发规则失败")
        return False
    # 5. 返回结果
    LOGGER.info("GOST 转发控制 -> 删除转发规则成功")
    return True
