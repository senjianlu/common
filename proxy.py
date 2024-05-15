#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: ~/Projects/common/proxy.py
# @DATE: 2024/02/25 周日
# @TIME: 11:24:50
#
# @DESCRIPTION: 共通代理模块
#   使用 port 作为每个代理的主键


import base64
import random
import cachetools
from sqlalchemy import text

from common.config import CONFIG
from common.logger import LOGGER
from common.Base import init_db


# === 全局变量 ===
# 端口到代理信息的映射
#   格式：{30001: {"country_code": $country_code, "host": $host, "port": $port, "protocol": $protocol, "exit_ip": $exit_ip, "remark": $remark}, ...}
PORT_2_PROXY_INFO_DICT = {}
# 国家代码到代理字符串列表的映射
#   格式：{"CN": [30001, 30002, ...], "US": [30003, 30004, ...], ...}
COUNTRY_CODE_2_PORTS_DICT = {}
# 被禁用的出口 IP，30 分钟过期
BANNED_EXIT_IP_CACHE = cachetools.TTLCache(maxsize=1000, ttl=1800)
# 混淆密钥
OBFS_KEY = CONFIG["proxy"]["obfs_key"]
# 转发 Host
FORWARDER_HOST = CONFIG["proxy"]["forwarder_host"]
# 上次初始化时使用的参数
LAST_IS_EXIT_IP_REMOVE_DUPLICATE = True
LAST_COUNTRY_CODE_LIST = []
LAST_REMARK_LIKE_STR_LIST = []


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

def _generate_proxy_str(host, port, protocol, username, password):
    """
    @description: 生成代理字符串
    """
    proxy_str = None
    # 1. 参数判断
    if not host or not port or not protocol:
        LOGGER.error("共通 Proxy -> 生成代理字符串失败，参数不全")
        return proxy_str
    # 2. 生成代理字符串
    if username and password:
        proxy_str = "%s://%s:%s@%s:%s" % (protocol, username, password, host, port)
    else:
        proxy_str = "%s://%s:%s" % (protocol, host, port)
    # 3. 返回结果
    return proxy_str

def parse_proxy_str(proxy_str: str):
    """
    @description: 解析代理字符串
    """
    host = None
    port = None
    protocol = None
    username = None
    password = None
    # 1. 参数判断
    if not proxy_str:
        LOGGER.error("共通 Proxy -> 代理字符串为空，无法解析")
        return host, port, protocol, username, password
    # 2. 解析代理字符串
    try:
        # 2.1 解析协议
        protocol = proxy_str.split("://", 1)[0]
        # 2.2 解析主机和端口
        host_port = proxy_str.split("://", 1)[1]
        host = host_port.split(":", 1)[0]
        port = int(host_port.split(":", 1)[1].split("@", 1)[0])
        # 2.3 解析用户名和密码
        if "@" in host_port:
            username_password = host_port.split("@", 1)[0].split(":", 1)
            username = username_password[0]
            password = username_password[1]
    except Exception as e:
        LOGGER.error("共通 Proxy -> 解析代理字符串失败，错误信息：%s" % str(e))
    # 3. 返回结果
    return host, port, protocol, username, password

def _select_and_save_proxy_info(is_exit_ip_remove_duplicate, sql, session):
    """
    @description: 查询代理信息并保存到全局变量中
    """
    try:
        # 1. 查询代理
        result = session.execute(text(sql)).fetchall()
        # 2. 遍历结果并保存到临时结果中
        temp_country_code_2_ports_dict = {}
        temp_port_2_proxy_info_dict = {}
        exit_ip_list = []
        for row in result:
            country_code = row[0] if row[0] else "UNKNOWN"
            host = row[1]
            port = row[2]
            protocol = row[3]
            exit_ip = row[4]
            remark = row[5]
            # 2.1 如果需要去重，检查是否已经存在
            if is_exit_ip_remove_duplicate and exit_ip in exit_ip_list:
                continue
            else:
                exit_ip_list.append(exit_ip)
            # 2.2 插入到全局变量中
            if country_code not in temp_country_code_2_ports_dict:
                temp_country_code_2_ports_dict[country_code] = []
            temp_country_code_2_ports_dict[country_code].append(port)
            temp_port_2_proxy_info_dict[port] = {
                "country_code": country_code,
                "host": host,
                "port": port,
                "protocol": protocol,
                "exit_ip": exit_ip,
                "remark": remark
            }
        # 3. 排序并显示代理数量
        LOGGER.info("共通 Proxy -> 初始化代理池成功，代理数量：%s" % len(temp_port_2_proxy_info_dict))
        # 4. 保存到全局变量中
        global COUNTRY_CODE_2_PORTS_DICT
        global PORT_2_PROXY_INFO_DICT
        COUNTRY_CODE_2_PORTS_DICT = temp_country_code_2_ports_dict
        PORT_2_PROXY_INFO_DICT = temp_port_2_proxy_info_dict
    except Exception as e:
        LOGGER.error("共通 Proxy -> 查询代理失败，错误信息：%s" % str(e))
        return

