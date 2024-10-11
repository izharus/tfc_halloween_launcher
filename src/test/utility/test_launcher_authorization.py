"""Tests for src/launcher/launcher_authorization.py"""

# pylint:disable = E0401
import os
from unittest.mock import MagicMock

import pytest
import requests
import requests_mock
from src.launcher import launcher_authorization, launcher_configs
from src.launcher.launcher_authorization import authenticate_user
from src.launcher.utility.custom_exceptions import (
    AuthenticationServiceUnavailable,
    InternalAuthenticationError,
    InvalidAuthenticationResponse,
    InvalidUserNameOrPassword,
)
from src.launcher.utility.pydantic_models import AuthResponse


def test_authenticate_user_service_unavailable(mocker):
    """
    Test AuthorizationThread for AuthorizationServiceUnavailable during
    authorization service unavailability.
    """
    # Mock the requests.post method
    mocker.patch(
        "requests.post",
        side_effect=requests.exceptions.ConnectTimeout,
    )
    with pytest.raises(AuthenticationServiceUnavailable):
        authenticate_user("url", "login", "pass")


def test_authenticate_user_success():
    """Test authenticate_user for a successful authentication."""
    config = MagicMock()
    config.minecraft_launcher_ip_addr = "https://test_api_url"

    json_ans = {
        "status": "status",
        "username": "username",
        "uuid": "uuid",
        "accessToken": "accessToken",
    }
    with requests_mock.Mocker() as m:
        # Mock the requests.post method for success (status code 200)
        m.post(
            config.minecraft_launcher_ip_addr,
            json=json_ans,
            status_code=200,
        )
        auth_data = authenticate_user(
            config.minecraft_launcher_ip_addr,
            "login",
            "pass",
        )

        # pylint: disable=W0212
    assert isinstance(auth_data, AuthResponse)
    assert auth_data == AuthResponse(**json_ans)


def test_authenticate_user_unauthorized():
    """
    Test authenticate_user for an unauthorized authentication
    (status code 401).
    """
    config = MagicMock()
    config.minecraft_launcher_ip_addr = "https://test_api_url"

    with requests_mock.Mocker() as m:
        # Mock the requests.post method for unauthorized (status code 401)
        m.post(config.minecraft_launcher_ip_addr, status_code=401)

        # Call the internal method and assert it raises the expected exception
        with pytest.raises(InvalidUserNameOrPassword):
            # pylint: disable=W0212
            authenticate_user(
                config.minecraft_launcher_ip_addr, "test_user", "test_password"
            )


def test_authenticate_user_internal_error():
    """
    Test authenticate_user for an internal server error
    (status code 500).
    """
    config = MagicMock()
    config.minecraft_launcher_ip_addr = "https://test_api_url"

    with requests_mock.Mocker() as m:
        # Mock the requests.post method for internal server
        # error (status code 500)
        m.post(config.minecraft_launcher_ip_addr, status_code=500)

        # Call the internal method and assert it raises the expected exception
        with pytest.raises(launcher_authorization.InternalAuthenticationError):
            authenticate_user(
                config.minecraft_launcher_ip_addr,
                "login",
                "pass",
            )


def test_authenticate_user_unexpected_error():
    """Test authenticate_user for an unexpected error
    (other status code)."""
    config = MagicMock()
    config.minecraft_launcher_ip_addr = "https://test_api_url"

    with requests_mock.Mocker() as m:
        # Mock the requests.post method for an unexpected status code
        m.post(config.minecraft_launcher_ip_addr, status_code=403)

        # Call the internal method and assert it raises the expected exception
        with pytest.raises(InternalAuthenticationError) as exc_info:
            authenticate_user(
                config.minecraft_launcher_ip_addr,
                "login",
                "pass",
            )

        assert "403" in repr(exc_info)


def test_authenticate_user_invalid_json_data_type(mocker):
    """Test authenticate_user for a successful authentication."""
    config = MagicMock()
    config.minecraft_launcher_ip_addr = "https://test_api_url"
    response_json = ["invalid_json_type"]
    mock_response = mocker.Mock(spec=requests.Response)
    with mocker.patch.object(
        mock_response, "json", return_value=response_json
    ):
        with requests_mock.Mocker() as m:
            # Mock the requests.post method for an unexpected status code
            m.post(config.minecraft_launcher_ip_addr, status_code=200)
            with pytest.raises(InvalidAuthenticationResponse):
                authenticate_user(
                    config.minecraft_launcher_ip_addr,
                    "login",
                    "pass",
                )


def test_authenticate_user_with_invalid_response_json_data(mocker):
    """
    Test authenticate_user when json response contains invalid field name.
    """
    config = MagicMock()
    config.minecraft_launcher_ip_addr = "https://test_api_url"
    response_json = {
        "status": "OK",
        "invalid_username": "test_username",
        "uuid": "uuid",
        "accessToken": "token",
    }
    mock_response = mocker.Mock(spec=requests.Response)
    with mocker.patch.object(
        mock_response, "json", return_value=response_json
    ):
        with requests_mock.Mocker() as m:
            # Mock the requests.post method for an unexpected status code
            m.post(config.minecraft_launcher_ip_addr, status_code=200)
            with pytest.raises(InvalidAuthenticationResponse):
                authenticate_user(
                    config.minecraft_launcher_ip_addr,
                    "login",
                    "pass",
                )


