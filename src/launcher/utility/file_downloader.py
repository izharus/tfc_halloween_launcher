"""
This module implements a simple class of utility functions
for safe downloading of files.
"""

import hashlib
from os import PathLike
from pathlib import Path
from typing import Callable, Optional, Protocol, Union

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
from .pydantic_models import HashInfo


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

    except OSError as error:
        raise FilesSaveError from error



class DownloadProgress:
    """
    A helper class to manage and update download progress
    values for a UI component.

    Attributes:
        set_current (Callable[[int], None]): A function to set
            the current progress value.
        set_maximum (Callable[[int], None]): A function to set
            the maximum value of the progress.

    Methods:
        current(int): Updates the current progress value.
        maximum(int): Updates the maximum progress value.
    """
    def __init__(
        self,
        set_current: Callable[[int], None],
        set_maximum: Callable[[int], None],
    ):
        """
        Initializes the DownloadProgress with functions
        to set maximum and current progress values.

        Args:
            set_maximum (Callable[[int], None]): A function
                to set the maximum value of the progress.
            set_current (Callable[[int], None]): A function
                to set the current value of the progress.
        """
        self._set_current = set_current
        self._set_maximum = set_maximum
        self._current = 0
        self._maximum = 0

    @property
    def current(self) -> None:
        """Returns the current status"""
        return self._current

    @property
    def maximum(self) -> None:
        """Returns the current maximum"""
        return self._maximum

    @current.setter
    def current(self, current: int) -> None:
        """Updates the current progress value."""
        self._current = current
        self._set_current(self._current)

    @maximum.setter
    def maximum(self, maximum: int) -> None:
        """Updates the maximum progress value."""
        self._maximum = maximum
        self._set_maximum(self._maximum)

class FileDownloaderProtocol(Protocol):
    """Protocol for defining a file downloader interface."""

    def download_file(
        self,
        object_key: str,
        dst_path: Union[str, PathLike],
        hash_info: Optional[HashInfo] = None,
        callback: Optional[DownloadProgress] = None,
    ) -> None:
        """
        Downloads a file from S3 and saves it to the specified
        destination path.

        Args:
            object_key (str): The key of the object in the S3 bucket
                to be downloaded.
            dst_path (Union[str, PathLike]): The local path where
                the file will be saved.
            hash_info (Optional[HashInfo]): An instance of HashInfo
                containing the expected hash value
                and the hash algorithm for verification. If None,
                    the hash check is skipped.
            callback (Optional[DownloadProgress]): An optional
                DownloadProgress instance to track download
                progress, receiving the bytes downloaded and
                total file size.

        Raises:
            FileHashMismatchError: If the downloaded file's hash does
                not match the  expected hash after the download.
            CalculateHashFailed: If the hash calculation fails
                during the hash check.
        """

    def download_bytes(
        self,
        object_key: str,
        callback: Optional[DownloadProgress] = None,
    ) -> bytes:
        """
        Download a file from the S3 bucket and return bytes.

        Args:
            object_key (str): The key of the object to download.
            dst_path (str): The path where the file will be saved.
            callback (Optional[DownloadProgress]): An optional
                DownloadProgress instance to track download
                progress, receiving the bytes downloaded and
                total file size.

        Returns:
            bytes: The content of the downloaded file.

        Raises:
            FileDownloadError : If there's any error occurs
                during file download.
        """

    def get_hash(
        self,
        object_key: str,
    ) -> str:
        """
        Retrieves the md5 hash (ETag) of an object from an S3 bucket.

        Args:
            object_key (str): The key of the object in the S3 bucket whose
                hash is to be retrieved.

        Returns:
            str: The ETag of the object, which serves as a hash
                representation.

        Raises:
            FileDownloadError: If the file cannot be downloaded
                from S3 due to connectivity issues or other exceptions.
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
        callback: Optional[DownloadProgress] = None,
        chunk_size: int = 1024 * 1024,
    ) -> bytes:
        try:
            response = self._boto3_client.get_object(
                Bucket=self._bucket_name,
                Key=object_key,
            )
            if callback:
                callback.maximum =  response["ContentLength"]

            data = b""
            while chunk := response["Body"].read(chunk_size):
                data += chunk
                if callback:
                    callback.current = len(data)

            return data

        except Exception as e:
            raise FileDownloadError(
                f"Failed to download file from S3: {e}"
            ) from e

    def get_hash(
        self,
        object_key: str,
    ) -> str:
        try:
            response = self._boto3_client.get_object(
                Bucket=self._bucket_name,
                Key=object_key,
            )
            return response["ETag"].strip('"')
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
        hash_info: Optional[HashInfo] = None,
        callback: Optional[DownloadProgress] = None,
    ) -> None:
        filepath = Path(dst_path)
        if hash_info and filepath.exists():
            log.debug(f"File exists: {filepath}")
            try:
                if hash_info.value == calculate_hash(
                    filepath, hash_info.algorithm
                ):
                    log.debug(f"File hash correct: {filepath}")
                    if callback:
                        callback.maximum = 1
                        callback.current = 1
                    return
                else:
                    log.error(f"File hash incorrect: {filepath}")
            except CalculateHashFailed:
                log.error(f"Failed to calculate hash: {filepath}")
        save_file(
            file_content=self.download_bytes(object_key, callback=callback),
            file_path=dst_path,
        )
        log.debug(f"File was downloaded: {filepath}")
        if hash_info and hash_info.value != calculate_hash(
            filepath, hash_info.algorithm
        ):
            log.debug(f"File hash incorrect after download: {filepath}")
            raise FileHashMismatchError