def init_proxy_pool(is_exit_ip_remove_duplicate = True,
                    country_code_list: list = [],
                    remark_like_str_list: list = []):
    """
    @description: 初始化代理池
    @param {type}
    @return:
    """
    # 1. 连接数据库
    session = init_db()
    # 2. 查询所有代理
    # 2.1 基础查询语句
    sql = """
        SELECT
            pi.country_code,
            pp.host,
            pp.port,
            pp.protocol,
            pp.exit_ip,
            pp.remark
        FROM
            pp_proxy pp LEFT JOIN pp_ip pi ON pp.exit_ip = pi.ip
        WHERE
            pp.exit_ip IS NOT NULL
        AND pp.is_available = True
    """
    # 2.2 拼接查询条件
    if country_code_list:
        sql += " AND pi.country_code IN ('" + "', '".join(country_code_list) + "')"
    if remark_like_str_list:
        sql += " AND pp.remark LIKE '%" + "%' OR pp.remark LIKE '%".join(remark_like_str_list) + "%'"
    # 3. 查询代理
    _select_and_save_proxy_info(is_exit_ip_remove_duplicate, sql, session)
    # 4. 关闭数据库连接
    session.close()
    # 5. 保存初始化参数
    global LAST_IS_EXIT_IP_REMOVE_DUPLICATE
    global LAST_COUNTRY_CODE_LIST
    global LAST_REMARK_LIKE_STR_LIST
    LAST_IS_EXIT_IP_REMOVE_DUPLICATE = is_exit_ip_remove_duplicate
    LAST_COUNTRY_CODE_LIST = country_code_list
    LAST_REMARK_LIKE_STR_LIST = remark_like_str_list

def refresh_proxy_pool(is_exit_ip_remove_banned = True):
    """
    @description: 刷新代理池
    """
    # 1. 连接数据库
    session = init_db()
    # 2. 查询所有代理
    # 2.1 基础查询语句
    sql = """
        SELECT
            pi.country_code,
            pp.host,
            pp.port,
            pp.protocol,
            pp.exit_ip,
            pp.remark
        FROM
            pp_proxy pp LEFT JOIN pp_ip pi ON pp.exit_ip = pi.ip
        WHERE
            pp.exit_ip IS NOT NULL
        AND pp.is_available = True
    """
    # 2.2 拼接查询条件
    if is_exit_ip_remove_banned:
        banned_exit_ip_list = list(BANNED_EXIT_IP_CACHE.keys())
        sql += " AND pp.exit_ip NOT IN ('" + "', '".join(banned_exit_ip_list) + "')"
    if LAST_COUNTRY_CODE_LIST:
        sql += " AND pi.country_code IN ('" + "', '".join(LAST_COUNTRY_CODE_LIST) + "')"
    if LAST_REMARK_LIKE_STR_LIST:
        sql += " AND pp.remark LIKE '%" + "%' OR pp.remark LIKE '%".join(LAST_REMARK_LIKE_STR_LIST) + "%'"
    # 3. 查询代理
    _select_and_save_proxy_info(LAST_IS_EXIT_IP_REMOVE_DUPLICATE, sql, session)
    # 4. 关闭数据库连接
    session.close()

