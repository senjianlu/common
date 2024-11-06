#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: app/common/logic/gost_chain.py
# @DATE: 2024/03/23
# @TIME: 14:27:24
#
# @DESCRIPTION: GOST 转发链逻辑
#   文档：https://gost.run/concepts/chain/


from common.logger import LOGGER
from common.logic import gost_requests
from common.logic import gost_config


def is_exist(name: str) -> bool:
    """
    @description: 检查转发链是否存在
    :param name: 转发链名称
    :return: 是否存在
    """
    # 1. 获取全部配置
    config = gost_config.get_config()
    if not config:
        LOGGER.error("GOST Chain 存在判断 -> 获取配置失败")
        return False
    # 2. 获取转发链列表
    services = config.get("chains", []) or []
    # 3. 检查转发链是否存在
    for service in services:
        if service.get("name") == name:
            return True
    return False

def add(name: str,
        hops: list):
    """
    @description: 添加转发链
    """
    # 1. 检查参数
    if not name:
        LOGGER.error("GOST Chain 新增 -> 转发链名称不能为空")
        return False
    if not hops:
        LOGGER.error("GOST Chain 新增 -> 跳跃点列表不能为空")
        return False
    # 2. 检查转发链是否存在
    if is_exist(name):
        LOGGER.error("GOST Chain 新增 -> 转发链已存在，无法添加")
        return False
    # 3. 构建转发链
    chain = {
        "name": name,
        "hops": hops
    }
    # 4. 添加转发链
    response_json = gost_requests.post("api/config/chains", data=chain)
    # 5. 检验返回值
    if not response_json:
        LOGGER.error("GOST Chain 新增 -> 添加转发链失败")
        return False
    # 6. 返回结果
    return True

def update(name: str,
           hops: list):
    """
    @description: 更新转发链
    """
    # 1. 检查参数
    if not name:
        LOGGER.error("GOST Chain 更新 -> 转发链名称不能为空")
        return False
    if not hops:
        LOGGER.error("GOST Chain 更新 -> 跳跃点列表不能为空")
        return False
    # 2. 检查转发链是否存在
    if not is_exist(name):
        LOGGER.error("GOST Chain 更新 -> 转发链不存在，无法更新")
        return False
    # 3. 构建转发链
    chain = {
        "name": name,
        "hops": hops
    }
    # 4. 更新转发链
    response_json = gost_requests.put("api/config/chains/{}".format(name), data=chain)
    # 5. 检验返回值
    if not response_json:
        LOGGER.error("GOST Chain 更新 -> 更新转发链失败")
        return False
    # 6. 返回结果
    return True

def delete(name: str):
    """
    @description: 删除转发链
    """
    # 1. 检查参数
    if not name:
        LOGGER.error("GOST Chain 删除 -> 转发链名称不能为空")
        return False
    # 2. 检查转发链是否存在
    if not is_exist(name):
        LOGGER.error("GOST Chain 删除 -> 转发链不存在，无法删除")
        return False
    # 3. 删除转发链
    response_json = gost_requests.delete("api/config/chains/{}".format(name))
    # 4. 检验返回值
    if not response_json:
        LOGGER.error("GOST Chain 删除 -> 删除转发链失败")
        return False
    # 5. 返回结果
    return True