#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: app/common/logic/gost_config.py
# @DATE: 2024/03/22
# @TIME: 22:10:45
#
# @DESCRIPTION: 配置文件逻辑


from common.config import CONFIG
from common.logger import LOGGER
from common.logic import gost_requests


def get_config():
    """
    @description: 获取 GOST 配置
    """
    # 1. 请求
    response_json = gost_requests.get("api/config")
    # 2. 检验返回值
    if not response_json:
        LOGGER.error("GOST 配置 -> 获取配置失败")
        return None
    if "api" not in response_json or not response_json["api"]:
        LOGGER.error("GOST 配置 -> 获取配置失败，api 字段不存在或为空")
        return None
    # 3. 返回结果
    return response_json