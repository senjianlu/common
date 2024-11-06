#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: common/logic/s3_cloudflare_r2.py
# @DATE: 2024/10/22
# @TIME: 16:24:51
#
# @DESCRIPTION: S3 对象存储 Cloudflare R2 操作逻辑


class CloudflareR2:
    """
    Cloudflare R2 操作类
    """

    def __init__(self, access_key: str, secret_key: str, endpoint: str, bucket: str):
        """
        初始化
        """
        self.access_key = access_key
        self.secret_key = secret_key
        self.endpoint = endpoint
        self.bucket = bucket
        self.client = None
    
    def connect(self):
        """
        连接 S3
        """
        # 1. 检查参数
        if not self.access_key or not self.secret_key or not self.endpoint:
            raise Exception("S3 对象存储 Cloudflare R2 连接 -> 参数不完整")
        # 2. 连接 S3
        self.client = boto3.client(
            "s3",
            verify = False,
            endpoint_url = self.endpoint,
            aws_access_key_id = self.access_key,
            aws_secret_access_key = self.secret_key
        )
