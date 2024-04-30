#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: ~/Projects/common/redis.py
# @DATE: 2024/02/25 周日
# @TIME: 11:25:07
#
# @DESCRIPTION: Redis 共通操作


import time
import redis

from common.config import CONFIG
from common.logger import LOGGER


# 全局变量
REDIS_POOL = None


def init_redis_pool(db = CONFIG["redis"]["db"]):
    """
    @description: 初始化 Redis 连接池
    @param {type} 
    @return: 
    """
    # 1. 初始化连接池
    global REDIS_POOL
    REDIS_POOL = redis.ConnectionPool(
        host=CONFIG["redis"]["host"],
        port=CONFIG["redis"]["port"],
        db=db,
        password=CONFIG["redis"]["password"],
        decode_responses=True
    )
    # 2. 打印日志
    LOGGER.info("共通 Redis -> Redis 连接池初始化成功")

def get_connetion(db = CONFIG["redis"]["db"]):
    """
    @description: 获取 Redis 连接
    """
    # 1. 初始化连接池
    global REDIS_POOL
    if not REDIS_POOL:
        init_redis_pool(db=db)
    # 2. 返回连接
    return redis.StrictRedis(connection_pool=REDIS_POOL)

def lock(lock_id, expire = 60) -> bool:
    """
    @description: 获取锁
    @param {type} 
    lock_name: 锁名
    expire: 过期时间（秒）
    @return: 
    """
    # 1. 获取连接
    global REDIS_POOL
    if not REDIS_POOL:
        init_redis_pool(db = 1)
    redis_conn = redis.StrictRedis(connection_pool=REDIS_POOL)
    # 2. 使用 LUA 脚本尝试锁定并设置过期时间
    is_lock_success = False
    lua_script = """
    if redis.call('get', KEYS[1]) == false then
        if redis.call('setnx', KEYS[1], ARGV[1]) == 1 then
            return redis.call('expire', KEYS[1], ARGV[2])
        else
            return 0
        end
    else
        return 0
    end
    """
    try:
        redis_key = "lock.{}".format(lock_id)
        is_lock_success = redis_conn.eval(lua_script, 1, redis_key, "1", expire)
        LOGGER.info("共通 Redis -> 获取锁 {} 成功".format(lock_id))
    except Exception as e:
        LOGGER.error("共通 Redis -> 获取锁 {} 失败: {}".format(lock_id, e))
    # 3. 返回锁
    return is_lock_success == 1

def unlock(lock_id) -> bool:
    """
    @description: 释放锁
    @param {type} 
    lock_name: 锁名
    @return: 
    """
    # 1. 获取连接
    global REDIS_POOL
    if not REDIS_POOL:
        init_redis_pool(db = 1)
    redis_conn = redis.StrictRedis(connection_pool=REDIS_POOL)
    # 2. 删除锁
    is_unlock_success = False
    lua_script = """
    if redis.call('get', KEYS[1]) == ARGV[1] then
        return redis.call('del', KEYS[1])
    else
        return 0
    end
    """
    try:
        redis_key = "lock.{}".format(lock_id)
        is_unlock_success = redis_conn.eval(lua_script, 1, redis_key, "1")
        LOGGER.info("共通 Redis -> 释放锁 {} 成功".format(lock_id))
    except Exception as e:
        LOGGER.error("共通 Redis -> 释放锁 {} 失败: {}".format(lock_id, e))
    # 3. 返回结果
    return is_unlock_success == 1

def wait_until_unlock(lock_id, max_wait_seconds = 60) -> bool:
    """
    @description: 等待锁释放
    @param {type} 
    lock_name: 锁名
    max_wait_seconds: 最大等待时间（秒）
    @return: 
    """
    # 1. 获取连接
    global REDIS_POOL
    if not REDIS_POOL:
        init_redis_pool(db = 1)
    redis_conn = redis.StrictRedis(connection_pool=REDIS_POOL)
    # 2. 循环等待
    start_time = time.time()
    LOGGER.info("共通 Redis -> 等待锁 {} 释放".format(lock_id))
    while time.time() - start_time < max_wait_seconds:
        # 3. 判断锁是否释放
        if not redis_conn.exists("lock.{}".format(lock_id)):
            LOGGER.info("共通 Redis -> 等待锁 {} 释放成功".format(lock_id))
            return True
        # 4. 等待 1 秒
        time.sleep(1)
    # 5. 等待超时
    LOGGER.error("共通 Redis -> 等待锁 {} 释放超时".format(lock_id))
    return False
