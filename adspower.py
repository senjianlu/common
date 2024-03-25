#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: common/adspower.py
# @DATE: 2024/03/24
# @TIME: 16:51:32
#
# @DESCRIPTION: todo...


import requests

from common.config import CONFIG
from common.logger import LOGGER


# 全局变量
ADSPOWER_HOST = CONFIG["adspower"]["host"]
ADSPOWER_API_URL = CONFIG["adspower"]["url"]


def check_api_status():
    """
    检查 Ads Power API 状态
    """
    # 1. 检查配置文件
    if not ADSPOWER_API_URL:
        LOGGER.error("AdsPower 指纹浏览器 -> 配置文件中 AdsPower URL 为空")
        return False
    # 2. 请求接口
    url = "{}/{}".format(ADSPOWER_API_URL, "status")
    try:
        response = requests.get(url)
        response_json = response.json()
    except Exception as e:
        LOGGER.error("AdsPower 指纹浏览器 -> API 检查状态出错: {}".format(e))
        return False
    # 3. 检验返回值
    if response.status_code != 200:
        LOGGER.error("AdsPower 指纹浏览器 -> API 检查状态失败，状态码: {}".format(response.status_code))
        return False
    if "msg" not in response_json or str(response_json["msg"]).lower() != "success":
        LOGGER.error("AdsPower 指纹浏览器 -> API 检查状态失败，msg 字段不存在或不为 success")
        return False
    # 4. 其他情况
    LOGGER.info("AdsPower 指纹浏览器 -> API 状态正常")
    return True

def start_browser(user_id: str = None,
                  serial_number: str = None,
                  is_open_tabs: bool = False,
                  is_open_ip_tab: bool = False,
                  is_new_first_tab: bool = False,
                  launch_args: list = [],
                  is_headless: bool = False,
                  is_disable_password_filling: bool = True,
                  is_clear_cache_after_closing: bool = True,
                  is_enable_password_saving: bool = False):
    """
    启动 AdsPower 浏览器
    """
    # 1. 检查 Ads Power API 状态
    if not check_api_status():
        LOGGER.error("AdsPower 指纹浏览器 -> 启动浏览器失败，Ads Power API 状态异常")
        return False
    # 2. 请求接口
    url = "{}/{}".format(ADSPOWER_API_URL, "api/v1/browser/start")
    params = {
        "user_id": user_id if user_id else "",
        "serial_number": serial_number if serial_number else "",
        "open_tabs": 0 if is_open_tabs else 1,
        "ip_tab": 1 if is_open_ip_tab else 0,
        "new_first_tab": 1 if is_new_first_tab else 0,
        "launch_args": launch_args,
        "headless": 1 if is_headless else 0,
        "disable_password_filling": 1 if is_disable_password_filling else 0,
        "clear_cache_after_closing": 1 if is_clear_cache_after_closing else 0,
        "enable_password_saving": 1 if is_enable_password_saving else 0
    }
    try:
        response = requests.get(url, params=params)
        response_json = response.json()
    except Exception as e:
        LOGGER.error("AdsPower 指纹浏览器 -> 启动浏览器出错: {}".format(e))
        return False
    # 3. 检验返回值
    if response.status_code != 200:
        LOGGER.error("AdsPower 指纹浏览器 -> 启动浏览器失败，状态码: {}".format(response.status_code))
        return False
    if "msg" not in response_json or str(response_json["msg"]).lower() != "success":
        LOGGER.error("AdsPower 指纹浏览器 -> 启动浏览器失败，msg 字段不存在或不为 success")
        return False
    if "data" not in response_json or not response_json["data"]:
        LOGGER.error("AdsPower 指纹浏览器 -> 启动浏览器失败，data 字段不存在或为空")
        return False
    # 4. 返回结果
    LOGGER.info("AdsPower 指纹浏览器 -> 启动浏览器成功")
    return True

def stop_browser(user_id: str = None,
                 serial_number: str = None):
    """
    停止 Ads Power 浏览器
    """
    # 1. 检查 Ads Power API 状态
    if not check_api_status():
        LOGGER.error("AdsPower 指纹浏览器 -> 停止浏览器失败，Ads Power API 状态异常")
        return False
    # 2. 请求接口
    url = "{}/{}".format(ADSPOWER_API_URL, "api/v1/browser/stop")
    params = {
        "user_id": user_id if user_id else "",
        "serial_number": serial_number if serial_number else ""
    }
    try:
        response = requests.get(url, params=params)
        response_json = response.json()
    except Exception as e:
        LOGGER.error("AdsPower 指纹浏览器 -> 停止浏览器出错: {}".format(e))
        return False
    # 3. 检验返回值
    if response.status_code != 200:
        LOGGER.error("AdsPower 指纹浏览器 -> 停止浏览器失败，状态码: {}".format(response.status_code))
        return False
    if "msg" not in response_json or str(response_json["msg"]).lower() != "success":
        LOGGER.error("AdsPower 指纹浏览器 -> 停止浏览器失败，msg 字段不存在或不为 success")
        return False
    # 4. 返回结果
    LOGGER.info("AdsPower 指纹浏览器 -> 停止浏览器成功")
    return True

def get_browser_status(user_id: str = None,
                       serial_number: str = None):
    """
    获取浏览器的状态
    """
    # 1. 检查 Ads Power API 状态
    if not check_api_status():
        LOGGER.error("AdsPower 指纹浏览器 -> 获取浏览器状态失败，Ads Power API 状态异常")
        return None
    # 2. 请求接口
    url = "{}/{}".format(CONFIG["adspower"]["url"], "api/v1/browser/active")
    params = {
        "user_id": user_id if user_id else "",
        "serial_number": serial_number if serial_number else ""
    }
    try:
        response = requests.get(url, params=params)
        response_json = response.json()
    except Exception as e:
        LOGGER.error("AdsPower 指纹浏览器 -> 获取浏览器状态出错: {}".format(e))
        return None
    # 2. 检验返回值
    if response.status_code != 200:
        LOGGER.error("AdsPower 指纹浏览器 -> 获取浏览器状态失败，状态码: {}".format(response.status_code))
        return None
    if "msg" not in response_json or str(response_json["msg"]).lower() != "success":
        LOGGER.error("AdsPower 指纹浏览器 -> 获取浏览器状态失败，msg 字段不存在或不为 success")
        return None
    if "data" not in response_json or not response_json["data"]:
        LOGGER.error("AdsPower 指纹浏览器 -> 获取浏览器状态失败，data 字段不存在或为空")
        return None
    # 3. 返回结果
    LOGGER.info("AdsPower 指纹浏览器 -> 获取浏览器状态成功：{}".format(response_json["data"]))
    return response_json["data"]

def is_browser_active(user_id: str = None,
                      serial_number: str = None):
    """
    判断浏览器是否处于激活状态
    """
    # 1. 获取浏览器状态
    browser_status = get_browser_status(user_id=user_id, serial_number=serial_number)
    # 2. 判断状态
    if not browser_status or "status" not in browser_status or browser_status["status"] != "Active":
        return False
    return True