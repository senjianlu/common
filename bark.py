#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: common/bark.py
# @DATE: 2024/03/25
# @TIME: 14:40:02
#
# @DESCRIPTION: Bark APP 通知模块


import requests

from common.config import CONFIG
from common.logger import LOGGER


def send_message(server_host: str = CONFIG["bark"]["url"],
                 key: str = CONFIG["bark"]["key"],
                 title: str = "",
                 content: str = None,
                 group: str = None,
                 url: str = None,
                 icon: str = None):
    """
    @description: 发送消息
    :param title:
    :param content:
    :param group:
    :param url:
    :param icon:
    :return:
    """
    # 1. 请求参数
    # 1.1 url
    _url = "{}/{}/{}".format(server_host, key, title)
    if content is not None:
        _url = "{}/{}".format(_url, content)
    # 1.2 params
    params = {
        "group": group,
        "url": url,
        "icon": icon
    }
    # 2. 发送请求
    try:
        response = requests.get(_url, params=params, timeout=5)
        response_json = response.json()
        print(response_json)
    except Exception as e:
        LOGGER.error("Bark 发送消息 -> 请求出错，错误信息：{}".format(e))
        return False
    # 3. 验证响应
    if response.status_code != 200:
        LOGGER.error("Bark 发送消息 -> 请求失败，响应码：{}".format(response.status_code))
        return False
    # 4. 返回结果
    return True