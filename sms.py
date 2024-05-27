#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: common/sms.py
# @DATE: 2024/05/20
# @TIME: 09:33:44
#
# @DESCRIPTION: 短信模块


import requests
from typing import List

from common.logger import COMMON_LOGGER as LOGGER
from common.config import CONFIG


class PrviderYezi():
    """
    @description: 椰子短信平台
    """
    def __init__(self,
                 host = CONFIG["sms"]["yezi"]["host"],
                 host_backup = CONFIG["sms"]["yezi"]["host_backup"],
                 username = CONFIG["sms"]["yezi"]["username"],
                 password = CONFIG["sms"]["yezi"]["password"]):
        """
        初始化
        """
        self.host = host
        self.host_backup = host_backup
        self.username = username
        self.password = password
        self.token = None

    def _request(self, movement = None, params = {}):
        """
        @description: 请求
        """
        # 1. 判断参数
        if (not self.host and not self.host_backup) and not self.username and not self.password:
            LOGGER.error("短信模块 -> 椰子短信平台登陆参数不完整！")
            return None
        # 2. 请求
        response = None
        for host in [self.host, self.host_backup]:
            url = host.rstrip("/") + "/api/" + movement
            try:
                response = requests.get(url, params=params)
                break
            except Exception as e:
                LOGGER.error(f"短信模块 -> 椰子短信平台请求失败：{e}")
        # 3. 判断
        # 3.1 判断响应
        if not response or response.status_code != 200:
            LOGGER.error("短信模块 -> 椰子短信平台请求失败，响应为空或状态码不为 200！")
            return None
        # 3.2 解析结果
        try:
            response_json = response.json()
        except Exception as e:
            LOGGER.error("短信模块 -> 椰子短信平台请求结果解析失败！")
            return None
        # 3.3 判断结果并返回
        if "message" in response_json and (response_json["message"].lower() == "ok" or response_json["message"] == "登录成功"):
            return response
        else:
            LOGGER.error("短信模块 -> 椰子短信平台请求失败，结果中的 message 为空或不为 OK！")
            LOGGER.error("短信模块 -> 响应：" + str(response_json))
            return None

    def login(self):
        """
        @description: 登录
        """
        # 1. 登录
        response = self._request("logins", {
            "username": self.username,
            "password": self.password
        })
        # 2. 设置 token
        if not response:
            LOGGER.error("短信模块 -> 椰子短信平台登录失败！")
            return False
        else:
            LOGGER.info("短信模块 -> 椰子短信平台登录成功！")
            self.token = response.json()["token"]
            return True

    def get_user_info(self):
        """
        @description: 获取用户信息
        """
        # 1. 获取用户信息
        response = self._request("get_myinfo", {
            "token": self.token
        })
        # 2. 返回结果
        return response.json()

    def get_phone_number(self, project_id = None, scope: int = None, scope_black: List = [], creat_time: int = None):
        """
        @description: 获取手机号
        """
        # 1. 参数判断
        if not project_id:
            LOGGER.error("短信模块 -> 椰子短信平台获取手机号失败，缺少项目 ID！")
            return None
        # 2. 获取手机号
        response = self._request("get_mobile", {
            "token": self.token,
            "project_id": project_id,
            "scope": scope if scope else "",
            "scope_black": ",".join(scope_black) if scope_black else "",
            "creat_time": creat_time if creat_time else ""
        })
        # 3. 返回结果
        return response.json() if response else None

    def get_message(self, project_id = None, phone_number: str = None):
        """
        @description: 获取短信
        """
        # 1. 参数判断
        if not project_id or not phone_number:
            LOGGER.error("短信模块 -> 椰子短信平台获取短信失败，缺少项目 ID 或手机号！")
            return None
        # 2. 获取短信
        response = self._request("get_message", {
            "token": self.token,
            "project_id": project_id,
            "phone_number": phone_number
        })
        # 3. 返回结果
        return response.json() if response else None

    def release_phone_number(self, project_id = None, phone_number: str = None):
        """
        @description: 释放手机号
        """
        # 1. 参数判断
        if not project_id or not phone_number:
            LOGGER.error("短信模块 -> 椰子短信平台释放手机号失败，缺少项目 ID 或手机号！")
            return None
        # 2. 释放手机号
        response = self._request("free_mobile", {
            "token": self.token,
            "project_id": project_id,
            "phone_number": phone_number
        })
        # 3. 返回结果
        return response.json() if response else None

    def shield_phone_number(self, project_id = None, phone_number: str = None):
        """
        @description: 屏蔽手机号
        """
        # 1. 参数判断
        if not project_id or not phone_number:
            LOGGER.error("短信模块 -> 椰子短信平台屏蔽手机号失败，缺少项目 ID 或手机号！")
            return None
        # 2. 屏蔽手机号
        response = self._request("add_blacklist", {
            "token": self.token,
            "project_id": project_id,
            "phone_number": phone_number
        })
        # 3. 返回结果
        return response.json() if response else None