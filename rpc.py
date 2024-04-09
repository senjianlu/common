#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: common/rpc.py
# @DATE: 2024/04/05
# @TIME: 10:40:36
#
# @DESCRIPTION: RPC 通信模块


from decimal import Decimal


def convert_decimal_to_marked_str(obj):
    """
    @description: 将对象中的 Decimal 属性转换为被标记的字符串
    :param obj: 待转换对象
    :return: 转换后对象
    """
    # 1. 如果是 Decimal
    if isinstance(obj, Decimal):
        obj = "<r_c><D>{}</D></r_c>".format(obj)
    # 2. 如果是字典
    elif isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = convert_decimal_to_marked_str(value)
    # 3. 如果是列表
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            obj[index] = convert_decimal_to_marked_str(value)
    # 4. 如果是自定义对象
    elif hasattr(obj, "__dict__"):
        for key, value in obj.__dict__.items():
            obj.__dict__[key] = convert_decimal_to_marked_str(value)
    # 5. 返回结果
    return obj

def convert_marked_str_to_decimal(obj):
    """
    @description: 将对象中的被标记的字符串转换为 Decimal 属性
    :param obj: 待转换对象
    :return: 转换后对象
    """
    # 1. 如果是被标记的字符串
    if isinstance(obj, str) and obj.startswith("<r_c><D>") and obj.endswith("</D></r_c>"):
        obj = Decimal(obj.replace("<r_c><D>", "").replace("</D></r_c>", ""))
    # 2. 如果是字典
    elif isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = convert_marked_str_to_decimal(value)
    # 3. 如果是列表
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            obj[index] = convert_marked_str_to_decimal(value)
    # 4. 如果是自定义对象
    elif hasattr(obj, "__dict__"):
        for key, value in obj.__dict__.items():
            obj.__dict__[key] = convert_marked_str_to_decimal(value)
    # 5. 返回结果
    return obj
