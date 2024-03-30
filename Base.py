#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: common/Base.py
# @DATE: 2024/03/24
# @TIME: 16:16:55
#
# @DESCRIPTION: ORM 模型基类


from functools import wraps
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import text
from sqlalchemy import event

# 导入配置，需要每次都重新导入，因为配置可能会变更
from common.config import CONFIG
from common.logger import LOGGER


# 基类
Base = declarative_base()


def set_created_by(mapper, connection, instance):
    """
    @description: 设置创建者信息
    @param {type}
    user_id: 用户 ID
    user_name: 用户名
    @return:
    """
    instance.created_by = CONFIG["user"]["id"]
    instance.created_by_name = CONFIG["user"]["name"]
    instance.created_at = datetime.now()

def set_updated_by(mapper, connection, instance):
    """
    @description: 设置更新者信息
    @param {type}
    user_id: 用户 ID
    user_name: 用户名
    @return:
    """
    instance.updated_by = CONFIG["user"]["id"]
    instance.updated_by_name = CONFIG["user"]["name"]
    instance.updated_at = datetime.now()


def init_db(host: str = CONFIG["postgresql"]["host"],
            port: int = CONFIG["postgresql"]["port"],
            username: str = CONFIG["postgresql"]["username"],
            password: str = CONFIG["postgresql"]["password"],
            database: str = CONFIG["postgresql"]["database"]):
    """
    @description: 初始化数据库
    @param {type}
    engine: 数据库引擎
    @return:
    """
    # 1. 判断参数
    if not host or not port or not username or not password or not database:
        LOGGER.error("类 Base -> 数据库参数错误")
        return None
    # 2. 建立数据库连接
    engine = create_engine(
        f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}",
    )
    # 3. 创建表（表结构变更时需要手动执行）
    Base.metadata.create_all(engine)
    # 4. 创建 DBSession
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    # 5. 查看数据库版本
    LOGGER.info("类 Base -> 数据库 {} 连接建立：{}".format(host, session.execute(text("SELECT version()")).fetchone()[0]))
    # 6. 监听插入和更新事件，设置创建者和更新者信息
    for mapper in Base.registry.mappers:
        event.listen(mapper, 'before_insert', set_created_by)
        event.listen(mapper, 'before_update', set_updated_by)
    # 7. 返回 session
    return session

def ensure_db_session(func):
    """
    @description: 确保数据库连接，需要手动指定参数 session=None 时才会触发
    @param {type}
    func: 函数
    @return:
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 检查是否已经传入了 session
        if "session" in kwargs and isinstance(kwargs["session"], Session):
            return func(*args, **kwargs)
        else:
            # 如果没有传入 session，就创建一个新的 session
            session = init_db()
            try:
                kwargs['session'] = session
                return func(*args, **kwargs)
            finally:
                # 确保在函数执行结束后关闭 session
                session.close()
    return wrapper

def batch_insert(session, model, data):
    """
    @description: 批量插入数据
    @param {type}
    session: 数据库连接
    model: 模型
    data: 数据
    @return:
    """
    # 1. 设置创建者信息
    for item in data:
        set_created_by(None, None, item)
    # 2. 批量插入
    session.bulk_save_objects(data)