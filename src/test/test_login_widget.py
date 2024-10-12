"""Tests for src.launcher.login_widget.py."""

import requests_mock
from src.launcher.launcher_configs import LauncherConfig
from src.launcher.login_widget import AuthenticationWorker, LoginWidget
from src.launcher.main_window import Window
from src.launcher.utility.pydantic_models import AuthData

VALID_AUTH_JSON_DATA = {
    "status": "status",
    "username": "username",
    "uuid": "uuid",
    "accessToken": "accessToken",
}


def get_app():
    """Return testing app/"""
    return Window()


# pylint: disable=W0201, W0212, W0613
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

    def setup_method(self):
        """Init testing app."""
        self.widget = LoginWidget(
            get_app()._ui_instance, LauncherConfig.MINECRAFT_LAUNCHER_IP_ADDR
        )

    def test_login_page_is_visible(self, qtbot):
        """Check if first page after app startup is login page."""
        assert self.widget._ui.stackedWidget.currentIndex() == 0

    def test_page_switching_after_success_authentication(self, qtbot):
        """Test if page switches to success after authentication."""
        auth_data = "some_data"
        self.widget.worker._auth_data = auth_data
        self.widget.worker.success.emit()

        assert self.widget.auth_data == auth_data
        assert self.widget._ui.pushButton_error_info.isHidden()
        assert self.widget.info_widget.isHidden()

        assert self.widget._ui.stackedWidget.currentIndex() == 1

    def test_ui_elements_initialization(self, qtbot):
        """Test if all necessary UI elements are hidden initially."""
        assert self.widget.info_widget.isHidden()
        assert self.widget._ui.pushButton_error_info.isHidden()

    def test_login_button_disabled_on_invalid_input(self, qtbot):
        """Test that the login button is disabled with invalid input."""
        self.widget._ui.lineEdit_nickname.setText("abc")
        self.widget._ui.lineEdit_password.setText("123")
        self.widget._validate_user_input()  # Call method directly
        assert not self.widget._ui.pushButton_login.isEnabled()

        self.widget._ui.lineEdit_nickname.setText("abcd")
        self.widget._ui.lineEdit_password.setText("1234")
        self.widget._validate_user_input()
        assert self.widget._ui.pushButton_login.isEnabled()

    def test_blur_effect_on_login(self, qtbot):
        """Test that blur effect is applied during login process."""
        self.widget.block_ui()  # Start the authentication process
        assert self.widget._widget.graphicsEffect()

        self.widget.enable_ui()  # Complete the authentication
        assert not self.widget._widget.graphicsEffect()
