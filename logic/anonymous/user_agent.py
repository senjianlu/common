#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: common/logic/anonymous/user_agent.py
# @DATE: 2024/11/01
# @TIME: 16:56:58
#
# @DESCRIPTION: 共通 - Anonymous 匿名模块 - User Agent 逻辑


import requests
from enum import Enum
from bs4 import BeautifulSoup


# useragents.me 网站地址
USER_AGENTS_ME_URL = "https://www.useragents.me/"
# 各平台的 User Agents
PLATFORM_2_USER_AGENTS = {}


# 平台枚举
class PLATFORM(Enum):
    """
    @description: 平台
    """
    PC = "PC"
    MOBILE = "Mobile"


# User Agent 类
class UserAgent:
    """
    @description: User Agent 类
    """
    def __init__(self, platform: str, user_agent: str):
        self.platform = platform
        self.user_agent = user_agent


def _init_from_web() -> list:
    """
    @description: 从网站初始化 User Agents
    @param {type}
    @return:
    """
    # 1. 请求网站
    try:
        response = requests.get(USER_AGENTS_ME_URL)
        response.raise_for_status()
    except Exception as e:
        print("请求 UserAgents.me 出错！错误信息：{}".format(e))
        return []
    # 2. 解析 User Agents
    user_agents = []
    soup = BeautifulSoup(response.text, "html.parser")
    # 2.1 最常见的桌面浏览器 User Agents(#most-common-desktop-useragents-json-csv/div/textarea)
    desktop_user_agents = soup.find("div", id="most-common-desktop-useragents-json-csv").find("textarea").text

def _init_from_local() -> list:
    """
    @description: 从本地初始化 User Agents
    @param {type}
    @return:
    """
    pass

def _init_from_db() -> list:
    """
    @description: 从数据库初始化 User Agents
    @param {type}
    @return:
    """
    pass

def _save_to_local(user_agents: list) -> bool:
    """
    @description: 保存 User Agents 到本地
    @param {type}
    user_agents: User Agents 列表
    @return: 是否保存成功
    """
    pass

def _save_to_db(user_agents: list) -> bool:
    """
    @description: 保存 User Agents 到数据库
    @param {type}
    user_agents: User Agents 列表
    @return: 是否保存成功
    """
    pass

def get_random_user_agent(platform: str = PLATFORM.PC) -> str:
    """
    @description: 获取随机的 User Agent
    @param {type}
    @return: 随机 User Agent
    """
    pass

if __name__ == "__main__":
    _init_from_web()
