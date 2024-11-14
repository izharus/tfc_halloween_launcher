"""Tests for src.launcher.login_widget.py."""

# pylint: disable=W0201, W0212, W0613, E0401

from unittest.mock import MagicMock

import pytest
import requests
import requests_mock
from pytest_mock import MockerFixture
from src.launcher.launcher_configs import LauncherConfig
from src.launcher.login_widget import AuthenticationWorker, ResetPasswordWorker
from src.launcher.main_window import Window
from src.launcher.utility.pydantic_models import AuthData

VALID_AUTH_JSON_DATA = {
    "status": "status",
    "username": "username",
    "uuid": "uuid",
    "accessToken": "accessToken",
}


class TestAuthenticationWorker:
    """Tests for AuthenticationWorker class."""

    def setup_method(self):
        """Init worker class."""
        self.worker = AuthenticationWorker(
            LauncherConfig.MINECRAFT_LAUNCHER_IP_ADDR
        )

    def test_authentication_success(self, qtbot):
        """Tests success authentication."""
        with requests_mock.Mocker() as m:
            m.post(
                LauncherConfig.MINECRAFT_LAUNCHER_IP_ADDR,
                json=VALID_AUTH_JSON_DATA,
                status_code=200,
            )
            self.worker.set_auth_data("username", "pass")
            with qtbot.wait_signal(self.worker.finished):
                with qtbot.wait_signal(self.worker.success):
                    with qtbot.assertNotEmitted(self.worker.error_message):
                        self.worker.run()

        assert self.worker.auth_data == AuthData(**VALID_AUTH_JSON_DATA)

    def test_authentication_when_auth_data_not_set(self, qtbot):
        """Tests authentication without calling set_auth_data."""
        with qtbot.wait_signal(self.worker.error_message):
            with qtbot.wait_signal(self.worker.finished):
                with qtbot.assertNotEmitted(self.worker.success):
                    self.worker.run()

        assert self.worker.auth_data is None

    def test_authentication_invalid_credentials(self, qtbot):
        """Tests authentication with invalid credentials."""
        with requests_mock.Mocker() as m:
            m.post(
                LauncherConfig.MINECRAFT_LAUNCHER_IP_ADDR,
                json={"error": "Invalid username or password"},
                status_code=401,  # Unauthorized
            )
            self.worker.set_auth_data("invalid_username", "invalid_password")

            with qtbot.wait_signal(self.worker.error_message):
                with qtbot.wait_signal(self.worker.finished):
                    with qtbot.assertNotEmitted(self.worker.success):
                        self.worker.run()

        assert self.worker.auth_data is None

    def test_authentication_api_failure(self, qtbot):
        """Tests handling of API failure during authentication."""
        with requests_mock.Mocker() as m:
            m.post(
                LauncherConfig.MINECRAFT_LAUNCHER_IP_ADDR,
                status_code=500,  # Internal Server Error
            )
            self.worker.set_auth_data("username", "password")
            with qtbot.wait_signal(self.worker.error_message):
                with qtbot.wait_signal(self.worker.finished):
                    with qtbot.assertNotEmitted(self.worker.success):
                        self.worker.run()

        assert self.worker.auth_data is None

    def test_credentials_reset_after_run(self):
        """
        Tests that credentials are reset after the worker finishes execution.
        """
        with requests_mock.Mocker() as m:
            m.post(
                LauncherConfig.MINECRAFT_LAUNCHER_IP_ADDR,
                json=VALID_AUTH_JSON_DATA,
                status_code=200,
            )

            self.worker.set_auth_data("username", "password")
            self.worker.start()
            self.worker.wait()

        assert self.worker._login is None
        assert self.worker._password is None


