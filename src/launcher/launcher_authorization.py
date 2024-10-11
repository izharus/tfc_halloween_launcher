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
from typing import Optional

import requests
from loguru import logger as log
from pydantic import ValidationError
from qtpy.QtCore import QThread

from .utility.custom_exceptions import (
    AuthDataNotSet,
    AuthenticationServiceUnavailable,
    Base64ParsingError,
    InternalAuthenticationError,
    InvalidAuthenticationResponse,
    InvalidUserNameOrPassword,
)
from .utility.pydantic_models import AuthData


def authenticate_user(
    login_api_url: str, username: str, password: str
) -> AuthData:
    """
    Authenticate a user using the provided username and password.

    Args:
        login_api_url (str): Api url for login response.
        username (str): The username for authentication.
        password (str): The password for authentication.


    Returns:
        AuthData: Extracted response data.

    Raises:
        AuthenticationServiceUnavailable:
            If the authentication service is unavailable.
        InvalidAuthenticationResponse:
            If the authentication response is invalid.
        InvalidUserNameOrPassword:
            If user authentication fails with a 401 status code.
        InternalAuthenticationError:
            If authentication fails due internal error.
    """
    try:

        log.info(f"Authentication attempt : {username}.")
        response = requests.post(
            login_api_url,
            json={
                "username": username,
                "password": password,
            },
            timeout=10,
        )
    except requests.RequestException as error:
        raise AuthenticationServiceUnavailable() from error

    code = response.status_code
    if code == 200:
        try:
            return AuthData.model_validate(response.json())
        except (requests.exceptions.JSONDecodeError, ValidationError) as error:
            raise InvalidAuthenticationResponse(
                "Failed to handle response."
            ) from error

    elif code == 401:
        raise InvalidUserNameOrPassword()
    else:
        raise InternalAuthenticationError(f"Unexpected response code: {code}")


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
            raise AuthenticationServiceUnavailable() from error
        if response.status_code == 200:
            log.info(f"_push_skin success: {self._username}.")
        elif response.status_code == 401:
            log.error(f"Failed to _push_skin with 401 code: {self._username}")
            raise InvalidUserNameOrPassword()
        elif response.status_code == 500:
            log.error(f"Failed to _push_skin with 500 code: {self._username}")
            raise InternalAuthenticationError()
        else:
            log.error(
                "Failed to _authenticate_user with unexpected"
                f" {response.status_code}: {self._username}"
            )
            raise InternalAuthenticationError(f"{response.status_code}")

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
            AuthenticationServiceUnavailable,
            InvalidUserNameOrPassword,
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
