#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: common/database.py
# @DATE: 2024/03/24
# @TIME: 16:16:55
#
# @DESCRIPTION: 数据库模块


from functools import wraps
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import text
from sqlalchemy import event
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import Insert
from enum import Enum

from common.config import CONFIG
from common.logger import LOGGER


# 基类
Base = declarative_base()
# 日志标识
LOGGER_PREFIX = "共通 Base 模块 -> "


class DatabaseType(Enum):
    """
    @description: 数据库类型
    @param {type}
    """
    POSTGRESQL = "POSTGRESQL"
    # 暂时只支持 PostgreSQL 数据库
    # MYSQL = "MYSQL"
    # SQLITE = "SQLITE"

def _check_config(config_key):
    """
    @description: 检查配置文件
    @param {type}
    """
    # 1. 判断是否有 Base 配置
    if config_key not in CONFIG:
        raise Exception(LOGGER_PREFIX + "没有找到 {} 配置".format(config_key))
    # 2. 判断是否是支持的数据库类型
    if CONFIG[config_key]["type"] not in [item.value for item in DatabaseType]:
        raise Exception(LOGGER_PREFIX + "不支持的数据库类型：{}".format(CONFIG[config_key]["type"]))
    # 3. 返回
    return True


@compiles(Insert, "postgresql")
def postgresql_on_conflict_do_nothing(insert, compiler, **kw):
    """
    @description: PostgreSQL 插入数据时如果冲突则不做任何操作
    @param {type}
    insert: 插入语句
    compiler: 编译器
    **kw: 其他参数
    """
    statement = compiler.visit_insert(insert, **kw)
    # IF we have a "RETURNING" clause, we must insert before it
    returning_position = statement.find("RETURNING")
    if returning_position >= 0:
        return (
                statement[:returning_position]
                + "ON CONFLICT DO NOTHING "
                + statement[returning_position:]
        )
    else:
        return statement + " ON CONFLICT DO NOTHING"

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

def truncate_table(session, model):
    """
    @description: 清空表
    """
    session.execute(text("TRUNCATE TABLE {}".format(model.__tablename__)))

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


def init(config_key = "database",
         host: str = None,
         port: int = None,
         username: str = None,
         password: str = None,
         database: str = None):
    """
    @description: 初始化数据库
    @param {type}
    engine: 数据库引擎
    @return:
    """
    # 1. 检查配置文件
    _check_config(config_key)
    # 2. 获取数据库连接信息
    host = host if host else CONFIG[config_key]["host"]
    port = port if port else CONFIG[config_key]["port"]
    username = username if username else CONFIG[config_key]["username"]
    password = password if password else CONFIG[config_key]["password"]
    database = database if database else CONFIG[config_key]["database"]
    # 3. 判断参数
    if not host or not port or not username or not password or not database:
        raise Exception(LOGGER_PREFIX + "数据库参数不完整")
    # 4. 建立数据库连接
    engine = create_engine(
        f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}",
    )
    # 4. 创建表（表结构变更时需要手动执行）
    Base.metadata.create_all(engine)
    # 5. 创建 DBSession
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    # 6. 打印数据库连接信息
    LOGGER.info(LOGGER_PREFIX + "数据库 {} 连接建立：{}".format(host, session.execute(text("SELECT version()")).fetchone()[0]))
    # 7. 监听插入和更新事件，设置创建者和更新者信息
    for mapper in Base.registry.mappers:
        event.listen(mapper, 'before_insert', set_created_by)
        event.listen(mapper, 'before_update', set_updated_by)
    # 8. 返回 session
    return session
