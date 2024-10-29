"""
This module implements a simple class of utility functions
for safe downloading of files.
"""

import hashlib
import os
from os import PathLike
from pathlib import Path
from typing import Protocol, Union

import boto3
import boto3.exceptions
from loguru import logger as log

from .custom_exceptions import (
    CalculateHashFailed,
    DownloadServerHandshakeError,
    FileDownloadError,
    FileHashMismatchError,
    FilesSaveError,
)


def calculate_hash(
        file_name: Union[str, PathLike],
        hash_algorithm="sha256",
        ) -> str:
    """Calculates the hash of a file using the specified hash algorithm.

    Args:
        file_name (str): The path to the file whose hash needs
            to be calculated.
        hash_algorithm (str, optional): The name of the hash algorithm to use 
            (e.g., 'sha256', 'md5'). Defaults to 'sha256'.

    Returns:
        str: The hexadecimal representation of the calculated hash.

    Raises:
        CalculateHashFailed: If an error occurs while calculating the hash.
        
    Example:
        >>> calculate_hash("example.txt", "md5")
        'd41d8cd98f00b204e9800998ecf8427e'
    """
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
    file_path: Union[str, PathLike],
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
        file = Path(file_path)
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(file_content)

    except Exception as error:
        raise FilesSaveError from error


class FileDownloaderProtocol(Protocol):
    """Protocol for defining a file downloader interface."""

    def download_file(
        self,
        object_key: str,
        dst_path: str,
        filehash: str,
        hash_algorithm: str = "sha256",
    ) -> None:
        """
        Download and save a file, with integrity verification using a hash.

        If the file already exists at the specified path, its hash is verified
        against the provided `filehash`. If the hash is incorrect, the file
        is re-downloaded. If, after re-downloading, the file's hash still does
        not match, an exception is raised.

        Args:
            object_key (str): The key of the object to download.
            dst_path (str): The path where the file will be saved.
            filehash (str): The expected hash of the file for integrity
                verification.
            hash_algorithm (str, optional): The hashing algorithm to use
                for verification (e.g., "md5", "sha256"). Default is "sha256".

        Raises:
            FileDownloadError: If an error occurs during file download.
            FileSaveError: If there is an error while saving the file.
            FileHashMismatchError: If the file's hash does not match
                `filehash` after re-downloading.
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
        dst_path: Union[str, PathLike],
        filehash: str,
        hash_algorithm: str = "sha256",
    ) -> None:
        
        filepath = Path(dst_path)
        s  = filepath.absolute()
        if filepath.exists():
            log.debug(f"File exists: {filepath}")
            try:
                if filehash == calculate_hash(filepath, hash_algorithm):
                    log.debug(f"File hash correct: {filepath}")
                    return
                else:
                    log.error(f"File hash incorrect: {filepath}")
            except CalculateHashFailed:
                log.error(f"Failed to calculate hash: {filepath}")
        save_file(
            file_content=self.download_bytes(object_key),
            file_path=dst_path,
        )
        log.debug(f"File was downloaded: {filepath}")
        if filehash != calculate_hash(filepath, hash_algorithm):
            log.debug(f"File hash incorrect after download: {filepath}")
            raise FileHashMismatchError
