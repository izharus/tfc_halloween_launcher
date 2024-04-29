"""Tests for src/launcher/launcher_authorization.py"""
# pylint:disable = E0401
import os
import secrets
from unittest.mock import MagicMock

import pytest
import requests
import requests_mock
from src.launcher import launcher_authorization, launcher_configs
from src.launcher.utility.custom_exceptions import (
    AuthDataNotSet,
    AuthorizationServiceUnavailable,
    InternalAuthenticationError,
    UserAuthenticationError,
)


def test_authorization_thread_inition():
    """Check if AuthorizationThread could be initialized correctly."""
    auth_class = launcher_authorization.AuthorizationThread(MagicMock())
    assert auth_class


def test_start_authorization_thread_without_setting_auth_data():
    """
    Test AuthorizationThread behavior when started without setting
    authentication data.
    """
    auth_class = launcher_authorization.AuthorizationThread(MagicMock())

    # Start the thread
    auth_class.start()  # i need to wait until auth_class finished

    # Wait for the thread to finish
    auth_class.wait(1000)

    # Assert that runtime_error is AuthDataNotSet
    assert isinstance(auth_class.runtime_error, AuthDataNotSet)
    assert str(auth_class.runtime_error) == str(AuthDataNotSet())


def test_authorization_thread_check_if_auth_data_resets(mocker):
    """
    Test AuthorizationThread behavior with authentication data reset
    between runs.
    """

    # pylint: disable=C0301
    mocker.patch(
        "src.launcher.launcher_authorization.AuthorizationThread._authenticate_user",
        return_value=None,
    )

    auth_class = launcher_authorization.AuthorizationThread(MagicMock())
    auth_class.set_auth_data("test_user", "test_password")

    # Start the thread
    auth_class.start()
    # Wait for the thread to finish
    auth_class.wait(1000)

    # First call should be successful
    assert auth_class.runtime_error is None

    # Start the thread
    auth_class.run()
    auth_class.wait(1000)
    # Assert that runtime_error is AuthDataNotSet
    assert isinstance(auth_class.runtime_error, AuthDataNotSet)
    assert str(auth_class.runtime_error) == str(AuthDataNotSet())


def test_authorization_thread_authorization_service_unavailable(mocker):
    """
    Test AuthorizationThread for AuthorizationServiceUnavailable during
    authorization service unavailability.
    """
    # Mock the requests.post method
    mocker.patch(
        "requests.post",
        side_effect=requests.exceptions.ConnectTimeout,
    )

    auth_class = launcher_authorization.AuthorizationThread(MagicMock())
    auth_class.set_auth_data("test_user", "test_password")
    auth_class.start()
    auth_class.wait(1000)

    assert isinstance(
        auth_class.runtime_error, AuthorizationServiceUnavailable
    )
    assert str(auth_class.runtime_error) == str(
        AuthorizationServiceUnavailable()
    )


def test_get_authenticate_response_success():
    """Test _get_authenticate_response for a successful authentication."""
    config = MagicMock()
    config.minecraft_launcher_ip_addr = "https://test_api_url"
    with requests_mock.Mocker() as m:
        # Mock the requests.post method for success (status code 200)
        m.post(
            config.minecraft_launcher_ip_addr,
            json={"status": "success", "data": {"key": "value"}},
            status_code=200,
        )
        auth_class = launcher_authorization.AuthorizationThread(
            config.minecraft_launcher_ip_addr
        )
        auth_class.set_auth_data("test_user", "test_password")

        # pylint: disable=W0212
        result = auth_class._get_authenticate_response(
            "test_user", "test_password"
        )

        assert result.json() == {"status": "success", "data": {"key": "value"}}


def test_get_authenticate_response_unauthorized():
    """
    Test _get_authenticate_response for an unauthorized authentication
    (status code 401).
    """
    config = MagicMock()
    config.minecraft_launcher_ip_addr = "https://test_api_url"

    with requests_mock.Mocker() as m:
        # Mock the requests.post method for unauthorized (status code 401)
        m.post(config.minecraft_launcher_ip_addr, status_code=401)

        auth_class = launcher_authorization.AuthorizationThread(
            config.minecraft_launcher_ip_addr
        )
        auth_class.set_auth_data("test_user", "test_password")

        # Call the internal method and assert it raises the expected exception
        with pytest.raises(UserAuthenticationError):
            # pylint: disable=W0212
            auth_class._get_authenticate_response("test_user", "test_password")


