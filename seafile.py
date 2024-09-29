#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: common/rpc.py
# @DATE: 2024/09/03
# @TIME: 10:40:36
#
# @DESCRIPTION: Seaflie 模块


import re
import requests

from common.logger import LOGGER


def download(url, password: str = None):
    """
    @description: 下载 Seafile 文件
    :param password: 密码
    :return: 下载结果
    """
    # 1. 访问 URL 获取 sfcsrftoken、csrfmiddlewaretoken 和 token
    try:
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("请求失败，状态码：" + str(response.status_code))
        # 1.1 使用正则 "Set-Cookie: sfcsrftoken=(.*);" 提取 sfcsrftoken
        sfcsrftoken = re.findall("Set-Cookie: sfcsrftoken=(.*);", response.text)[0]
        # 1.2 使用正则 '<input type="hidden" name="csrfmiddlewaretoken" value="(.*)"' 提取 csrfmiddlewaretoken
        csrfmiddlewaretoken = re.findall('<input type="hidden" name="csrfmiddlewaretoken" value="(.*)"', response.text)[0]
        # 1.3 使用正则 '<input type="hidden" name="token" value="(.*)"'
        token = re.findall('<input type="hidden" name="token" value="(.*)"', response.text)[0]
    except Exception as e:
        LOGGER.error("共通 Seafile -> 文件下载失败，第一次请求失败！")
        LOGGER.error("共通 Seafile -> " + str(e))
        return None
    print(sfcsrftoken, csrfmiddlewaretoken, token)
    # 2. 发送 POST 请求以获得 sessionid
    data = "csrfmiddlewaretoken={}&token={}&password={}".format(csrfmiddlewaretoken, token, password)
    header_cookie = "sfcsrftoken={}".format(sfcsrftoken)
    header_content_type = "Content-Type: application/x-www-form-urlencoded"
    headers = {
        "Cookie": header_cookie,
        "Content-Type": header_content_type
    }
    try:
        response = requests.post(url, data=data, headers=headers)
        if response.status_code != 200:
            raise Exception("请求失败，状态码：" + str(response.status_code))
        # 使用正则 'sessionid=(.*);' 提取 sessionid
        sessionid = re.findall("sessionid=(.*);", response.text)[0]
    except Exception as e:
        LOGGER.error("共通 Seafile -> 文件下载失败，第二次请求失败！")
        LOGGER.error("共通 Seafile -> " + str(e))
        return None
    print(sessionid)