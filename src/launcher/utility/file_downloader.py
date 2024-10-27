"""
This module implements a simple class of utility functions
for safe downloading of files.
"""

import hashlib
import os
from typing import Protocol

import boto3
import boto3.exceptions

from .custom_exceptions import (
    CalculateHashFailed,
    DownloadServerHandshakeError,
    FileDownloadError,
    FilesSaveError,
)


def calculate_hash(file_name, hash_algorithm="sha256"):
    """Calculate the hash of a file using the specified hash algorithm."""
    try:
        # Create a hash object based on the specified algorithm
        hasher = hashlib.new(hash_algorithm)

        # Open the file in binary mode for reading
        with open(file_name, "rb") as file:
            while True:
                # Read the file in small chunks to conserve memory
                chunk = file.read(4096)
                if not chunk:
                    break
                hasher.update(chunk)

        # Return the hexadecimal representation of the hash
        return hasher.hexdigest()
    except Exception as error:
        raise CalculateHashFailed() from error


def save_file(
    file_path: str,
    file_content: bytes,
) -> None:
    """
    Save file content to the specified file path.

    Args:
        file_path (str): The path where the file will be saved.
        file_content (bytes): The content of the file to be saved.

    Returns:
        None
    Raises:
        FilesSaveError: If there's an error while saving the file.
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as file:
            file.write(file_content)
    except Exception as error:
        raise FilesSaveError from error


class FileDownloaderProtocol(Protocol):
    """Protocol for defining a file downloader interface."""

    def download_file(self, object_key: str, dst_path: str) -> None:
        """
        Download and save file.

        Args:
            object_key (str): The key of the object to download.
            dst_path (str): The path where the file will be saved.

        Returns:
            bytes: The content of the downloaded file.
        Raises:
            FileDownloadError : If there's any error occurs
                during file download.
            FilesSaveError: If there's an error while saving the file.
        """

    def download_bytes(
        self,
        object_key: str,
    ) -> bytes:
        """
        Download a file from the S3 bucket and return bytes.

        Args:
            object_key (str): The key of the object to download.
            dst_path (str): The path where the file will be saved.

        Returns:
            bytes: The content of the downloaded file.

        Raises:
            FileDownloadError : If there's any error occurs
                during file download.
        """


class FileYOSDownloader(FileDownloaderProtocol):
    """
    Initializes the FileYOSDownloader with AWS credentials and settings.
    """

    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        bucket_name: str,
    ):
        """
        Initializes the FileYOSDownloader with the necessary
        AWS S3 settings.

        Args:
            aws_access_key_id (str): AWS access key ID for authenticating
                requests.
            aws_secret_access_key (str): AWS secret access key for securing
                requests.
            bucket_name (str): The name of the S3 bucket to interact with.

        Raises:
            DownloadServerHandshakeError: If there's an issue connecting
                to the S3 server.
        """
        endpoint_url = "https://storage.yandexcloud.net"
        self._bucket_name = bucket_name
        try:
            self._boto3_client = boto3.client(
                "s3",
                endpoint_url=endpoint_url,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
            )
        except boto3.exceptions.Boto3Error as error:
            raise DownloadServerHandshakeError from error

    def download_bytes(
        self,
        object_key: str,
    ) -> bytes:
        """
        Download a file from the S3 bucket and return bytes.

        Args:
            object_key (str): The key of the object to download.

        Returns:
            bytes: The content of the downloaded file.

        Raises:
            FileDownloadError : If there's any error occurs
                during file download.
        """
        try:
            response = self._boto3_client.get_object(
                Bucket=self._bucket_name,
                Key=object_key,
            )
            return response["Body"].read()
        # boto3.exceptions.Boto3Error do not catches
        # exceptions if ethernet connection was lost
        except Exception as e:
            raise FileDownloadError(
                f"Failed to download file from S3: {e}"
            ) from e

    def download_file(
        self,
        object_key: str,
        dst_path: str,
    ) -> None:
        """
        Download a file from the S3 bucket and saves it to the dst_path.

        Args:
            object_key (str): The key of the object to download.
            dst_path (str): The path where the file will be saved.

        Returns:
            None.
        Raises:
            FileDownloadError : If there's any error occurs
                during file download.
            FilesSaveError: If there's an error while saving the file.
        """
        save_file(
            file_content=self.download_bytes(object_key),
            file_path=dst_path,
        )
