#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: ~/Projects/common/proxy.py
# @DATE: 2024/02/25 周日
# @TIME: 11:24:50
#
# @DESCRIPTION: 共通代理模块


import base64
import random
from sqlalchemy import text

from common.config import CONFIG
from common.logger import LOGGER
from models.Base import init_db


# 全局变量
# 国家代码到代理字符串列表的映射
COUNTRY_CODE_2_PROXY_STR_LIST = {}
# 端口到代理字符串的映射
PORT_2_PROXY_STR = {}
# 混淆密钥
OBFS_KEY = CONFIG["proxy"]["obfs_key"]
# 转发 Host
FORWARDER_HOST = CONFIG["proxy"]["forwarder_host"]


def _generate_proxy_username_and_password_by_port(port: int):
    """
    @description: 生成代理用户名和密码
    @param {int} port 代理端口
    @return {str} 代理用户名和密码
    """
    # 1. 参数判断
    if not port:
        raise Exception("共通 Proxy -> 端口号不能为空")
    # 2. 进行 base64 编码
    encrypted_string = base64.b64encode(str(port).encode("utf-8")).decode("utf-8")
    # 3. 字符串加上混淆密钥
    encrypted_string = "{}{}".format(OBFS_KEY, encrypted_string)
    # 4. 再次进行 base64 编码
    encrypted_string = base64.b64encode(encrypted_string.encode("utf-8")).decode("utf-8")
    # 5. 尾部去掉所有的等号
    encrypted_string = encrypted_string.replace("=", "")
    # 6. 转为大写
    encrypted_string = encrypted_string.upper()
    # 7. 检查位数，不满 20 位在前面补 0
    if len(encrypted_string) < 20:
        encrypted_string = "0" * (20 - len(encrypted_string)) + encrypted_string
    # 8. 超过 20 位，依次从前面删一个，从后面删一个，直到 20 位
    while len(encrypted_string) > 20:
        encrypted_string = encrypted_string[1:]
        if len(encrypted_string) > 20:
            encrypted_string = encrypted_string[:-1]
    # 9. 返回结果
    return encrypted_string[:10], encrypted_string[10:]

def init_proxy_pool(is_exit_ip_remove_duplicate = True):
    """
    @description: 初始化代理池
    @param {type} 
    @return: 
    """
    # 1. 连接数据库
    session = init_db()
    # 2. 查询所有代理
    sql = """
    SELECT
        pi.country_code,
        pp.host,
        pp.port,
        pp.protocol,
        pp.exit_ip
    FROM
        pp_proxy pp LEFT JOIN pp_ip pi ON pp.exit_ip = pi.ip
    WHERE
        pp.exit_ip IS NOT NULL
    AND pp.is_available = True
    """
    try:
        # 2.1 查询代理
        result = session.execute(text(sql)).fetchall()
        # 2.2 遍历结果并插入到全局变量中
        global COUNTRY_CODE_2_PROXY_STR_LIST
        global PORT_2_PROXY_STR
        exit_ip_list = []
        for row in result:
            country_code = row[0] if row[0] else "UNKNOWN"
            host = row[1]
            port = row[2]
            protocol = row[3]
            exit_ip = row[4]
            # 如果需要去重
            if is_exit_ip_remove_duplicate and exit_ip in exit_ip_list:
                continue
            exit_ip_list.append(exit_ip)
            # 插入到全局变量中
            if country_code not in COUNTRY_CODE_2_PROXY_STR_LIST:
                COUNTRY_CODE_2_PROXY_STR_LIST[country_code] = []
            COUNTRY_CODE_2_PROXY_STR_LIST[country_code].append("%s://%s:%s" % (protocol, host, port))
            PORT_2_PROXY_STR[port] = "%s://%s:%s" % (protocol, host, port)
        # 2.3 打印日志（各个国家的代理数量）
        for country_code, proxy_str_list in COUNTRY_CODE_2_PROXY_STR_LIST.items():
            LOGGER.info("共通 Proxy -> 国家代码：%s，代理数量：%s" % (country_code, len(proxy_str_list)))
    except Exception as e:
        LOGGER.error("共通 Proxy -> 查询代理失败，错误信息：%s" % str(e))
        return
    # 3. 关闭数据库连接
    finally:
        session.close()

def get_proxy_str(country_code: str = None, is_forward: bool = False, protocol: str = "socks5"):
    """
    @description: 根据国家代码获取代理字符串
    @param {type} 
    country_code: 国家代码
    @return: 代理字符串
    """
    proxy_str = None
    # 1. 代理池未初始化
    if not COUNTRY_CODE_2_PROXY_STR_LIST:
        LOGGER.warning("共通 Proxy -> 代理池未初始化，无法获取代理")
        return proxy_str
    # 2.1 指定了国家代码
    if country_code:
        if country_code in COUNTRY_CODE_2_PROXY_STR_LIST:
            proxy_str_list = COUNTRY_CODE_2_PROXY_STR_LIST[country_code]
            if proxy_str_list:
                proxy_str = random.choice(proxy_str_list)
            else:
                LOGGER.warning("共通 Proxy -> 指定国家的代理池为空，无法获取代理")
                return proxy_str
        else:
            LOGGER.warning("共通 Proxy -> 未找到指定国家的代理池，无法获取代理")
            return proxy_str
    # 2.2 未指定国家代码
    else:
        all_proxy_str_list = [proxy_str for proxy_str_list in COUNTRY_CODE_2_PROXY_STR_LIST.values() for proxy_str in proxy_str_list]
        if all_proxy_str_list:
            proxy_str = random.choice(all_proxy_str_list)
        else:
            LOGGER.warning("共通 Proxy -> 代理池为空，无法获取代理")
            return proxy_str
    # 3. 指定了协议
    proxy_protocol = protocol if protocol else proxy_str.split("://", 1)[0]
    # 4. 是否需要转发
    if proxy_str:
        if is_forward:
            # 4.1 是的话，不需要账号密码，但是需要替换 host
            proxy_str = proxy_protocol + "://" + FORWARDER_HOST + ":" + proxy_str.split(":")[-1]
        else:
            # 4.2 否的话，需要账号密码
            proxy_username, proxy_password = _generate_proxy_username_and_password_by_port(int(proxy_str.split(":")[-1]))
            proxy_str = "%s://%s:%s@%s" % (proxy_protocol, proxy_username, proxy_password, proxy_str.split("://", 1)[1])
    # 5. 返回结果
    return proxy_str

def remove_by_proxy_str(proxy_str: str):
    """
    @description: 根据代理字符串移除代理
    @param {type} 
    proxy_str: 代理字符串
    @return: 
    """
    # 1. 参数判断
    if not proxy_str:
        LOGGER.warning("共通 Proxy -> 代理字符串为空，无法移除代理")
        return
    # 2. 获取代理的端口，暂时可以作为唯一标识
    port = int(proxy_str.split(":")[-1])
    # 3. 获取代理字符串
    global PORT_2_PROXY_STR
    if port in PORT_2_PROXY_STR:
        proxy_str = PORT_2_PROXY_STR[port]
    else:
        LOGGER.warning("共通 Proxy -> 未找到代理字符串，无法移除代理")
        return
    # 4. 移除代理字符串
    for country_code, proxy_str_list in COUNTRY_CODE_2_PROXY_STR_LIST.items():
        if proxy_str in proxy_str_list:
            proxy_str_list.remove(proxy_str)
            LOGGER.info("共通 Proxy -> 移除代理：%s" % proxy_str)
            break
    # 5. 返回结果
    return