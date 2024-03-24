#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: app/common/logic/gost_requests.py
# @DATE: 2024/03/22
# @TIME: 22:14:05
#
# @DESCRIPTION: GOST 请求封装


import json
import requests

from common.config import CONFIG
from common.logger import LOGGER


# 全局变量
# 基础配置
GOST_API_URL = CONFIG["gost"]["url"]
GOST_AUTH_USERNAME = CONFIG["gost"]["auth_username"]
GOST_AUTH_PASSWORD = CONFIG["gost"]["auth_password"]
# 是否已经通知过没有 AUTH 信息
IS_NOTIFIED_NO_AUTH = False


def get(uri_path: str, params: dict = None) -> dict:
    """
    @description: GET 请求
    :param uri_path: URI 路径
    :param params: 请求参数
    :return: 返回结果
    """
    # 1. 检查配置
    if not GOST_API_URL:
        LOGGER.error("GOST 请求 -> 配置文件中 GOST URL 为空")
        return None
    if not GOST_AUTH_USERNAME or not GOST_AUTH_PASSWORD:
        global IS_NOTIFIED_NO_AUTH
        if not IS_NOTIFIED_NO_AUTH:
            LOGGER.warning("GOST 请求 -> 配置文件中 GOST 用户名或密码为空，将不会进行认证")
            IS_NOTIFIED_NO_AUTH = True
    # 2. 请求
    url = "{}/{}".format(GOST_API_URL, uri_path)
    auth = (GOST_AUTH_USERNAME, GOST_AUTH_PASSWORD)
    try:
        response = requests.get(url, auth=auth, params=params)
        response_json = response.json()
    except Exception as e:
        LOGGER.error("GOST 请求 -> GET 请求出错: {}".format(e))
        return None
    # 3. 检验返回值
    if response.status_code != 200:
        LOGGER.error("GOST 请求 -> GET 请求失败，状态码: {}".format(response.status_code))
        LOGGER.error("GOST 请求 -> GET 请求失败，响应内容: {}".format(response.text))
        return None
    # 4. 返回结果
    return response_json

def post(uri_path: str, data: dict = None) -> dict:
    """
    @description: POST 请求
    :param uri_path: URI 路径
    :param data: 请求数据
    :return: 返回结果
    """
    # 1. 检查配置
    if not GOST_API_URL:
        LOGGER.error("GOST 请求 -> 配置文件中 GOST URL 为空")
        return None
    if not GOST_AUTH_USERNAME or not GOST_AUTH_PASSWORD:
        global IS_NOTIFIED_NO_AUTH
        if not IS_NOTIFIED_NO_AUTH:
            LOGGER.warning("GOST 请求 -> 配置文件中 GOST 用户名或密码为空，将不会进行认证")
            IS_NOTIFIED_NO_AUTH = True
    # 2. 请求
    url = "{}/{}".format(GOST_API_URL, uri_path)
    auth = (GOST_AUTH_USERNAME, GOST_AUTH_PASSWORD)
    try:
        response = requests.post(url, auth=auth, data=json.dumps(data) if type(data) == dict else data)
        response_json = response.json()
    except Exception as e:
        LOGGER.error("GOST 请求 -> POST 请求出错: {}".format(e))
        return None
    # 3. 检验返回值
    if response.status_code != 200:
        LOGGER.error("GOST 请求 -> POST 请求失败，状态码: {}".format(response.status_code))
        LOGGER.error("GOST 请求 -> POST 请求失败，响应内容: {}".format(response.text))
        return None
    # 4. 返回结果
    return response_json

def put(uri_path: str, data: dict = None) -> dict:
    """
    @description: PUT 请求
    :param uri_path: URI 路径
    :param data: 请求数据
    :return: 返回结果
    """
    # 1. 检查配置
    if not GOST_API_URL:
        LOGGER.error("GOST 请求 -> 配置文件中 GOST URL 为空")
        return None
    if not GOST_AUTH_USERNAME or not GOST_AUTH_PASSWORD:
        global IS_NOTIFIED_NO_AUTH
        if not IS_NOTIFIED_NO_AUTH:
            LOGGER.warning("GOST 请求 -> 配置文件中 GOST 用户名或密码为空，将不会进行认证")
            IS_NOTIFIED_NO_AUTH = True
    # 2. 请求
    url = "{}/{}".format(GOST_API_URL, uri_path)
    auth = (GOST_AUTH_USERNAME, GOST_AUTH_PASSWORD)
    try:
        response = requests.put(url, auth=auth, data=json.dumps(data) if type(data) == dict else data)
        response_json = response.json()
    except Exception as e:
        LOGGER.error("GOST 请求 -> PUT 请求出错: {}".format(e))
        return None
    # 3. 检验返回值
    if response.status_code != 200:
        LOGGER.error("GOST 请求 -> PUT 请求失败，状态码: {}".format(response.status_code))
        LOGGER.error("GOST 请求 -> PUT 请求失败，响应内容: {}".format(response.text))
        return None
    # 4. 返回结果
    return response_json

def delete(uri_path: str) -> dict:
    """
    @description: DELETE 请求
    :param uri_path: URI 路径
    :return: 返回结果
    """
    # 1. 检查配置
    if not GOST_API_URL:
        LOGGER.error("GOST 请求 -> 配置文件中 GOST URL 为空")
        return None
    if not GOST_AUTH_USERNAME or not GOST_AUTH_PASSWORD:
        global IS_NOTIFIED_NO_AUTH
        if not IS_NOTIFIED_NO_AUTH:
            LOGGER.warning("GOST 请求 -> 配置文件中 GOST 用户名或密码为空，将不会进行认证")
            IS_NOTIFIED_NO_AUTH = True
    # 2. 请求
    url = "{}/{}".format(GOST_API_URL, uri_path)
    auth = (GOST_AUTH_USERNAME, GOST_AUTH_PASSWORD)
    try:
        response = requests.delete(url, auth=auth)
        response_json = response.json()
    except Exception as e:
        LOGGER.error("GOST 请求 -> DELETE 请求出错: {}".format(e))
        return None
    # 3. 检验返回值
    if response.status_code != 200:
        LOGGER.error("GOST 请求 -> DELETE 请求失败，状态码: {}".format(response.status_code))
        LOGGER.error("GOST 请求 -> DELETE 请求失败，响应内容: {}".format(response.text))
        return None
    # 4. 返回结果
    return response_json