#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: ~/Projects/common/logger.py
# @DATE: 2024/02/25 周日
# @TIME: 11:24:43
#
# @DESCRIPTION: 日志模块


import os
import logging
from datetime import datetime

from common.config import CONFIG


# 获取 logger
LOGGER = logging.getLogger(__name__)
# 日志格式
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
# 日志级别
LOG_LEVEL_STR = CONFIG["log"]["level"]
LOG_LEVEL = logging.INFO
if LOG_LEVEL_STR == "DEBUG":
    LOG_LEVEL = logging.DEBUG
elif LOG_LEVEL_STR == "INFO":
    LOG_LEVEL = logging.INFO
elif LOG_LEVEL_STR == "WARNING":
    LOG_LEVEL = logging.WARNING
elif LOG_LEVEL_STR == "ERROR":
    LOG_LEVEL = logging.ERROR
elif LOG_LEVEL_STR == "CRITICAL":
    LOG_LEVEL = logging.CRITICAL
# 日志文件夹路径
LOG_DIR_PATH = "../" + CONFIG["log"]["dir_path"]
# 如果日志文件夹不存在则创建
if not os.path.exists(LOG_DIR_PATH):
    os.makedirs(LOG_DIR_PATH)
# 基础配置
logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    datefmt="%Y-%m-%d %H:%M:%S"
)


def get_logger():
    """
    @description: 获取 logger
    @param {type}:
    """
    # 1. 日志文件名为当日日期，格式为：年-月-日.log
    log_file_name = datetime.now().strftime("%Y-%m-%d") + ".log"
    # 2. 日志文件路径为：日志文件夹路径 + 日志文件名
    log_file_path = LOG_DIR_PATH + log_file_name
    # 3. 创建 logger
    logger = logging.getLogger(__name__)
    # 4. 设置日志级别
    logger.setLevel(LOG_LEVEL)
    # 5. 创建 handler
    handler = logging.FileHandler(log_file_path, encoding="utf-8")
    # 6. 创建 formatter
    formatter = logging.Formatter(LOG_FORMAT)
    # 7. 设置 formatter
    handler.setFormatter(formatter)
    # 8. 添加 handler
    logger.addHandler(handler)
    # 9. 返回 logger
    return logger


# 全局 logger
LOGGER = get_logger()


class CommonLogger:
    """
    @description: 共通日志类
    """
    def __init__(self):
        """
        @description: 构造函数
        @param {type}:
        """
        self.is_print_only = CONFIG["log"]["is_print_only"] if "is_print_only" in CONFIG["log"] else True
        self.logger = LOGGER

    def debug(self, msg: str):
        """
        @description: debug 日志
        @param {type} msg: 日志信息
        """
        if self.is_print_only:
            print(msg)
        else:
            self.logger.debug(msg)

    def info(self, msg: str):
        """
        @description: info 日志
        @param {type} msg: 日志信息
        """
        if self.is_print_only:
            print(msg)
        else:
            self.logger.info(msg)

    def warning(self, msg: str):
        """
        @description: warning 日志
        @param {type} msg: 日志信息
        """
        if self.is_print_only:
            print(msg)
        else:
            self.logger.warning(msg)

    def error(self, msg: str):
        """
        @description: error 日志
        @param {type} msg: 日志信息
        """
        if self.is_print_only:
            print(msg)
        else:
            self.logger.error(msg)

    def critical(self, msg: str):
        """
        @description: critical 日志
        @param {type} msg: 日志信息
        """
        if self.is_print_only:
            print(msg)
        else:
            self.logger.critical(msg)


COMMON_LOGGER = CommonLogger()


# 单体测试
if __name__ == "__main__":
    LOGGER.debug("debug")
    LOGGER.info("info")
    LOGGER.warning("warning")
    LOGGER.error("error")
    LOGGER.critical("critical")