class TestLoginWidget:
    """Tests for LoginWidget."""

    def test_login_page_is_visible(self, main_window: Window, qtbot):
        """Check if first page after app startup is login page."""
        widget = main_window._login_widget
        assert widget._ui.stackedWidget.currentIndex() == 0

    def test_ui_elements_initialization(self, main_window: Window, qtbot):
        """Test if all necessary UI elements are hidden initially."""
        widget = main_window._login_widget
        assert widget._info_widget.isHidden()
        assert widget._ui.pushButton_error_info.isHidden()

    def test_login_button_disabled_on_invalid_input(
        self, main_window: Window, qtbot
    ):
        """Test that the login button is disabled with invalid input."""
        widget = main_window._login_widget
        widget._ui.lineEdit_nickname.setText("abc")
        widget._ui.lineEdit_password.setText("123")
        widget._validate_user_input_login()  # Call method directly
        assert not widget._ui.pushButton_login.isEnabled()

        widget._ui.lineEdit_nickname.setText("abcd11")
        widget._ui.lineEdit_password.setText("1234111")
        widget._validate_user_input_login()
        assert widget._ui.pushButton_login.isEnabled()

    def test_blur_effect_on_login(self, main_window: Window, qtbot):
        """Test that blur effect is applied during login process."""
        widget = main_window._login_widget
        widget.disable_ui()  # Start the authentication process
        assert widget._widget.graphicsEffect()

        widget.enable_ui()  # Complete the authentication
        assert not widget._widget.graphicsEffect()

    def test_if_ui_enables_after_failed_authentication(
        self, main_window: Window, qtbot
    ):
        """Test if ui enables if authentication failed."""

        widget = main_window._login_widget
        widget._worker.set_auth_data("login", "pass")
        with requests_mock.Mocker() as m:
            m.post(
                LauncherConfig.MINECRAFT_LAUNCHER_IP_ADDR,
                status_code=500,  # Internal Server Error
            )
            widget._worker.run()
        assert widget._widget.isEnabled()

    def test_successful_authentication(
        self,
        main_window: Window,
        qtbot,
        mock_auth_data,
        mocker,
    ):
        """Test successful authentication."""

        widget = main_window._login_widget
        widget._worker.set_auth_data("login", "pass")
        mock_set_user_data = MagicMock()
        mocker.patch.object(
            widget._settings, "set_user_value", mock_set_user_data
        )
        # Simulate blocking ui after clicking on login button
        widget.disable_ui()
        with requests_mock.Mocker() as m:
            m.post(
                LauncherConfig.MINECRAFT_LAUNCHER_IP_ADDR,
                status_code=200,  # Internal Server Error
                json=mock_auth_data,
            )
            widget._worker.run()
        assert not widget._widget.isEnabled()
        mock_set_user_data.assert_called_once_with(
            widget._launcher_config.IS_AUTHENTICATED_KEY,
            1,
        )

    def test_auto_reconnect(
        self,
        qtbot,
        mocker,
    ):
        """Test reconnect logic."""

        settings = MagicMock()
        mock_get_user_data = MagicMock(return_value=1)
        mocker.patch.object(settings, "value", mock_get_user_data)
        mocker.patch.object(settings, "ser_value", MagicMock())

        window = Window(settings=settings)
        qtbot.wait_signal(window._ui_instance.pushButton_login.clicked)


class TestResetPasswordWorker:
    """Tests for ResetPasswordWorker class."""

    def setup_method(self):
        """Setup every test method."""
        self.mock_url = "https://restore"
        self.username = "test_username"
        self.email = "test@email.com"
        self.worker = ResetPasswordWorker(
            self.username,
            self.email,
            self.mock_url,
        )
        self.expected_json = {
            "username": self.username,
            "email": self.email,
        }
        self.worker.success = MagicMock()
        self.worker.success.emit = MagicMock()
        self.worker.write_error = MagicMock()
        self.worker.write_error.emit = MagicMock()

    def test_rest_password_success(
        self,
    ):
        """Test successful password reset request with expected JSON."""
        with requests_mock.Mocker() as m:
            m.post(
                self.mock_url,
                status_code=200,
            )
            self.worker.run()

            request = m.request_history[0]
            assert request.json() == self.expected_json
        self.worker.success.emit.assert_called_once_with()
        self.worker.write_error.emit.assert_not_called()

    @pytest.mark.parametrize("error_code", (409, 404, 500))
    def test_rest_password_error_code(
        self,
        error_code: int,
    ):
        """
        Test password reset request handling for HTTP different error codes.
        """
        with requests_mock.Mocker() as m:
            m.post(
                self.mock_url,
                status_code=error_code,
            )
            self.worker.run()

            request = m.request_history[0]
            assert request.json() == self.expected_json
        self.worker.success.emit.assert_not_called()
        self.worker.write_error.emit.assert_called_once_with(str(error_code))

    def test_rest_password_internal_error(
        self,
        mocker: MockerFixture,
    ):
        """Test password reset request handling for an internal error."""
        mocker.patch.object(requests, "post", side_effect=RuntimeError)

        self.worker.run()

        self.worker.success.emit.assert_not_called()
        self.worker.write_error.emit.assert_called_once_with("indefinite")
