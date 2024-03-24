#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: common/currency.py
# @DATE: 2024/03/24
# @TIME: 16:38:02
#
# @DESCRIPTION: 货币相关


from sqlalchemy import text

from common.config import CONFIG
from common.logger import LOGGER
from common.Base import init_db


# 本位币
BASE_CURRENCY_CODE = CONFIG["currency"]["base_currency_code"] or "CNY"
# 汇率
CURRENCY_RATES = {}


class BaseCurrencyRateNotExistsError(Exception):
    """
    @description: 本位币汇率不存在
    """
    def __init__(self):
        super().__init__("本位币 {} 汇率不存在".format(BASE_CURRENCY_CODE))


def init_currency_rates():
    """
    @description: 初始化货币汇率
    @param {type}
    @return:
    """
    # 1. 初始化数据库
    session = init_db()
    # 2. 查询本位币和人民币的汇率
    sql = """
        SELECT
            rate
        FROM
            bd_v_currency
        WHERE
            code = :base_currency_code
    """
    result = session.execute(text(sql), {"base_currency_code": BASE_CURRENCY_CODE}).fetchall()
    if not result:
        LOGGER.error("共通 Currency -> 本位币汇率不存在")
        raise BaseCurrencyRateNotExistsError()
    to_cny_rate = result[0][0]
    # 3. 检索全部货币
    sql = """
        SELECT
            currency_type,
            code,
            rate
        FROM
            bd_v_currency
    """
    result = session.execute(text(sql)).fetchall()
    # 4. 计算汇率
    temp_currency_rates = {}
    for currency in result:
        temp_currency_rates[currency[1]] = currency[2] / to_cny_rate
        # print(currency[1], currency[2] / to_cny_rate)
    # 5. 关闭数据库连接
    session.close()
    LOGGER.info("共通 Currency -> 初始化货币汇率成功，共 {} 种货币".format(len(temp_currency_rates)))
    # 6. 赋值
    global CURRENCY_RATES
    CURRENCY_RATES = temp_currency_rates