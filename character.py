#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: common/character.py
# @DATE: 2024/07/27
# @TIME: 20:17:59
#
# @DESCRIPTION: 字符串处理模块


def is_chinese(char: str) -> bool:
    """
    @description: 判断字符是否为中文
    @param {type}
    char: 待判断字符
    @return: 是否为中文
    """
    return '\u4e00' <= char <= '\u9fa5'

def is_alphabet(char: str) -> bool:
    """
    @description: 判断字符是否为英文字母
    @param {type}
    char: 待判断字符
    @return: 是否为英文字母
    """
    return 'a' <= char <= 'z' or 'A' <= char <= 'Z'

def is_number(char: str) -> bool:
    """
    @description: 判断字符是否为数字
    @param {type}
    char: 待判断字符
    @return: 是否为数字
    """
    return '0' <= char <= '9'

def is_all_alphabet_or_number(string: str) -> bool:
    """
    @description: 判断字符串是否全部为英文字母或数字
    @param {type}
    string: 待判断字符串
    @return: 是否全部为英文字母或数字
    """
    for char in string:
        if not is_alphabet(char) and not is_number(char):
            return False
    return True