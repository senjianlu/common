#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: common/rpc.py
# @DATE: 2024/09/03
# @TIME: 10:40:36
#
# @DESCRIPTION: Seaflie 模块


import requests
from bs4 import BeautifulSoup

from common.logger import LOGGER


# 文件下载路径
DOWNLOAD_PATH = "tmp/"


def download(url, file_name, password: str = None) -> str:
    """
    @description: 下载 Seafile 文件
    @param url: 文件 URL
    @param file_name: 文件名
    @param password: 文件密码
    @return: 文件路径
    """
    # 1. 修正 url
    if url.strip().endswith("?dl=1"):
        url = url.strip().rstrip("?dl=1")
    print(url)
    # 2. 访问 URL 获取 sfcsrftoken、csrfmiddlewaretoken 和 token
    try:
        sessoin = requests.Session()
        response = sessoin.get(url)
        if response.status_code != 200:
            raise Exception("请求失败，状态码：" + str(response.status_code))
        # 2.1 使用正则 "Set-Cookie: sfcsrftoken=(.*);" 提取 sfcsrftoken
        # > 由 session 保持，不需要提取
        # if ("Set-Cookie" in response.headers) is False:
        #     LOGGER.error("共通 Seafile -> 文件下载失败，第一次请求失败！")
        #     LOGGER.error("共通 Seafile -> 请求头中没有 Set-Cookie")
        # sfcsrftoken = re.findall("sfcsrftoken=(.*?);", response.headers["Set-Cookie"])[0]
        # 2.2 将 HTML 转为 BeautifulSoup 对象
        soup = BeautifulSoup(response.text, "html.parser")
        # 2.3 获取 name = "csrfmiddlewaretoken" 的 input 标签的 value
        csrfmiddlewaretoken = soup.find("input", {"name": "csrfmiddlewaretoken"})["value"]
        # 2.3 获取 name = "token" 的 input 标签的 value
        token = soup.find("input", {"name": "token"})["value"]
    except Exception as e:
        LOGGER.error("共通 Seafile -> 文件下载失败，第一次请求失败！")
        LOGGER.error("共通 Seafile -> " + str(e))
        return None
    # 3. 发送 POST 请求以获得 sessionid
    data = "csrfmiddlewaretoken={}&token={}&password={}".format(csrfmiddlewaretoken, token, password)
    # header_cookie = "sfcsrftoken={}".format(sfcsrftoken)
    # > 由 session 保持，不需要设置
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": url,
    }
    try:
        response = sessoin.post(url, data=data, headers=headers)
        if response.status_code != 200:
            raise Exception("请求失败，状态码：" + str(response.status_code))
        # 使用正则 'sessionid=(.*);' 提取 sessionid
        # > 由 session 保持，不需要提取
        # if ("Set-Cookie" in response.headers) is False:
        #     print("共通 Seafile -> 文件下载失败，第二次请求失败！")
        #     print("共通 Seafile -> 请求头中没有 Set-Cookie")
        # sessionid = re.findall("sessionid=(.*?);", response.headers["Set-Cookie"])[0]
    except Exception as e:
        LOGGER.error("共通 Seafile -> 文件下载失败，第二次请求失败！")
        LOGGER.error("共通 Seafile -> " + str(e))
        return None
    # 4. 发送 GET 请求以下载文件
    file_download_url = url.rstrip("/") + "/?dl=1"
    LOGGER.info("共通 Seafile -> 文件下载地址：" + file_download_url)
    # 下载到 ../tmp/ 目录下
    try:
        response = sessoin.get(file_download_url)
        if response.status_code != 200:
            raise Exception("请求失败，状态码：" + str(response.status_code))
        with open(DOWNLOAD_PATH + file_name, "wb") as file:
            file.write(response.content)
    except Exception as e:
        LOGGER.error("共通 Seafile -> 文件下载失败，第三次请求失败！")
        LOGGER.error("共通 Seafile -> " + str(e))
        return None
    # 5. 返回文件路径
    return DOWNLOAD_PATH + file_name
