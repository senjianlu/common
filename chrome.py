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
import platform
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from common.logger import CONFIG
from common.logger import LOGGER
from common import adspower
from common import gost
from common import proxy


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


def import_jquery(driver):
    """
    @description: 导入 jQuery
    """
    with open("common/resources/js/jquery.min.js", "r") as f:
        jquery_js = f.read()
    try:
        driver.execute_script(jquery_js)
    except Exception as e:
        LOGGER.error("共通 Chrome -> 导入 jQuery 失败！")
        LOGGER.error(e)
        return False
    LOGGER.info("共通 Chrome -> 导入 jQuery 成功。")
    return True

# def _get_stealth_js_content():
#     """
#     @description: 获取 Stealth.js 内容
#     """
#     with open("common/resources/js/stealth.min.js", "r") as f:
#         return f.read()

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
    # 1.4 防止被检测为 Selenium（在 79 版本之后不再生效）
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
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
    # 5. 防止被检测为 Selenium
    # js = _get_stealth_js_content()
    # driver.execute(
    #     driver_command="executeCdpCommand",
    #     params={
    #         "cmd": "Page.addScriptToEvaluateOnNewDocument",
    #         "params": {
    #             "source": js
    #         }
    #     }
    # )
    # 6. 返回 driver
    return driver

def connect_debug_chrome(debug_host: str = "localhost", debug_port: int = 9222, chrome_version: int = 122):
    """
    @description: 连接调试 Chrome 浏览器
    @param {type}
    @return:
    """
    # 1. 设置 Chrome 选项
    chrome_options = webdriver.ChromeOptions()
    # 1.1 设置调试地址
    chrome_options.add_experimental_option("debuggerAddress", "{}:{}".format(debug_host, debug_port))
    # 1.2 选择 chromedriver 版本
    chrome_service = None
    LOGGER.info("共通 Chrome -> 操作系统：{}".format(platform.system()))
    if platform.system() == "Linux":
        chrome_service = Service("common/resources/chromedriver/{}/linux".format(chrome_version))
    elif platform.system() == "Darwin":
        chrome_service = Service("common/resources/chromedriver/{}/macos".format(chrome_version))
    else:
        LOGGER.error("共通 Chrome -> 不支持的操作系统：{}".format(platform.system()))
        return None
    # 1.3 判断 chromedriver 是否存在
    if not os.path.exists(chrome_service.path):
        LOGGER.error("共通 Chrome -> chromedriver 不存在：{}".format(chrome_service.path))
        return None
    # 2. 连接调试 Chrome
    try:
        driver = webdriver.Chrome(
            service=chrome_service,
            options=chrome_options
        )
        LOGGER.info("共通 Chrome -> 连接调试 Chrome 浏览器成功。")
    except Exception as e:
        LOGGER.error("共通 Chrome -> 连接调试 Chrome 浏览器出错！")
        LOGGER.error(e)
        return None
    # 3. 设置页面加载超时时间
    driver.set_page_load_timeout(30)
    # 4. 设置脚本执行超时时间
    driver.set_script_timeout(10)
    # 5. 返回 driver
    return driver