def test_successful_skin_upload():
    """Test successful Minecraft skin upload."""
    script_directory = os.path.dirname(os.path.abspath(__file__))
    api_url = launcher_configs.LauncherConfig.MINECRAFT_LAUNCHER_IP_ADDR
    with requests_mock.Mocker() as m:
        # Mock the requests.post method for success (status code 200)
        m.post(
            api_url,
            status_code=200,
        )

        # Create an instance of SkinUploaderThread
        skin_thread = launcher_authorization.SkinUploaderThread(api_url)

        # Set data for skin upload
        skin_thread.set_data(
            username="test_user",
            password="test_password",
            selected_skin_path=f"{script_directory}/test_skin.png",
        )

        # Run the thread
        skin_thread.start()
        # Wait for the thread to finish
        skin_thread.wait(1000)
        # Check if runtime_error is None
        assert skin_thread.runtime_error is None


def test_make_json_response():
    """Tests if json creates correctly."""
    script_directory = os.path.dirname(os.path.abspath(__file__))
    api_url = launcher_configs.LauncherConfig.MINECRAFT_LAUNCHER_IP_ADDR

    # Create an instance of SkinUploaderThread
    skin_thread = launcher_authorization.SkinUploaderThread(api_url)

    # Set data for skin upload
    skin_thread.set_data(
        username="test_user",
        password="test_password",
        selected_skin_path=f"{script_directory}/test_skin.png",
        is_skin_slim=True,  # You can set is_skin_slim to True for testing
    )

    # Call the _make_json_response method
    # pylint: disable = W0212
    json_response = skin_thread._make_json_response("test_base64_img")

    # Validate the structure and content of the JSON response
    expected_json = {
        "username": "test_user",
        "password": "test_password",
        "base64_image": "test_base64_img",
        "is_skin_slim": True,
    }

    assert json_response == expected_json


def test_skin_upload_with_invalid_skin_path():
    """Test skin upload with an invalid skin path."""
    api_url = launcher_configs.LauncherConfig.MINECRAFT_LAUNCHER_IP_ADDR
    # Create an instance of SkinUploaderThread
    skin_thread = launcher_authorization.SkinUploaderThread(api_url)
    with requests_mock.Mocker() as m:
        # Mock the requests.post method for success (status code 200)
        m.post(
            api_url,
            status_code=401,
        )
        # Set data for skin upload
        skin_thread.set_data(
            username="test_user",
            password="test_password",
            selected_skin_path="invalid_path",
        )

        # Run the thread
        skin_thread.start()
        # Wait for the thread to finish
        skin_thread.wait(1000)
        # Check if runtime_error is None
        assert isinstance(
            skin_thread.runtime_error,
            launcher_authorization.Base64ParsingError,
        )


def test_skin_upload_with_invalid_auth_data():
    """Test skin upload with an invalid auth data."""
    api_url = launcher_configs.LauncherConfig.MINECRAFT_LAUNCHER_IP_ADDR
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # Create an instance of SkinUploaderThread
    skin_thread = launcher_authorization.SkinUploaderThread(api_url)
    with requests_mock.Mocker() as m:
        # Mock the requests.post method for success (status code 200)
        m.post(
            api_url,
            status_code=401,
        )
        # Set data for skin upload
        skin_thread.set_data(
            username="test_user",
            password="test_password",
            selected_skin_path=f"{script_directory}/test_skin.png",
        )

        # Run the thread
        skin_thread.start()
        # Wait for the thread to finish
        skin_thread.wait(1000)
        # Check if runtime_error is None
        assert isinstance(
            skin_thread.runtime_error,
            launcher_authorization.InvalidUserNameOrPassword,
        )


def test_skin_upload_with_invalid_api_response_code():
    """Test skin upload with an invalid API response status code."""
    api_url = launcher_configs.LauncherConfig.MINECRAFT_LAUNCHER_IP_ADDR
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # Create an instance of SkinUploaderThread
    skin_thread = launcher_authorization.SkinUploaderThread(api_url)
    with requests_mock.Mocker() as m:
        # Mock the requests.post method for success (status code 200)
        m.post(
            api_url,
            status_code=501,
        )
        # Set data for skin upload
        skin_thread.set_data(
            username="test_user",
            password="test_password",
            selected_skin_path=f"{script_directory}/test_skin.png",
        )

        # Run the thread
        skin_thread.start()
        # Wait for the thread to finish
        skin_thread.wait(1000)
        # Check if runtime_error is None
        assert isinstance(
            skin_thread.runtime_error,
            launcher_authorization.InternalAuthenticationError,
        )


def test_skin_upload_with_unavailable_authorization_service():
    """
    Test the behavior of skin upload when the authorization service
    is unavailable.
    """
    api_url = launcher_configs.LauncherConfig.MINECRAFT_LAUNCHER_IP_ADDR
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # Create an instance of SkinUploaderThread
    skin_thread = launcher_authorization.SkinUploaderThread(api_url)
    with requests_mock.Mocker() as m:
        # Mock the requests.post method for success (status code 200)
        m.post(api_url, exc=requests.exceptions.ConnectTimeout)
        # Set data for skin upload
        skin_thread.set_data(
            username="test_user",
            password="test_password",
            selected_skin_path=f"{script_directory}/test_skin.png",
        )

        # Run the thread
        skin_thread.start()
        # Wait for the thread to finish
        skin_thread.wait(1000)
        # Check if runtime_error is None
        assert isinstance(
            skin_thread.runtime_error,
            launcher_authorization.AuthenticationServiceUnavailable,
        )