def get_proxy_str(country_code: str = None,
                  is_forward: bool = False,
                  protocol: str = "socks5"):
    """
    @description: 根据国家代码获取代理字符串
    @param {type} 
    country_code: 国家代码
    @return: 代理字符串
    """
    # 1. 代理池未初始化
    if not PORT_2_PROXY_INFO_DICT:
        LOGGER.warning("共通 Proxy -> 代理池未初始化，无法获取代理")
        return None
    # 2. 获取代理（这里为获取代理的主键 port）
    port = None
    # 2.1 指定了国家代码
    if country_code:
        if country_code in COUNTRY_CODE_2_PORTS_DICT:
            ports = COUNTRY_CODE_2_PORTS_DICT[country_code]
            if ports:
                port = random.choice(ports)
            else:
                LOGGER.warning("共通 Proxy -> 指定国家的代理池为空，无法获取代理")
                return None
        else:
            LOGGER.warning("共通 Proxy -> 未找到指定国家的代理池，无法获取代理")
            return None
    # 2.2 未指定国家代码
    else:
        all_ports = list(PORT_2_PROXY_INFO_DICT.keys())
        if all_ports:
            port = random.choice(all_ports)
        else:
            LOGGER.warning("共通 Proxy -> 代理池为空，无法获取代理")
            return None
    # 3. 根据端口查找代理信息，生成代理字符串
    # 3.1 获取代理信息
    if port not in PORT_2_PROXY_INFO_DICT:
        LOGGER.warning("共通 Proxy -> 未找到代理信息，无法获取代理")
        return None
    proxy_info = PORT_2_PROXY_INFO_DICT[port]
    # 3.2 生成账户和密码
    proxy_username, proxy_password = _generate_proxy_username_and_password_by_port(port)
    # 3.3 生成代理字符串
    proxy_str = _generate_proxy_str(
        proxy_info["host"],
        proxy_info["port"],
        proxy_info["protocol"],
        proxy_username,
        proxy_password
    )
    # 4. 指定了协议
    if protocol:
        proxy_str = protocol + "://" + proxy_str.split("://", 1)[1]
    # 5. 是否需要转发
    if is_forward:
        proxy_str = proxy_str.split("://", 1)[0] + "://" + FORWARDER_HOST + ":" + proxy_str.split(":")[-1]
    # 6. 返回结果
    return proxy_str

def ban_exit_ip_by_proxy_str(proxy_str: str):
    """
    @description: 根据代理字符串禁用出口 IP
    """
    # 1. 参数判断
    if not proxy_str:
        LOGGER.warning("共通 Proxy -> 代理字符串为空，无法禁用出口 IP")
        return
    # 2. 解析代理字符串
    host, port, protocol, username, password = parse_proxy_str(proxy_str)
    # 3. 获取代理信息
    proxy_info = PORT_2_PROXY_INFO_DICT.get(port, None)
    if not proxy_info:
        LOGGER.warning("共通 Proxy -> 未找到代理信息，无法禁用出口 IP")
        return
    # 4. 获取出口 IP
    exit_ip = proxy_info.get("exit_ip", None)
    if not exit_ip:
        LOGGER.warning("共通 Proxy -> 未找到出口 IP，无法禁用出口 IP")
        return
    # 5. 添加到禁用列表
    global BANNED_EXIT_IP_CACHE
    BANNED_EXIT_IP_CACHE[exit_ip] = True
    LOGGER.info("共通 Proxy -> 禁用出口 IP：%s" % exit_ip)
    # 6. 返回结果
    return

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
    global PORT_2_PROXY_INFO_DICT
    if port in PORT_2_PROXY_INFO_DICT:
        proxy_info = PORT_2_PROXY_INFO_DICT[port]
        # 3.1 移除代理信息
        PORT_2_PROXY_INFO_DICT.pop(port)
        LOGGER.info("共通 Proxy -> 从代理信息字典中移除代理：%s" % proxy_info)
    # 4. 移除代理字符串
    for country_code, ports in COUNTRY_CODE_2_PORTS_DICT.items():
        if port in ports:
            COUNTRY_CODE_2_PORTS_DICT[country_code].remove(port)
            LOGGER.info("共通 Proxy -> 从国家代码 %s 的代理列表中移除代理：%s" % (country_code, port))
    # 5. 返回结果
    return