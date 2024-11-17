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

from .utility.custom_exceptions import (
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


class SkinUploader:
    """
    A thread class for uploading Minecraft skins and capes.
    """

    def __init__(
        self,
        username: str,
        password: str,
        push_skin_api_url: str,
        push_cape_api_url: str,
    ) -> None:
        """
        Initializes the user credentials and API URLs for pushing
        skins and capes.

        Args:
            username (str): The username of the user.
            password (str): The password associated with the username.
            push_skin_api_url (str): The API URL for pushing skins.
            push_cape_api_url (str): The API URL for pushing capes.
        """
        self._push_skin_api_url = push_skin_api_url
        self._push_cape_api_url = push_cape_api_url
        self._username = username
        self._password = password

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

    def _make_json_response(
        self, base64_img: Optional[str] = None, is_skin_slim: bool = False
    ):
        """
        Create a JSON response for the skin upload API.

        Args:
            base64_img (Optional, str): The base64-encoded string of
                the user's skin.
            is_skin_slim (bool): True is skin is slim, False otherwise.

        Returns:
            dict: A dictionary representing the JSON response.

        """
        return {
            "username": self._username,
            "password": self._password,
            "base64_image": base64_img,
            "is_skin_slim": is_skin_slim,
        }

    def _push_img(
        self,
        api_url: str,
        selected_skin_path: Optional[str] = None,
        is_skin_slim: bool = False,
    ) -> None:
        """
        Pushes a skin image to the specified API URL.

        Args:
            api_url (str): The URL of the API to which the skin image
                should be pushed.
            selected_skin_path (Optional[str], optional): The file path
                of the skin image. If None, the behavior will depend on
                the implementation of `get_base64_string_from_file`.
                Defaults to None.
            is_skin_slim (bool, optional): Indicates whether the skin is
                slim (True) or regular (False). Defaults to False.

        Raises:
            Base64ParsingError: If there is an error parsing the image
                file into a Base64 string.
            AuthenticationServiceUnavailable: If the request to the API
                fails due to an unavailable authentication service.
            InvalidUserNameOrPassword: If the response status code is
                401, indicating invalid credentials.
            InternalAuthenticationError: If the response status code is
                500 or any other unexpected status code.
        """

        base64_img = self.get_base64_string_from_file(
            filepath=selected_skin_path,
        )
        try:
            response = requests.post(
                api_url,
                json=self._make_json_response(
                    base64_img=base64_img,
                    is_skin_slim=is_skin_slim,
                ),
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

    def push_skin(
        self,
        selected_skin_path: Optional[str] = None,
        is_skin_slim: bool = False,
    ) -> None:
        """
        Pushes a skin image to the configured skin API URL.

        Args:
            selected_skin_path (Optional[str], optional): The file path
                of the skin image to be pushed. If None, the behavior
                will depend on the implementation of `_push_img`.
                Defaults to None.
            is_skin_slim (bool, optional): Indicates whether the skin
                is slim (True) or regular (False). Defaults to False.

        Raises:
            Base64ParsingError: If there is an error parsing the image
                file into a Base64 string.
            AuthenticationServiceUnavailable: If the request to the API
                fails due to an unavailable authentication service.
            InvalidUserNameOrPassword: If the response status code is
                401, indicating invalid credentials.
            InternalAuthenticationError: If the response status code
                is 500 or any other unexpected status code.
        """
        self._push_img(
            api_url=self._push_skin_api_url,
            selected_skin_path=selected_skin_path,
            is_skin_slim=is_skin_slim,
        )

    def push_cape(
        self,
        selected_skin_path: Optional[str] = None,
        is_skin_slim: bool = False,
    ) -> None:
        """
        Pushes a cape image to the configured cape API URL.

        Args:
            selected_skin_path (Optional[str], optional): The file path
                of the cape image to be pushed. If None, the behavior
                will depend on the implementation of `_push_img`.
                Defaults to None.
            is_skin_slim (bool, optional): Indicates whether the skin
                is slim (True) or regular (False). Defaults to False.
        Raises:
            Base64ParsingError: If there is an error parsing the image
                file into a Base64 string.
            AuthenticationServiceUnavailable: If the request to the API
                fails due to an unavailable authentication service.
            InvalidUserNameOrPassword: If the response status code is
                401, indicating invalid credentials.
            InternalAuthenticationError: If the response status code
                is 500 or any other unexpected status code.
        """
        self._push_img(
            api_url=self._push_cape_api_url,
            selected_skin_path=selected_skin_path,
            is_skin_slim=is_skin_slim,
        )
