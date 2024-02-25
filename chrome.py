#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: ~/Projects/common/chrome.py
# @DATE: 2024/02/25 周日
# @TIME: 11:24:25
#
# @DESCRIPTION: Chrome 相关的共通方法


import os
from selenium import webdriver

from common.logger import CONFIG
from common.logger import LOGGER


class ChromeNetworkError(Exception):
    """
    @description: Chrome 网络错误异常
    """
    def __init__(self, network_error_message: str):
        self.network_error_message = network_error_message
        super().__init__(network_error_message)

class ChromeNginxError(Exception):
    """
    @description: Chrome Nginx 错误异常
    """
    def __init__(self, nginx_error_message: str):
        self.nginx_error_message = nginx_error_message
        super().__init__(nginx_error_message)


def connect_remote_chrome(selenium_remote_url: str, proxy_str: str = None):
    """
    @description: 连接远程 Chrome 浏览器
    @param {type} 
    @return: 
    """
    # 1. 设置 Chrome 选项
    chrome_options = webdriver.ChromeOptions()
    # 1.1 设置代理
    if proxy_str:
        chrome_options.add_argument("--proxy-server={}".format(proxy_str))
    # 1.2 设置无沙盒模式和禁用开发者模式
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # 1.3 设置分辨率为 1920x1080
    chrome_options.add_argument("--window-size=1920,1080")
    # 2. 连接远程 Chrome
    try:
        driver = webdriver.Remote(
            command_executor=selenium_remote_url,
            options=chrome_options
        )
        LOGGER.info("共通 Chrome -> 连接远程 Chrome 浏览器成功。")
    except Exception as e:
        LOGGER.error("共通 Chrome -> 连接远程 Chrome 浏览器失败！")
        LOGGER.error(e)
        return None
    # 3. 设置页面加载超时时间
    driver.set_page_load_timeout(30)
    # 4. 设置脚本执行超时时间
    driver.set_script_timeout(10)
    # 5. 返回 driver
    return driver

def check_is_network_error(driver):
    """
    @description: 检查是否是网络错误
    @param {type} 
    @return: 
    """
    # 1. 获取页面源码
    page_source = driver.page_source
    # 2. 判断是否是网络错误
    if ("ERR_PROXY_CONNECTION_FAILED" in page_source
            or "ERR_PROXY_AUTH_FAILED" in page_source
            or "ERR_CONNECTION_TIMED_OUT" in page_source
            or "ERR_CONNECTION_CLOSED" in page_source):
        return True
    # 3. 返回结果
    return False

def check_is_nginx_error(driver):
    """
    @description: 检查是否是 Nginx 错误（暂时没有特殊的意义）
    @param {type} 
    @return: 
    """
    # 1. 获取页面源码
    page_source = driver.page_source
    # 2. 判断是否是 Nginx 错误
    if ("502 Bad Gateway" in page_source
            or "503 Service Temporarily Unavailable" in page_source
            or "504 Gateway Time-out" in page_source
            or "nginx" in page_source.lower()):
        return True
    # 3. 返回结果
    return False

def save_snapshot(driver, snapshot_name: str):
    """
    @description: 保存截图
    @param {type} 
    @return: 
    """
    # 1. 获取配置中的快照存放地址
    snapshot_dir = CONFIG["chrome"]["snapshot_path"]
    if not snapshot_dir:
        snapshot_dir = "../snapshots/"
    # 2. 判断快照目录是否存在，不存在则创建
    if not os.path.exists(snapshot_dir):
        os.makedirs(snapshot_dir)
    # 3. 保存快照
    # 3.1 保存图片
    screenshot_path = os.path.join(snapshot_dir, snapshot_name + ".png")
    screenshot = driver.get_screenshot_as_png()
    with open(screenshot_path, "wb") as f:
        f.write(screenshot)
    LOGGER.info("共通 Chrome -> 快照截图保存成功：{}".format(screenshot_path))
    # 3.2 保存页面源码
    page_source_path = os.path.join(snapshot_dir, snapshot_name + ".html")
    with open(page_source_path, "w") as f:
        f.write(driver.page_source)
    LOGGER.info("共通 Chrome -> 快照页面源码保存成功：{}".format(page_source_path))
    # 4. 返回结果
    return screenshot_path, page_source_path