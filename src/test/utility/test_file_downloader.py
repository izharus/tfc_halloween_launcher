"""Unit tests for src/launcher/utility/file_downloader.py"""

# pylint: disable=W0201, W0212
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import boto3
import pytest
from pytest_mock import MockerFixture
from src.launcher.boto3_cred import BOTO3_ACCESS_KEY, BOTO3_SECRET_KEY
from src.launcher.launcher_configs import LauncherConfig
from src.launcher.utility import file_downloader
from src.launcher.utility.custom_exceptions import (
    FileDownloadError,
    FileHashMismatchError,
    FilesSaveError,
)
from src.launcher.utility.file_downloader import FileYOSDownloader, save_file
from src.launcher.utility.pydantic_models import HashInfo


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


class TestFileYOSDownloader:
    """Tests for FileYOSDownloader class."""

    def setup_method(self):
        """Initialize a file_downloader instance."""
        self.file_downloader = FileYOSDownloader(
            aws_access_key_id=BOTO3_ACCESS_KEY,
            aws_secret_access_key=BOTO3_SECRET_KEY,
            bucket_name=LauncherConfig.BUCKET_NAME,
        )

    def test_download_bytes_success(
        self,
    ):
        """Test downloading bytes from S3 successfully."""

        tmp_data = self.file_downloader.download_bytes(
            LauncherConfig.MAP_JSON_YOS_OBJ_KEY
        )

        assert isinstance(tmp_data, bytes)
        assert len(tmp_data) > 100

    def test_download_file_boto3_error(self):
        """Test handling Boto3 errors during file download."""
        bucket_name = LauncherConfig.BUCKET_NAME
        object_key = "test-object-key"
        boto3_client = MagicMock()
        boto3_client.get_object.side_effect = boto3.exceptions.Boto3Error(
            "Connection error"
        )
        self.file_downloader._boto3_client = boto3_client
        with pytest.raises(FileDownloadError):
            self.file_downloader.download_file(
                object_key, "mock_path", "mock_filehash"
            )

        self.file_downloader._boto3_client.get_object.assert_called_once_with(
            Bucket=bucket_name, Key=object_key
        )

    def test_download_file_file_system_error(self):
        """Test handling Boto3 errors during file download."""
        object_key = "test-object-key"
        boto3_client = MagicMock()
        self.file_downloader._boto3_client = boto3_client
        with pytest.raises(FilesSaveError):
            self.file_downloader.download_file(
                object_key, "unknown_path", "mock_filehash"
            )

    def test_download_file_hash_mismatch(
        self,
        mocker: MockerFixture,
        tmp_path: Path,
    ):
        """Test handling file hash mismatch after download."""
        object_key = "test-object-key"
        dst_path = tmp_path / "file"
        correct_hash_info = HashInfo(
            value="correct_hash",
            algorithm="sha256",
        )
        wrong_hash_info = HashInfo(
            value="wrong_hash",
            algorithm="sha256",
        )

        # Mocking download_bytes to return dummy content
        self.file_downloader.download_bytes = MagicMock(
            return_value=b"dummy data"
        )

        # Mocking save_file to simulate saving the file without error
        save_file_mock = MagicMock()

        # Patch the calculate_hash function to return the wrong hash on first call
        mock_hash = MagicMock()

        with mocker.patch.object(file_downloader, "calculate_hash", mock_hash):
            with mocker.patch.object(
                file_downloader, "save_file", save_file_mock
            ):
                mock_hash.return_value = wrong_hash_info.value

                with pytest.raises(FileHashMismatchError):
                    self.file_downloader.download_file(
                        object_key, dst_path, correct_hash_info
                    )

                save_file_mock.assert_called_once_with(
                    file_content=b"dummy data", file_path=dst_path
                )

    def test_download_file_success_with_correct_hash(
        self,
        mocker: MockerFixture,
        tmp_path: Path,
    ):
        """Test downloading a file successfully when the hash matches."""
        object_key = "test-object-key"
        dst_path = tmp_path / "file"
        correct_hash_info = HashInfo(
            value="correct_hash",
            algorithm="sha256",
        )
        # Mocking download_bytes to return dummy content
        self.file_downloader.download_bytes = MagicMock(
            return_value=b"dummy data"
        )

        # Mocking save_file to simulate saving the file without error
        save_file_mock = MagicMock()

        # Patch the calculate_hash function to return the correct hash
        mock_hash = MagicMock()

        with mocker.patch.object(file_downloader, "calculate_hash", mock_hash):
            with mocker.patch.object(
                file_downloader, "save_file", save_file_mock
            ):
                mock_hash.return_value = (
                    correct_hash_info.value  # Returns the correct hash
                )

                # Call the download_file method and check for exceptions
                self.file_downloader.download_file(
                    object_key, dst_path, correct_hash_info
                )

                # Ensure save_file was called with the expected arguments
                save_file_mock.assert_called_once_with(
                    file_content=b"dummy data", file_path=dst_path
                )


def test_save_file_success(tmp_path, mock_file_content):
    """Test saving file content successfully."""
    file_path = os.path.join(tmp_path, "temp_dir", "test_file.txt")

    save_file(file_path, mock_file_content)

    assert os.path.exists(file_path)
    with open(file_path, "rb") as file:
        assert file.read() == mock_file_content


def test_save_file_failure(tmp_path, mock_file_content):
    """Test handling file saving failure."""
    file_path = os.path.join(tmp_path, "temp_dir", "test_file.txt")

    # Patching open to raise an exception
    with patch("pathlib.Path.write_bytes", side_effect=Exception("File write error")):
        with pytest.raises(FilesSaveError):
            save_file(file_path, mock_file_content)

    # Verify that the file was not created
    assert not os.path.exists(file_path)
