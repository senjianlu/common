#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: common/s3.py
# @DATE: 2024/10/21
# @TIME: 18:24:36
#
# @DESCRIPTION: S3 对象存储共通操作模块


import boto3

from common.config import CONFIG


def _check_is_provider_valid(provider: str) -> bool:
    """
    检查 provider 是否合法
    """
    return provider.lower() in ["cloudflare_r2"]

def _get_config(provider: str) -> (str, str, str, str):
    """
    获取配置
    """
    return (
        CONFIG["s3"][provider]["access_key"],
        CONFIG["s3"][provider]["secret_key"],
        CONFIG["s3"][provider]["endpoint"],
        CONFIG["s3"][provider]["bucket"]
    )


class S3:
    """
    S3 对象存储共通操作类
    """
    def __init__(self,
                 provider: str,
                 access_key: str = None,
                 secret_key: str = None,
                 endpoint: str = None,
                 bucket: str = None):
        """
        初始化
        """
        # 1. 检查 provider 是否合法
        if not _check_is_provider_valid(provider):
            raise Exception("S3 对象存储 -> 不支持的提供商")
        # 2. 获取配置
        default_access_key, default_secret_key, default_endpoint, default_bucket = _get_config(provider)
        # 3. 以传入参数优先
        self.provider = provider
        self.access_key = access_key or default_access_key
        self.secret_key = secret_key or default_secret_key
        self.endpoint = endpoint or default_endpoint
        self.bucket = bucket or default_bucket
        # 4. 连接
        self.client = None

    def connect(self):
        """
        连接
        """
        self.client = boto3.client(
            "s3",
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key
        )