def start_adspower_browser(user_id: str = None,
                           serial_number: str = None,
                           is_open_tabs: bool = False,
                           is_open_ip_tab: bool = False,
                           is_new_first_tab: bool = False,
                           launch_args: list = [],
                           is_headless: bool = False,
                           is_disable_password_filling: bool = True,
                           is_clear_cache_after_closing: bool = True,
                           is_enable_password_saving: bool = False,
                           proxy_str: str = None):
    """
    @description: 启动 Ads Power 浏览器
    @param {type}
    @return:
    """
    # 1. 设置变量
    adspower_host = adspower.ADSPOWER_HOST
    adspower_browser_debug_host = "127.0.0.1"
    adspower_browser_debug_port = None
    adspower_browser_debug_protocol = "tcp"
    adspower_browser_forwarded_debug_host = "0.0.0.0"
    adspower_browser_forwarded_debug_port = 14080 + int(serial_number)
    adspower_browser_forwarded_debug_protocol = "tcp"
    adspower_browser_proxy_host = "127.0.0.1"
    adspower_browser_proxy_port = 13080 + int(serial_number)
    adspower_browser_proxy_protocol = "socks5"
    # 2. 检测浏览器状态
    browser_status = adspower.get_browser_status(user_id=user_id, serial_number=serial_number)
    if not browser_status:
        LOGGER.error("共通 Chrome -> 获取 Ads Power 浏览器状态失败")
        return None
    if "status" in browser_status and browser_status["status"] == "Active":
        LOGGER.info("共通 Chrome -> Ads Power 浏览器已经启动，如有需要请关闭后再启动")
        return None
    # 3. 设置代理转发
    # 3.1 删除之前的代理转发
    proxy_port_forward_service_list = gost.get_port_forward_service_list(
        from_host=adspower_browser_proxy_host, from_port=adspower_browser_proxy_port)
    for proxy_port_forward_service in proxy_port_forward_service_list:
        gost.delete_port_forward_service_with_chain(proxy_port_forward_service["name"])
    # 3.2 添加新的代理转发
    proxy_host, proxy_port, proxy_protocol, proxy_username, proxy_password = proxy.parse_proxy_str(proxy_str)
    is_proxy_service_added = gost.add_port_forward_service_with_chain(
        from_host=adspower_browser_proxy_host,
        from_port=adspower_browser_proxy_port,
        from_protocol=adspower_browser_proxy_protocol,
        to_host=proxy_host,
        to_port=proxy_port,
        to_protocol=proxy_protocol,
        to_auth_username=proxy_username,
        to_auth_password=proxy_password
    )
    if not is_proxy_service_added:
        LOGGER.error("共通 Chrome -> 添加代理转发失败")
        return None
    # 4. 启动浏览器
    is_browser_started = adspower.start_browser(
        user_id=user_id,
        serial_number=serial_number,
        is_open_tabs=is_open_tabs,
        is_open_ip_tab=is_open_ip_tab,
        is_new_first_tab=is_new_first_tab,
        launch_args=launch_args,
        is_headless=is_headless,
        is_disable_password_filling=is_disable_password_filling,
        is_clear_cache_after_closing=is_clear_cache_after_closing,
        is_enable_password_saving=is_enable_password_saving
    )
    if not is_browser_started:
        LOGGER.error("共通 Chrome -> 启动 Ads Power 浏览器失败")
        return None
    # 5. 获取启动后的浏览器状态
    browser_status = adspower.get_browser_status(user_id=user_id, serial_number=serial_number)
    if not browser_status:
        LOGGER.error("共通 Chrome -> 获取 Ads Power 浏览器状态失败")
        return None
    if "debug_port" not in browser_status or not browser_status["debug_port"]:
        LOGGER.error("共通 Chrome -> Ads Power 浏览器状态中 debug_port 不存在")
        return None
    adspower_browser_debug_port = browser_status["debug_port"]
    # 4. 添加对于 debug 端口的转发
    # 4.1 删除之前对于浏览器 debug 端口的转发
    debug_port_forward_service_list = gost.get_port_forward_service_list(
        from_host=adspower_browser_forwarded_debug_host,
        from_port=adspower_browser_forwarded_debug_port)
    for debug_port_forward_service in debug_port_forward_service_list:
        gost.delete_port_forward_service_without_chain(debug_port_forward_service["name"])
    # 4.2 添加新的浏览器 debug 端口转发
    is_debug_port_forward_service_added = gost.add_port_forward_service_without_chain(
        from_host=adspower_browser_forwarded_debug_host,
        from_port=adspower_browser_forwarded_debug_port,
        from_protocol=adspower_browser_forwarded_debug_protocol,
        to_host=adspower_browser_debug_host,
        to_port=adspower_browser_debug_port,
        to_protocol=adspower_browser_debug_protocol
    )
    if not is_debug_port_forward_service_added:
        LOGGER.error("共通 Chrome -> 添加浏览器 debug 端口转发失败")
        return None
    # 6. 返回结果
    return adspower_host, adspower_browser_forwarded_debug_port

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