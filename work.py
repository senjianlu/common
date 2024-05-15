#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: common/work.py
# @DATE: 2024/04/30
# @TIME: 23:33:21
#
# @DESCRIPTION: 工作模块


import time
from functools import wraps

from common.logger import LOGGER
from common import redis
from common.logic.work_worker import StatusEnum as WorkerStatusEnum


def ensure_worker_end(worker_id, WORK_RECORD_ID_REDIS_KEY, WORKER_ID_REDIS_KEY: str=None, WORK_RECORD_EXPIRE=600, WORKER_EXPIRE=600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                LOGGER.error("共通工作 -> 装饰器监测到方法出错：{}".format(str(e)))
            finally:
                end(worker_id, WORK_RECORD_ID_REDIS_KEY, WORKER_ID_REDIS_KEY, WORK_RECORD_EXPIRE, WORKER_EXPIRE)
            return result
        return wrapper
    return decorator

def start(worker_id, WORK_RECORD_ID_REDIS_KEY, WORKER_ID_REDIS_KEY: str=None, WORK_RECORD_EXPIRE=600, WORKER_EXPIRE=600):
    """
    @description: 开始工作
    """
    LOGGER.info("共通工作 -> {} {} 开始尝试启动！".format(WORK_RECORD_ID_REDIS_KEY, worker_id))
    # 1. 参数判断
    if not WORKER_ID_REDIS_KEY:
        # 去掉最后一个冒号和后面的内容，然后加上 worker_id
        WORKER_ID_REDIS_KEY = WORK_RECORD_ID_REDIS_KEY[:WORK_RECORD_ID_REDIS_KEY.rfind(":")] + ":worker:" + worker_id
    # 2. 建立 Redis 连接
    redis_conn = redis.get_connetion(db=3)
    # 3. 创建或读取工作记录 ID
    work_record_id = redis_conn.get(WORK_RECORD_ID_REDIS_KEY)
    if not work_record_id:
        LOGGER.info("共通工作 -> {} 没有工作记录 ID，开始创建！".format(worker_id))
        work_record_id = "{}_{}".format(time.strftime("%Y%m%d%H%M%S", time.localtime()), int(time.time() * 1000))
        redis_conn.set(WORK_RECORD_ID_REDIS_KEY, work_record_id, ex=WORK_RECORD_EXPIRE)
        LOGGER.info("共通工作 -> {} 创建工作记录 ID：{}！".format(worker_id, work_record_id))
    else:
        LOGGER.info("共通工作 -> {} 已经有工作记录 ID：{}！".format(worker_id, work_record_id))
    # 4. 创建或读取工作者状态
    worker_status = redis_conn.get(WORKER_ID_REDIS_KEY)
    if not worker_status or worker_status == WorkerStatusEnum.END.value:
        LOGGER.info("共通工作 -> {} 没有工作者状态或工作者状态为结束，开始创建！".format(worker_id))
        redis_conn.set(WORKER_ID_REDIS_KEY, WorkerStatusEnum.START.value, ex=WORKER_EXPIRE)
        LOGGER.info("共通工作 -> {} 创建工作者状态！".format(worker_id))
        return True
    else:
        LOGGER.info("共通工作 -> {} 已经有工作者状态：{}，这种情况可能是由于上次工作异常结束或工作者 ID 重复导致的！".format(worker_id, worker_status))
        return False

def active(worker_id, WORK_RECORD_ID_REDIS_KEY,  WORKER_ID_REDIS_KEY: str=None, WORK_RECORD_EXPIRE=600, WORKER_EXPIRE=600):
    """
    @description: 激活工作（刷新过期时间）
    """
    LOGGER.info("共通工作 -> {} {} 开始尝试激活！".format(WORK_RECORD_ID_REDIS_KEY, worker_id))
    # 1. 参数判断
    if not WORKER_ID_REDIS_KEY:
        # 去掉最后一个冒号和后面的内容，然后加上 worker_id
        WORKER_ID_REDIS_KEY = WORK_RECORD_ID_REDIS_KEY[:WORK_RECORD_ID_REDIS_KEY.rfind(":")] + ":worker:" + worker_id
    # 2. 建立 Redis 连接
    redis_conn = redis.get_connetion(db=3)
    # 3. 读取工作记录 ID
    work_record_id = redis_conn.get(WORK_RECORD_ID_REDIS_KEY)
    if not work_record_id:
        LOGGER.info("共通工作 -> {} 没有工作记录 ID，无法激活！".format(worker_id))
        return False
    else:
        LOGGER.info("共通工作 -> {} 读取到工作记录 ID：{}！".format(worker_id, work_record_id))
    # 4. 刷新工作记录 ID 的过期时间
    redis_conn.expire(WORK_RECORD_ID_REDIS_KEY, WORK_RECORD_EXPIRE)
    # 5. 读取工作者状态
    worker_status = redis_conn.get(WORKER_ID_REDIS_KEY)
    if not worker_status:
        LOGGER.info("共通工作 -> {} 没有工作者状态，可能是由于距离上次工作记录 ID 创建时间过长导致的，直接创建并激活！".format(worker_id))
    else:
        LOGGER.info("共通工作 -> {} 读取到工作者状态：{}，刷新过期时间！".format(worker_id, worker_status))
    # 6. 刷新工作者状态的过期时间
    redis_conn.set(WORKER_ID_REDIS_KEY, WorkerStatusEnum.RUNNING.value, ex=WORKER_EXPIRE)
    LOGGER.info("共通工作 -> {} 刷新工作者状态的过期时间！".format(worker_id))
    return True

def end(worker_id, WORK_RECORD_ID_REDIS_KEY, WORKER_ID_REDIS_KEY: str=None, WORK_RECORD_EXPIRE=600, WORKER_EXPIRE=600):
    """
    @description: 结束工作
    """
    LOGGER.info("共通工作 -> {} {} 开始尝试结束！".format(WORK_RECORD_ID_REDIS_KEY, worker_id))
    # 1. 参数判断
    if not WORKER_ID_REDIS_KEY:
        # 去掉最后一个冒号和后面的内容，然后加上 worker_id
        WORKER_ID_REDIS_KEY = WORK_RECORD_ID_REDIS_KEY[:WORK_RECORD_ID_REDIS_KEY.rfind(":")] + ":worker:" + worker_id
    # 2. 建立 Redis 连接
    redis_conn = redis.get_connetion(db=3)
    # 3. 读取当前工作者状态
    worker_status = redis_conn.get(WORKER_ID_REDIS_KEY)
    if not worker_status:
        LOGGER.info("共通工作 -> {} 没有工作者状态，可能是由于距离上次工作记录 ID 创建时间过长导致的，直接创建并结束！".format(worker_id))
    else:
        LOGGER.info("共通工作 -> {} 读取到工作者状态：{}，修改为结束！".format(worker_id, worker_status))
    # 4. 结束当前工作者状态
    redis_conn.set(WORKER_ID_REDIS_KEY, WorkerStatusEnum.END.value, ex=WORKER_EXPIRE)
    # 5. 读取全部工作者状态
    other_worker_id_redis_key_like = WORK_RECORD_ID_REDIS_KEY[:WORK_RECORD_ID_REDIS_KEY.rfind(":")] + ":worker:*"
    other_worker_id_redis_keys = redis_conn.keys(other_worker_id_redis_key_like)
    other_worker_statuses = []
    for other_worker_id_redis_key in other_worker_id_redis_keys:
        other_worker_statuses.append(redis_conn.get(other_worker_id_redis_key))
    LOGGER.info("共通工作 -> {} 读取到全部工作者状态：{}！".format(worker_id, other_worker_statuses))
    # 6. 判断是否全部结束
    if WorkerStatusEnum.START.value in other_worker_statuses or WorkerStatusEnum.RUNNING.value in other_worker_statuses:
        redis_conn.expire(WORK_RECORD_ID_REDIS_KEY, WORK_RECORD_EXPIRE)
        LOGGER.info("共通工作 -> {} 还有其他工作者在运行或等待，不结束！".format(worker_id))
        return False
    else:
        LOGGER.info("共通工作 -> {} 全部工作者都结束，结束工作记录 ID！".format(worker_id))
    # 7. 结束工作记录 ID
    redis_conn.delete(WORK_RECORD_ID_REDIS_KEY)
    LOGGER.info("共通工作 -> {} 从 Redis 中被删除！".format(WORK_RECORD_ID_REDIS_KEY))
    return True

def wait_until_all_workers_end(worker_id, WORK_RECORD_ID_REDIS_KEY, WORKER_ID_REDIS_KEY: str=None):
    """
    @description: 等待所有工作者结束
    """
    LOGGER.info("共通工作 -> {} {} 开始尝试等待所有工作者结束！".format(WORK_RECORD_ID_REDIS_KEY, worker_id))
    # 1. 参数判断
    if not WORKER_ID_REDIS_KEY:
        # 去掉最后一个冒号和后面的内容，然后加上 worker_id
        WORKER_ID_REDIS_KEY = WORK_RECORD_ID_REDIS_KEY[:WORK_RECORD_ID_REDIS_KEY.rfind(":")] + ":worker:" + worker_id
    # 2. 建立 Redis 连接
    redis_conn = redis.get_connetion(db=3)
    # 3. 循环等待直到全部结束
    while True:
        # 4. 读取全部工作者状态
        other_worker_id_redis_key_like = WORK_RECORD_ID_REDIS_KEY[:WORK_RECORD_ID_REDIS_KEY.rfind(":")] + ":worker:*"
        other_worker_id_redis_keys = redis_conn.keys(other_worker_id_redis_key_like)
        other_worker_statuses = []
        for other_worker_id_redis_key in other_worker_id_redis_keys:
            other_worker_statuses.append(redis_conn.get(other_worker_id_redis_key))
        LOGGER.info("共通工作 -> {} 读取到全部工作者状态：{}！".format(worker_id, other_worker_statuses))
        # 4. 判断是否全部结束
        if WorkerStatusEnum.START.value in other_worker_statuses or WorkerStatusEnum.RUNNING.value in other_worker_statuses:
            LOGGER.info("共通工作 -> {} 还有其他工作者在运行或等待，继续等待！".format(worker_id))
            time.sleep(1)
        else:
            LOGGER.info("共通工作 -> {} 全部工作者都结束，结束等待！".format(worker_id))
            break
    return True

def clear_all_workers(worker_id, WORK_RECORD_ID_REDIS_KEY):
    """
    @description: 清除所有工作者
    """
    LOGGER.info("共通工作 -> {} {} 开始尝试清除所有工作者！".format(WORK_RECORD_ID_REDIS_KEY, worker_id))
    # 1. 建立 Redis 连接
    redis_conn = redis.get_connetion(db=3)
    # 2. 读取全部工作者状态
    other_worker_id_redis_key_like = WORK_RECORD_ID_REDIS_KEY[:WORK_RECORD_ID_REDIS_KEY.rfind(":")] + ":worker:*"
    other_worker_id_redis_keys = redis_conn.keys(other_worker_id_redis_key_like)
    for other_worker_id_redis_key in other_worker_id_redis_keys:
        redis_conn.delete(other_worker_id_redis_key)
        LOGGER.info("共通工作 -> {} 删除工作者状态：{}！".format(worker_id, other_worker_id_redis_key))
    return True

def clean_up(redis_key_like: str):
    """
    @description: 清理 Redis 中的数据
    """
    LOGGER.info("共通工作 -> 开始尝试清理 Redis 中键类似 {} 的数据！".format(redis_key_like))
    # 1. 参数检查
    if not redis_key_like:
        LOGGER.error("共通工作 -> 键类似不能为空！")
        return False
    # 2. 建立 Redis 连接
    redis_conn = redis.get_connetion(db=3)
    # 3. 读取全部键
    redis_keys = redis_conn.keys(redis_key_like)
    for redis_key in redis_keys:
        redis_conn.delete(redis_key)
        LOGGER.info("共通工作 -> 删除键：{}！".format(redis_key))
    return True
