"""
This module implements a simple class of utillity functions
for safe downloading of files.
"""
import hashlib
import os

import requests

from .custom_exceptions import (
    CalculateHashFailed,
    FilesSaveError,
    RequestDownloadError,
)


class FileDownloader:
    """This class contains modules for safe downloading files."""

    @staticmethod
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

    @staticmethod
    def download_file(download_url: str) -> bytes:
        """
        Download a file from the given URL.

        Args:
            download_url (str): The URL from which to
                download the file.

        Returns:
            bytes: The content of the downloaded file.
        Raises:
            RequestDownloadError: If there's an HTTP error
                during file download.
        """
        try:
            response = requests.get(download_url, timeout=10)
            response.raise_for_status()
            return response.content
        except Exception as error:
            raise RequestDownloadError from error

    @staticmethod
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
