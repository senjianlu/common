#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: common/anonymous.py
# @DATE: 2024/03/24
# @TIME: 16:49:08
#
# @DESCRIPTION: 匿名函数


from common.logic import anonymous_user_agent

def get_random_user_agent():
    """
    @description: 获取随机的 User-Agent
    """
    return anonymous_user_agent.get_random_user_agent()
