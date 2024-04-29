"""Unit tests for src/launcher/utility/file_downloader.py"""
import os
from unittest.mock import MagicMock, patch

import boto3
import pytest
import requests
from src.launcher.utility.custom_exceptions import (
    FilesSaveError,
    RequestDownloadError,
)
from src.launcher.utility.file_downloader import FileDownloader


@pytest.fixture
def mock_requests_response():
    """Mock a requests response object."""
    response = MagicMock()
    response.content = b"Mocked file content"
    response.raise_for_status.side_effect = None  # No exception for success
    return response


@pytest.fixture
def mock_yos_response():
    """Mock an yos response object."""
    response = MagicMock()
    response.read.return_value = b"Mocked file content"
    return response


@pytest.fixture
def mock_file_content():
    """Mock file content."""
    return b"Mocked file content"


def test_download_file_from_url_success(mock_requests_response):
    """Test downloading a file from a URL successfully."""
    download_url = "http://example.com/test_file.txt"

    # Patching requests.get() to return the mock response
    with patch(
        "requests.get", return_value=mock_requests_response
    ) as mock_get:
        file_content = FileDownloader.download_file_from_url(download_url)

    assert file_content == b"Mocked file content"
    mock_get.assert_called_once_with(download_url, timeout=10)


def test_download_file_from_url_http_error(mock_requests_response):
    """Test handling HTTP errors during file download."""
    download_url = "http://example.com/nonexistent_file.txt"
    mock_requests_response.raise_for_status.side_effect = requests.HTTPError(
        "404 Client Error"
    )

    # Patching requests.get() to return the mock response with HTTP error
    with patch(
        "requests.get", return_value=mock_requests_response
    ) as mock_get:
        with pytest.raises(RequestDownloadError):
            FileDownloader.download_file_from_url(download_url)

    mock_get.assert_called_once_with(download_url, timeout=10)


def test_download_file_from_yos_success(mock_yos_response):
    """Test downloading a file from S3 successfully."""
    bucket_name = "test-bucket"
    object_key = "test-object-key"
    boto3_client = MagicMock()
    boto3_client.get_object.return_value = {"Body": mock_yos_response}

    file_content = FileDownloader.download_file_from_yos(
        boto3_client, bucket_name, object_key
    )

    assert file_content == b"Mocked file content"
    boto3_client.get_object.assert_called_once_with(
        Bucket=bucket_name, Key=object_key
    )


def test_download_file_from_yos_boto3_error():
    """Test handling Boto3 errors during file download."""
    bucket_name = "test-bucket"
    object_key = "test-object-key"
    boto3_client = MagicMock()
    boto3_client.get_object.side_effect = boto3.exceptions.Boto3Error(
        "Connection error"
    )

    with pytest.raises(RequestDownloadError):
        FileDownloader.download_file_from_yos(
            boto3_client, bucket_name, object_key
        )

    boto3_client.get_object.assert_called_once_with(
        Bucket=bucket_name, Key=object_key
    )


def test_save_file_success(tmp_path, mock_file_content):
    """Test saving file content successfully."""
    file_path = os.path.join(tmp_path, "temp_dir", "test_file.txt")

    FileDownloader.save_file(file_path, mock_file_content)

    assert os.path.exists(file_path)
    with open(file_path, "rb") as file:
        assert file.read() == mock_file_content


def test_save_file_failure(tmp_path, mock_file_content):
    """Test handling file saving failure."""
    file_path = os.path.join(tmp_path, "temp_dir", "test_file.txt")

    # Patching open to raise an exception
    with patch("builtins.open", side_effect=Exception("File write error")):
        with pytest.raises(FilesSaveError):
            FileDownloader.save_file(file_path, mock_file_content)

    # Verify that the file was not created
    assert not os.path.exists(file_path)