def test_get_authenticate_response_internal_error():
    """
    Test _get_authenticate_response for an internal server error
    (status code 500).
    """
    config = MagicMock()
    config.minecraft_launcher_ip_addr = "https://test_api_url"

    with requests_mock.Mocker() as m:
        # Mock the requests.post method for internal server
        # error (status code 500)
        m.post(config.minecraft_launcher_ip_addr, status_code=500)

        auth_class = launcher_authorization.AuthorizationThread(
            config.minecraft_launcher_ip_addr
        )
        auth_class.set_auth_data("test_user", "test_password")

        # Call the internal method and assert it raises the expected exception
        with pytest.raises(launcher_authorization.InternalAuthenticationError):
            # pylint: disable=W0212
            auth_class._get_authenticate_response("test_user", "test_password")


def test_get_authenticate_response_unexpected_error():
    """Test _get_authenticate_response for an unexpected error
    (other status code)."""
    config = MagicMock()
    config.minecraft_launcher_ip_addr = "https://test_api_url"

    with requests_mock.Mocker() as m:
        # Mock the requests.post method for an unexpected status code
        m.post(config.minecraft_launcher_ip_addr, status_code=403)

        auth_class = launcher_authorization.AuthorizationThread(
            config.minecraft_launcher_ip_addr
        )
        auth_class.set_auth_data("test_user", "test_password")

        # Call the internal method and assert it raises the expected exception
        with pytest.raises(InternalAuthenticationError) as exc_info:
            # pylint: disable=W0212
            auth_class._get_authenticate_response("test_user", "test_password")

        assert exc_info.value.error_code == 403


def test_is_response_valid_success(mocker):
    """Test _get_authenticate_response for a successful authentication."""

    username = "test_username"
    uuid = "c575bbb5-050d-abb0-736b-431ddfbb720b"
    token = secrets.token_hex(32)
    response_json = {
        "status": "OK",
        "username": username,
        "uuid": uuid,
        "accessToken": token,
    }
    mock_response = mocker.Mock(spec=requests.Response)
    mocker.patch.object(mock_response, "json", return_value=response_json)
    # pylint: disable=W0212
    result = launcher_authorization.AuthorizationThread.is_response_valid(
        mock_response
    )

    assert result is True


def test_is_response_valid_with_invalid_response_json_data(mocker):
    """Test _get_authenticate_response"""

    username = "test_username"
    uuid = "c575bbb5-050d-abb0-736b-431ddfbb720b"
    token = secrets.token_hex(32)
    response_json = {
        "status": "OK",
        "invalid_username": username,
        "uuid": uuid,
        "accessToken": token,
    }
    mock_response = mocker.Mock(spec=requests.Response)
    mocker.patch.object(mock_response, "json", return_value=response_json)
    # pylint: disable=W0212
    result = launcher_authorization.AuthorizationThread.is_response_valid(
        mock_response
    )
    assert result is False


def test_is_response_valid_with_invalid_response_type_str(mocker):
    """Test _get_authenticate_response"""
    response_json = "This is invalid response type."
    mock_response = mocker.Mock(spec=requests.Response)
    mocker.patch.object(mock_response, "json", return_value=response_json)
    # pylint: disable=W0212
    result = launcher_authorization.AuthorizationThread.is_response_valid(
        mock_response
    )
    assert result is False


def test_is_response_valid_with_json_parsing_error(mocker):
    """Test _get_authenticate_response"""
    mock_response = mocker.Mock(spec=requests.Response)
    mocker.patch.object(mock_response, "json", side_effect=Exception)
    # pylint: disable=W0212
    result = launcher_authorization.AuthorizationThread.is_response_valid(
        mock_response
    )
    assert result is False


def test_update_last_auth_data(mocker):
    """Test _update_last_auth_data for a successful update."""
    config = MagicMock()
    config.minecraft_launcher_ip_addr = "https://test_api_url"
    auth_class = launcher_authorization.AuthorizationThread(
        config.minecraft_launcher_ip_addr
    )
    response_json = {"status": "OK"}
    mock_response = mocker.Mock(spec=requests.Response)
    mocker.patch.object(mock_response, "json", return_value=response_json)

    # pylint: disable=W0212
    assert auth_class._last_auth_data is None

    auth_class._update_last_auth_data(mock_response)
    assert auth_class._last_auth_data == mock_response.json()


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
            launcher_authorization.UserAuthenticationError,
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
            launcher_authorization.AuthorizationServiceUnavailable,
        )
