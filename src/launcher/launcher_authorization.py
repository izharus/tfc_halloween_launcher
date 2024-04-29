"""
Module for user authorization in the launcher.

This module defines the `AuthorizationThread` class, a subclass of PyQt5's
QThread, which is designed to run in a separate thread to perform user
authentication using the provided username and password. It includes methods
for setting authentication data, getting the last authentication data, and
handling response validation.

Classes:
    AuthorizationThread: A thread class for making authorization requests.

Note: This module assumes the existence of certain classes and functions
      imported from other modules such as `MinecraftLauncherConfig`.
"""
import base64
import traceback
from typing import Dict, Optional

import requests
from loguru import logger as log
from PyQt6.QtCore import QThread

from .utility.custom_exceptions import (
    AuthDataNotSet,
    AuthorizationServiceUnavailable,
    Base64ParsingError,
    InternalAuthenticationError,
    InvalidAuthenticationResponseError,
    UserAuthenticationError,
)


class AuthorizationThread(QThread):
    """
    A thread class for making authorization requests.

    This class is designed to run in a separate thread to perform
    user authentication using the provided username and password.
    """

    def __init__(
        self,
        minecraft_launcher_ip_addr: str,
    ) -> None:
        """
        Initialize the AuthorizationThread instance.

        Args:
            minecraft_launcher_ip_addr (str): Api url for authorization.
        """
        QThread.__init__(self)
        self.minecraft_launcher_ip_addr = minecraft_launcher_ip_addr
        self.is_working = False
        self.runtime_error: Optional[Exception] = None

        self._username: Optional[str] = None
        self._password: Optional[str] = None
        self._last_auth_data: Optional[Dict[str, str]] = None

    def set_auth_data(self, username: str, password: str) -> None:
        """
        Set authentication data for the AuthorizationThread.

        Args:
            username (str): The username for authentication.
            password (str): The password for authentication.

        Returns:
            None
        """
        self._username = username
        self._password = password

    def get_last_auth_data(self) -> Optional[Dict]:
        """
        Get the last authentication data.

        Returns:
            Optional[Dict]: The last authentication data if available,
                otherwise None.
        """
        return self._last_auth_data

    @staticmethod
    def is_response_valid(response: requests.Response) -> bool:
        """
        Check if the response and its JSON data are valid.

        Args:
            response (requests.Response): The response object.

        Returns:
            bool: True if the response and JSON data are valid,
                False otherwise.
        """
        try:
            json_data = response.json()
        except Exception:
            log.error(
                "is_response_valid: failed to parse json data from response."
            )
            return False
        if not isinstance(json_data, dict):
            log.error(
                f"is_response_valid: invalid type of json data: {json_data}"
            )
            return False
        if (
            "status" not in json_data
            or "username" not in json_data
            or "uuid" not in json_data
            or "accessToken" not in json_data
        ):
            log.error(
                f"is_response_valid failed, response keys: {json_data.keys()}"
            )
            return False
        return True

    def _update_last_auth_data(self, response: requests.Response) -> None:
        """
        Update auth data with validated requests.Response.

        Args:
            response (requests.Response): The response object.

        Returns:
            None
        """
        self._last_auth_data = response.json()

    def _get_authenticate_response(
        self, username: str, password: str
    ) -> requests.Response:
        """
        Get the response object for user authentication.

        Args:
            username (str): The username for authentication.
            password (str): The password for authentication.

        Returns:
            requests.Response: The response object.

        Raises:
            AuthorizationServiceUnavailable: If the authentication service is
                unavailable.
            UserAuthenticationError: If user authentication fails with a 401
                status code.
            InternalAuthenticationError: If internal authentication fails
                with a 500 status code.
        """
        try:
            response = requests.post(
                self.minecraft_launcher_ip_addr,
                json={
                    "username": username,
                    "password": password,
                },
                timeout=10,
            )
        except Exception as error:
            log.error(f"_authenticate_user failed: {error}")
            log.debug(traceback.format_exc())
            raise AuthorizationServiceUnavailable() from error
        match response.status_code:
            case 200:
                log.info(f"_authenticate_user success: {username}.")
                return response
            case 401:
                log.error(
                    f"Failed to _authenticate_user with 401 code: {username}"
                )
                raise UserAuthenticationError()
            case 500:
                log.error(
                    f"Failed to _authenticate_user with 500 code: {username}"
                )
                raise InternalAuthenticationError()
            case code:
                log.error(
                    "Failed to _authenticate_user with unexpected"
                    f" {code}: {username}"
                )
                raise InternalAuthenticationError(error_code=code)

    def _authenticate_user(self, username: str, password: str) -> None:
        """
        Authenticate a user using the provided username and password.

        Args:
            username (str): The username for authentication.
            password (str): The password for authentication.

        Raises:
            AuthorizationServiceUnavailable:
                If the authentication service is unavailable.
            InvalidAuthenticationResponseError:
                If the authentication response is invalid.
            UserAuthenticationError:
                If user authentication fails with a 401 status code.
            InternalAuthenticationError:
                If internal authentication fails with a 500 status code.
        """
        response = self._get_authenticate_response(username, password)
        if not self.is_response_valid(response):
            raise InvalidAuthenticationResponseError
        self._last_auth_data = response.json()

    def run(self):
        """
        Entry point for QT start() method.

        This method is called when the thread starts running.
        """
        log.info("Authentication started.")
        if not self._username or not self._password:
            self.runtime_error = AuthDataNotSet()
            return
        self.runtime_error = None
        try:
            # Call get_auth_data within the thread
            self._authenticate_user(self._username, self._password)
            # if not self.is_response_valid()

        except (
            AuthorizationServiceUnavailable,
            UserAuthenticationError,
            InternalAuthenticationError,
            InvalidAuthenticationResponseError,
        ) as error:
            # Handle the AuthorizationServiceUnavailable exception
            self.runtime_error = error
        log.info(f"User authentication success: {self._username}")
        self.set_auth_data(None, None)


