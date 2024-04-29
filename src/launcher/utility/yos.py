"""Module with utility functions for boto3."""
from typing import Optional

import boto3
import boto3.exceptions
from loguru import logger as log
from src.launcher.boto3_cred import BOTO3_ACCESS_KEY, BOTO3_SECRET_KEY


def get_boto3_instance() -> boto3.client:
    s3 = boto3.client(
        "s3",
        endpoint_url="https://storage.yandexcloud.net",
        aws_access_key_id=BOTO3_ACCESS_KEY,
        aws_secret_access_key=BOTO3_SECRET_KEY,
    )
    return s3
