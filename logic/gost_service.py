#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: app/common/logic/gost_service.py
# @DATE: 2024/03/22
# @TIME: 21:57:37
#
# @DESCRIPTION: GOST Service 相关逻辑
#   文档：https://gost.run/concepts/service/


from common.logger import LOGGER
from common.logic import gost_requests
from common.logic import gost_config


def is_exist(name: str) -> bool:
    """
    @description: 检查服务是否存在
    :param name: 服务名称
    :return: 是否存在
    """
    # 1. 获取全部配置
    config = gost_config.get_config()
    if not config:
        LOGGER.error("GOST Service 存在判断 -> 获取配置失败")
        return False
    # 2. 获取服务列表
    services = config.get("services", []) or []
    # 3. 检查服务是否存在
    for service in services:
        if service.get("name") == name:
            return True
    return False

def add(name: str,
        addr: str,
        handler: dict,
        listener: dict,
        forwarder: dict):
    """
    @description: 添加服务
    """
    # 1. 检查参数
    if not name:
        LOGGER.error("GOST Service 新增 -> 服务名称不能为空")
        return False
    if not addr:
        LOGGER.error("GOST Service 新增 -> 服务地址不能为空")
        return False
    # 2. 检查服务是否存在
    if is_exist(name):
        LOGGER.error("GOST Service 新增 -> 服务已存在，无法添加")
        return False
    # 3. 构建服务
    service = {
        "name": name,
        "addr": addr,
        "handler": handler,
        "listener": listener,
        "forwarder": forwarder
    }
    # 4. 添加服务
    response_json = gost_requests.post("api/config/services", data=service)
    # 5. 检验返回值
    if not response_json:
        LOGGER.error("GOST Service 新增 -> 添加服务失败")
        return False
    # 6. 返回结果
    return True

def update(name: str,
        addr: str,
        handler: dict,
        listener: dict,
        forwarder: dict):
    """
    @description: 修改服务
    """
    # 1. 检查参数
    if not name:
        LOGGER.error("GOST Service 修改 -> 服务名称不能为空")
        return False
    if not addr:
        LOGGER.error("GOST Service 修改 -> 服务地址不能为空")
        return False
    # 2. 检查服务是否存在
    if not is_exist(name):
        LOGGER.error("GOST Service 修改 -> 服务不存在，无法更新")
        return False
    # 3. 构建服务
    service = {
        "name": name,
        "addr": addr,
        "handler": handler,
        "listener": listener,
        "forwarder": forwarder
    }
    # 4. 修改服务
    response_json = gost_requests.put("api/config/services/{}".format(name), data=service)
    # 5. 检验返回值
    if not response_json:
        LOGGER.error("GOST Service 修改 -> 更新服务失败")
        return False
    # 6. 返回结果
    return True

def delete(name: str):
    """
    @description: 删除服务
    """
    # 1. 检查参数
    if not name:
        LOGGER.error("GOST Service 删除 -> 服务名称不能为空")
        return False
    # 2. 检查服务是否存在
    if not is_exist(name):
        LOGGER.error("GOST Service 删除 -> 服务不存在，无法删除")
        return False
    # 3. 删除服务
    response_json = gost_requests.delete("api/config/services/{}".format(name))
    # 4. 检验返回值
    if not response_json:
        LOGGER.error("GOST Service 删除 -> 删除服务失败")
        return False
    # 5. 返回结果
    return True

def delete_by_name_like(name_like: str):
    """
    @description: 删除服务
    """
    # 1. 检查参数
    if not name_like:
        LOGGER.error("GOST Service 删除 -> 服务名称不能为空")
        return False
    # 2. 获取全部配置
    config = gost_config.get_config()
    if not config:
        LOGGER.error("GOST Service 删除 -> 获取配置失败")
        return False
    # 3. 获取服务列表
    services = config.get("services", []) or []
    # 4. 删除服务
    for service in services:
        if name_like in service.get("name"):
            response_json = gost_requests.delete("api/config/services/{}".format(service.get("name")))
            if not response_json:
                LOGGER.error("GOST Service 删除 -> 删除服务失败")
                return False
    # 5. 返回结果
    return True