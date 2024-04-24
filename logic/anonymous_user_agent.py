#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: common/logic/anonymous_user_agent.py
# @DATE: 2024/03/24
# @TIME: 16:36:58
#
# @DESCRIPTION: todo...


import random
from sqlalchemy import text

from common.logger import LOGGER
from common.Base import init_db


# User Agent 列表
USER_AGENTS = []


def init_user_agents():
    """
    @description: 初始化 User Agents
    @param {type}
    @return:
    """
    # 1. 连接数据库
    session = init_db()
    # 2. 查询所有 User Agents
    sql = """
        SELECT
            ua.user_agent
        FROM
            bd_user_agent AS ua
        """
    try:
        # 2.1 查询
        result = session.execute(text(sql)).fetchall()
        # 2.2 遍历结果并插入到全局变量中
        global USER_AGENTS
        USER_AGENTS = [item[0] for item in result]
        LOGGER.info("共通 Anonymous User Agent -> 初始化 User Agents 成功，共有 {} 条 User Agents".format(len(USER_AGENTS)))
    except Exception as e:
        LOGGER.error("共通 Anonymous User Agent -> 初始化 User Agents 出错！错误信息：{}".format(e))
    finally:
        session.close()
    return True

def get_random_user_agent():
    """
    @description: 获取随机 User Agent
    @param {type}
    @return: 随机 User Agent
    """
    if not USER_AGENTS:
        LOGGER.error("共通 Anonymous User Agent -> User Agents 为空！")
        return None
    return random.choice(USER_AGENTS)