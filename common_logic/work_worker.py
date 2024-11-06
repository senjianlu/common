#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: common/logic/work_worker.py
# @DATE: 2024/04/30
# @TIME: 23:34:36
#
# @DESCRIPTION: 工作工作者逻辑


from enum import Enum


class StatusEnum(Enum):
    """
    @description: 状态枚举
    """
    START = "START"
    RUNNING = "RUNNING"
    END = "END"
