"""Tests for src/launcher/launcher_authorization.py"""

# pylint:disable = E0401, W0212
import os
from unittest.mock import MagicMock

import pytest
import requests
import requests_mock
from src.launcher import launcher_authorization, launcher_configs
from src.launcher.launcher_authorization import authenticate_user
from src.launcher.utility.custom_exceptions import (
    AuthenticationServiceUnavailable,
    Base64ParsingError,
    InternalAuthenticationError,
    InvalidAuthenticationResponse,
    InvalidUserNameOrPassword,
)
from src.launcher.utility.pydantic_models import AuthData


class TestAuthenticateUser:
    """Tests for authenticate_user function."""

    def test_authenticate_user_service_unavailable(self, mocker):
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

    def test_authenticate_user_success(self):
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
        assert isinstance(auth_data, AuthData)
        assert auth_data == AuthData(**json_ans)

    def test_authenticate_user_unauthorized(self):
        """
        Test authenticate_user for an unauthorized authentication
        (status code 401).
        """
        config = MagicMock()
        config.minecraft_launcher_ip_addr = "https://test_api_url"

        with requests_mock.Mocker() as m:
            # Mock the requests.post method for unauthorized (status code 401)
            m.post(config.minecraft_launcher_ip_addr, status_code=401)

            with pytest.raises(InvalidUserNameOrPassword):
                # pylint: disable=W0212
                authenticate_user(
                    config.minecraft_launcher_ip_addr,
                    "test_user",
                    "test_password",
                )

    def test_authenticate_user_internal_error(self):
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

            with pytest.raises(
                launcher_authorization.InternalAuthenticationError
            ):
                authenticate_user(
                    config.minecraft_launcher_ip_addr,
                    "login",
                    "pass",
                )

    def test_authenticate_user_unexpected_error(self):
        """Test authenticate_user for an unexpected error
        (other status code)."""
        config = MagicMock()
        config.minecraft_launcher_ip_addr = "https://test_api_url"

        with requests_mock.Mocker() as m:
            # Mock the requests.post method for an unexpected status code
            m.post(config.minecraft_launcher_ip_addr, status_code=403)

            with pytest.raises(InternalAuthenticationError) as exc_info:
                authenticate_user(
                    config.minecraft_launcher_ip_addr,
                    "login",
                    "pass",
                )

            assert "403" in repr(exc_info)

    def test_authenticate_user_invalid_json_data_type(self, mocker):
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

    def test_authenticate_user_with_invalid_response_json_data(self, mocker):
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


