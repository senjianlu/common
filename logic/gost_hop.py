#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: app/common/logic/gost_hop.py
# @DATE: 2024/03/23
# @TIME: 14:34:16
#
# @DESCRIPTION: GOST 跳跃点逻辑
#   文档：https://gost.run/concepts/hop/


from common.logger import LOGGER
from common.logic import gost_requests
from common.logic import gost_config


def is_exist(name: str) -> bool:
    """
    @description: 检查跳跃点是否存在
    :param name: 跳跃点名称
    :return: 是否存在
    """
    # 1. 获取全部配置
    config = gost_config.get_config()
    if not config:
        LOGGER.error("GOST Hop 存在判断 -> 获取配置失败")
        return False
    # 2. 获取跳跃点列表
    services = config.get("hops", []) or []
    # 3. 检查跳跃点是否存在
    for service in services:
        if service.get("name") == name:
            return True
    return False

def add(name: str,
        nodes: list):
    """
    @description: 添加跳跃点
    """
    # 1. 检查参数
    if not name:
        LOGGER.error("GOST Hop 新增 -> 跳跃点名称不能为空")
        return False
    if not nodes:
        LOGGER.error("GOST Hop 新增 -> 节点列表不能为空")
        return False
    # 2. 检查跳跃点是否存在
    if is_exist(name):
        LOGGER.error("GOST Hop 新增 -> 跳跃点已存在，无法添加")
        return False
    # 3. 构建跳跃点
    hop = {
        "name": name,
        "nodes": nodes
    }
    # 4. 添加跳跃点
    response_json = gost_requests.post("api/config/hops", data=hop)
    # 5. 检验返回值
    if not response_json:
        LOGGER.error("GOST Hop 新增 -> 添加跳跃点失败")
        return False
    # 6. 返回结果
    return True

def update(name: str,
              nodes: list):
     """
     @description: 更新跳跃点
     """
     # 1. 检查参数
     if not name:
          LOGGER.error("GOST Hop 更新 -> 跳跃点名称不能为空")
          return False
     if not nodes:
          LOGGER.error("GOST Hop 更新 -> 节点列表不能为空")
          return False
     # 2. 检查跳跃点是否存在
     if not is_exist(name):
          LOGGER.error("GOST Hop 更新 -> 跳跃点不存在，无法更新")
          return False
     # 3. 构建跳跃点
     hop = {
          "name": name,
          "nodes": nodes
     }
     # 4. 更新跳跃点
     response_json = gost_requests.put("api/config/hops/{}".format(name), data=hop)
     # 5. 检验返回值
     if not response_json:
          LOGGER.error("GOST Hop 更新 -> 更新跳跃点失败")
          return False
     # 6. 返回结果
     return True

def delete(name: str):
    """
    @description: 删除跳跃点
    """
    # 1. 检查跳跃点是否存在
    if not is_exist(name):
        LOGGER.error("GOST Hop 删除 -> 跳跃点不存在，无法删除")
        return False
    # 2. 删除跳跃点
    response_json = gost_requests.delete("api/config/hops/{}".format(name))
    # 3. 检验返回值
    if not response_json:
        LOGGER.error("GOST Hop 删除 -> 删除跳跃点失败")
        return False
    # 4. 返回结果
    return True
