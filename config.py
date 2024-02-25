#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: ~/Projects/common/config.py
# @DATE: 2024/02/25 周日
# @TIME: 11:24:34
#
# @DESCRIPTION: 共通配置文件


import toml


# 项目根目录下的配置文件
CONFIG = {}
CONFIG_FILE_PATH = ""
try:
    CONFIG = toml.load("../config.toml")
    CONFIG_FILE_PATH = "../config.toml"
except Exception as e:
    CONFIG = toml.load("config.toml")
    CONFIG_FILE_PATH = "config.toml"


def reload():
    """
    重新加载配置文件
    """
    global CONFIG
    try:
        CONFIG = toml.load("../config.toml")
        CONFIG_FILE_PATH = "../config.toml"
    except Exception:
        CONFIG = toml.load("config.toml")
        CONFIG_FILE_PATH = "config.toml"