class TestSkinUploader:
    """Tests for SkinUploader class."""

    def test_successful_skin_upload(self):
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
            skin_uploader = launcher_authorization.SkinUploader(
                "test_user", "test_password", api_url, "mock_url"
            )

            skin_uploader._push_img(
                api_url=api_url,
                selected_skin_path=f"{script_directory}/test_skin.png",
            )

    def test_make_json_response(self):
        """Tests if json creates correctly."""
        api_url = launcher_configs.LauncherConfig.MINECRAFT_LAUNCHER_IP_ADDR

        # Create an instance of SkinUploaderThread
        skin_uploader = launcher_authorization.SkinUploader(
            "test_user", "test_password", api_url, "mock_url"
        )

        # Call the _make_json_response method
        # pylint: disable = W0212
        json_response = skin_uploader._make_json_response(
            base64_img="test_base64_img",
            is_skin_slim=True,
        )

        # Validate the structure and content of the JSON response
        expected_json = {
            "username": "test_user",
            "password": "test_password",
            "base64_image": "test_base64_img",
            "is_skin_slim": True,
        }

        assert json_response == expected_json

    def test__push_img_with_invalid_skin_path(self):
        """Test skin upload with an invalid skin path."""
        api_url = launcher_configs.LauncherConfig.MINECRAFT_LAUNCHER_IP_ADDR
        # Create an instance of SkinUploaderThread
        skin_uploader = launcher_authorization.SkinUploader(
            "test_user", "test_password", api_url, "mock_url"
        )
        with pytest.raises(Base64ParsingError):
            skin_uploader._push_img(
                api_url=api_url,
                selected_skin_path="non_exists.png",
            )

    def test__push_img_with_invalid_auth_data(self):
        """Test skin upload with an invalid auth data."""
        api_url = launcher_configs.LauncherConfig.MINECRAFT_LAUNCHER_IP_ADDR
        script_directory = os.path.dirname(os.path.abspath(__file__))

        skin_uploader = launcher_authorization.SkinUploader(
            "test_user", "test_password", api_url, "mock_url"
        )
        with requests_mock.Mocker() as m:
            m.post(
                api_url,
                status_code=401,
            )
            with pytest.raises(InvalidUserNameOrPassword):
                skin_uploader._push_img(
                    api_url=api_url,
                    selected_skin_path=f"{script_directory}/test_skin.png",
                )

    def test__push_img_with_invalid_api_response_code(self):
        """Test skin upload with an invalid API response status code."""
        api_url = launcher_configs.LauncherConfig.MINECRAFT_LAUNCHER_IP_ADDR
        script_directory = os.path.dirname(os.path.abspath(__file__))

        skin_uploader = launcher_authorization.SkinUploader(
            "test_user", "test_password", api_url, "mock_url"
        )
        with requests_mock.Mocker() as m:
            # Mock the requests.post method for success (status code 501)
            m.post(
                api_url,
                status_code=501,
            )
            with pytest.raises(InternalAuthenticationError):
                skin_uploader._push_img(
                    api_url=api_url,
                    selected_skin_path=f"{script_directory}/test_skin.png",
                )

    def test__push_img_with_unavailable_authorization_service(self):
        """
        Test the behavior of skin upload when the authorization service
        is unavailable.
        """
        api_url = launcher_configs.LauncherConfig.MINECRAFT_LAUNCHER_IP_ADDR
        script_directory = os.path.dirname(os.path.abspath(__file__))

        skin_uploader = launcher_authorization.SkinUploader(
            "test_user", "test_password", api_url, "mock_url"
        )
        with requests_mock.Mocker() as m:
            # Mock the requests.post method for success (status code 200)
            m.post(api_url, exc=requests.exceptions.ConnectTimeout)
            with pytest.raises(AuthenticationServiceUnavailable):
                skin_uploader._push_img(
                    api_url=api_url,
                    selected_skin_path=f"{script_directory}/test_skin.png",
                )

    def test_push_skin(self, mocker):
        """Check if push_skin calls _push_img with correct arguments."""
        skin_uploader = launcher_authorization.SkinUploader(
            "test_user",
            "test_password",
            "api_skin_mock_url",
            "api_cape_mock_url",
        )
        mock_path = "path"
        mock_is_slim = True
        mock__push_img = MagicMock()
        with mocker.patch.object(skin_uploader, "_push_img", mock__push_img):
            skin_uploader.push_skin(mock_path, mock_is_slim)

        mock__push_img.assert_called_once_with(
            api_url=skin_uploader._push_skin_api_url,
            selected_skin_path=mock_path,
            is_skin_slim=mock_is_slim,
        )

    def test_push_cape(self, mocker):
        """Check if push_cape calls _push_img with correct arguments."""
        skin_uploader = launcher_authorization.SkinUploader(
            "test_user",
            "test_password",
            "api_skin_mock_url",
            "api_cape_mock_url",
        )
        mock_path = "path"
        mock_is_slim = True
        mock__push_img = MagicMock()
        with mocker.patch.object(skin_uploader, "_push_img", mock__push_img):
            skin_uploader.push_cape(mock_path, mock_is_slim)

        mock__push_img.assert_called_once_with(
            api_url=skin_uploader._push_cape_api_url,
            selected_skin_path=mock_path,
            is_skin_slim=mock_is_slim,
        )
