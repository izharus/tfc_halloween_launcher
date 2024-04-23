"""Tests for src.launcher.yos module."""
import boto3
import boto3.exceptions
import boto3.utils
from src.launcher.utillity.yos import get_boto3_instance


def test_get_boto3_instance_success():
    """Test if boto3 instance creates successfully."""
    assert get_boto3_instance()


def test_get_boto3_instance_failed(mocker):
    """Test if get_boto3_instance catches boto3 exceptions."""
    with mocker.patch.object(
        boto3,
        "client",
        side_effect=boto3.exceptions.S3TransferFailedError,
    ):
        assert get_boto3_instance() is None
