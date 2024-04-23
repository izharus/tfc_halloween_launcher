"""Module with utility functions for boto3."""
from typing import Optional

import boto3
import boto3.exceptions
from log_wizard import log as get_logger
from src.launcher.boto3_cred import BOTO3_ACCESS_KEY, BOTO3_SECRET_KEY

log = get_logger()


def get_boto3_instance() -> Optional[boto3.client]:
    """Initialize a boto3 instance."""
    try:
        s3 = boto3.client(
            "s3",
            endpoint_url="https://storage.yandexcloud.net",
            aws_access_key_id=BOTO3_ACCESS_KEY,
            aws_secret_access_key=BOTO3_SECRET_KEY,
        )
    except boto3.exceptions.Boto3Error as error:
        log.critical(f"Failed to receive a boto3 instance: {error}.")
        return None
    log.debug("Boto3 instance was received.")
    return s3