# pylint: disable = R0902
class SkinUploaderThread(QThread):
    """
    A thread class for uploading Minecraft skins.
    """

    def __init__(self, push_skin_api_url: str) -> None:
        QThread.__init__(self)
        self._push_skin_api_url = push_skin_api_url
        self._username: Optional[str] = None
        self._password: Optional[str] = None
        self._selected_skin_path: Optional[str] = None
        self._is_skin_slim: bool = False
        self._is_data_inited: bool = False
        self.runtime_error: Optional[Exception] = None

    @staticmethod
    def get_base64_string_from_file(filepath: Optional[str]) -> Optional[str]:
        """
        Read the binary content of an image file and return its
        base64-encoded string.
        """
        if not filepath:
            return None
        try:
            with open(filepath, "rb") as image_file:
                # Read the binary content of the image file
                image_binary = image_file.read()
                return base64.b64encode(image_binary).decode()
        except Exception as error:
            log.error(f"Unable to parse base64 string: {error}")
            log.debug(traceback.format_exc)
            raise Base64ParsingError() from error

    # pylint: disable = R0913
    def set_data(
        self,
        username: str,
        password: str,
        selected_skin_path: Optional[str] = None,
        is_skin_slim: bool = False,
    ) -> None:
        """
        Set data for the skin upload.
        """

        self._username = username
        self._password = password
        self._selected_skin_path = selected_skin_path
        self._is_data_inited = True
        self._is_skin_slim = is_skin_slim

    def _make_json_response(self, base64_img: Optional[str] = None):
        """
        Create a JSON response for the skin upload API.

        Args:
            base64_img (Optional, str): The base64-encoded string of
                the user's skin.

        Returns:
            dict: A dictionary representing the JSON response.

        """
        return {
            "username": self._username,
            "password": self._password,
            "base64_image": base64_img,
            "is_skin_slim": self._is_skin_slim,
        }

    def _push_skin(
        self,
        base64_img: Optional[str] = None,
    ) -> None:
        """
        Push the user's skin to the Minecraft server.

        Args:
            base64_img (Optional, str): The base64-encoded
                string of the user's skin.

        """
        try:
            response = requests.post(
                self._push_skin_api_url,
                json=self._make_json_response(base64_img),
                timeout=10,
            )
        except Exception as error:
            log.error(f"_authenticate_user failed: {error}")
            log.debug(traceback.format_exc())
            raise AuthorizationServiceUnavailable() from error
        match response.status_code:
            case 200:
                log.info(f"_push_skin success: {self._username}.")
            case 401:
                log.error(
                    f"Failed to _push_skin with 401 code: {self._username}"
                )
                raise UserAuthenticationError()
            case 500:
                log.error(
                    f"Failed to _push_skin with 500 code: {self._username}"
                )
                raise InternalAuthenticationError()
            case code:
                log.error(
                    "Failed to _authenticate_user with unexpected"
                    f" {code}: {self._username}"
                )
                raise InternalAuthenticationError(error_code=code)

    def run(self):
        """
        Entry point for QT start() method.

        This method is called when the thread starts running.
        """
        self.runtime_error = None
        if not self._is_data_inited:
            self.runtime_error = AuthDataNotSet()
            return
        try:
            # Call get_auth_data within the thread
            base64_string = self.get_base64_string_from_file(
                self._selected_skin_path
            )
            self._push_skin(base64_string)
            # if not self.is_response_valid()

        except (
            AuthorizationServiceUnavailable,
            UserAuthenticationError,
            InternalAuthenticationError,
            Base64ParsingError,
        ) as error:
            # Handle the AuthorizationServiceUnavailable exception
            self.runtime_error = error


class CapeUploaderThread(SkinUploaderThread):
    """
    A thread class for uploading Minecraft capes. Extends
    the functionality of the SkinUploaderThread class to
    handle cape-specific operations.
    """

    def set_data(
        self,
        username: str,
        password: str,
        selected_skin_path: Optional[str] = None,
        is_skin_slim: bool = False,
    ) -> None:
        """
        Set data for the cape upload.

        Args:
            username (str): The username associated with the cape.
            password (str): The password for authentication.
            selected_skin_path (Optional[str]): The file path to the
                selected cape skin.
            is_skin_slim (bool, optional): Flag indicating whether
                the cape skin is slim. It dont uses in the current class, only
                in super() class.

        Returns:
            None
        """

        self._username = username
        self._password = password
        self._selected_skin_path = selected_skin_path
        self._is_skin_slim = is_skin_slim
        self._is_data_inited = True

    def _make_json_response(self, base64_img: Optional[str] = None):
        """
        Create a JSON response for the cape upload API.

        Args:
            base64_img (Optional, str): The base64-encoded
                string of the user's cape.

        Returns:
            dict: A dictionary representing the JSON response.

        """
        return {
            "username": self._username,
            "password": self._password,
            "base64_image": base64_img,
        }
