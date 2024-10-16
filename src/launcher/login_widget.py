"""Implementation of launcher login logic."""

import time
from typing import Optional

from loguru import logger as log
from PySide6.QtCore import QObject, QThread, QTimer, Signal, Slot
from qtpy.QtWidgets import QPushButton

from .design.design import Ui_MainWindow
from .design.thread_data_utils import SettingsManager
from .design.utility import BaseWidget, MessageBox
from .launcher_authorization import authenticate_user
from .launcher_configs import LauncherConfig
from .utility.custom_exceptions import (
    AuthDataNotSet,
    AuthenticationError,
    InvalidUserNameOrPassword,
)
from .utility.pydantic_models import AuthData


class LogoutMessageBox(MessageBox):
    """A logout message box."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logout_button = QPushButton(self)
        self.logout_button.setText("выйти")
        self.logout_button.clicked.connect(self.accept)
        self.button_layout.addWidget(self.logout_button)
        self.button_layout.addStretch()
        self._msg = self._format_title("Вы точно хотите выйти?")
        self._text_edit.setFixedHeight(75)


class AuthenticationWorker(QThread):
    """
    A worker thread to handle the user authentication process.

    Signals:
        finished: Emitted when the authentication process is complete,
            regardless of success or failure.
        error_message (str): Emitted when an error occurs during
            the authentication process, with a descriptive error message.
        success: Emitted when authentication completes successfully.
        write_message (str): Emitted to communicate status messages to the GUI
            during the process.

    """

    finished = Signal()
    error_message = Signal(str)
    success = Signal()
    write_message = Signal(str)

    def __init__(self, login_api_url: str):
        """
        Initializes the AuthenticationWorker with the specified
            API URL for authentication.

        Args:
            login_api_url (str): The URL of the API endpoint
                for user authentication.
        """
        super().__init__()
        self.login_api_url = login_api_url
        self._login: Optional[str] = None
        self._password: Optional[str] = None

        self._auth_data: Optional[AuthData] = None

    def run(self):
        """Run the authentication process."""
        self.write_message.emit("Авторизация...")

        try:
            log.info("AuthenticationWorker started.")
            if self._login is None or self._password is None:
                log.critical("Calling of set_auth_data is required.")
                self.error_message.emit(str(AuthDataNotSet))
                return  # Stop further execution

            # Proceed with authentication if data is set
            self._auth_data = authenticate_user(
                self.login_api_url,
                self._login,
                self._password,
            )

            log.info("Authentication completed.")
            self.write_message.emit("Авторизация завершена...")
            self.success.emit()
        except InvalidUserNameOrPassword as error:
            time.sleep(3)
            log.error(repr(error))
            self.error_message.emit(str(error))
        except AuthenticationError as error:
            log.error(repr(error))
            self.error_message.emit(str(error))
        finally:
            self._login = None
            self._password = None
            self.finished.emit()

    def set_auth_data(self, login: str, password: str) -> None:
        """Set user credentials data."""
        self._login = login
        self._password = password

    @property
    def auth_data(self) -> Optional[AuthData]:
        """Return user authentication data."""
        return self._auth_data


class LoginWidget(QObject, BaseWidget):
    """
    A widget for user login interface.

    This widget handles user input for login and communicates with the
    authentication worker to manage the login process. It provides feedback
    to the user through UI elements and manages the visibility of
    different UI components based on the authentication state.
    """

    authentication_complete = Signal()

    def __init__(
        self,
        main_window: Ui_MainWindow,
        launcher_config: LauncherConfig,
        settings: SettingsManager,
    ):
        """
        Initialize the LoginWidget.

        Args:
            main_window (Ui_MainWindow): The main window UI instance to
                which this widget is attached.
            launcher_config (LauncherConfig): An instance of LauncherConfig
                class.
            settings (SettingsManager): An instance of SettingsManager.
        """

        super().__init__(
            widget=main_window.stackedWidget,
            parent_widget=main_window.widget_main_window,
        )

        self._ui = main_window
        self._logout_accept = LogoutMessageBox(self._ui.widget_main_window)
        self._launcher_config = launcher_config
        self._error_timer: Optional[QTimer] = None
        self._auth_data: Optional[AuthData] = None
        self._settings = settings

        # Initialize UI components and settings.
        self._init_ui()

        # Initialize the authentication worker.
        self._worker = AuthenticationWorker(
            self._launcher_config.MINECRAFT_LAUNCHER_IP_ADDR
        )

        # Connect signals to their respective slots.
        self._connect_signals()

        if self._settings.get_user_value("is_authenticated"):
            self._ui.pushButton_login.clicked.emit()

    @Slot()
    def disable_ui(self, show_text: bool = True, show_progress: bool = True):
        """Disable the login UI during the authentication process."""
        super().disable_ui(show_text, show_progress)
        self._ui.pushButton_error_info.hide()

    @property
    def auth_data(self) -> Optional[AuthData]:
        """Return the authentication data.

        This property provides access to the authentication
            data retrieved from the worker.

        Returns:
            Optional[AuthData]: The current authentication data or None.
        """
        return self._auth_data

    @Slot()
    def write_error(self, message: str):
        """Display an error message in the UI."""
        self._ui.pushButton_error_info.setText(message)
        self._ui.pushButton_error_info.show()

    def _connect_signals(self):
        """Connect UI elements to their respective slots."""
        self._ui.pushButton_login.clicked.connect(
            lambda _: self.disable_ui(True, False)
        )
        self._ui.pushButton_login.clicked.connect(self._make_authorization)

        self._worker.write_message.connect(self.info_label.setText)
        self._worker.error_message.connect(self.write_error)
        self._worker.error_message.connect(self.enable_ui)

        self._worker.success.connect(self._complete_authentication)

        self._ui.lineEdit_nickname.textChanged.connect(
            self._validate_user_input
        )
        self._ui.lineEdit_password.textChanged.connect(
            self._validate_user_input
        )

        self._ui.pushButton_error_info.clicked.connect(
            self._ui.pushButton_error_info.hide
        )
        self._ui.pushButton_logout.clicked.connect(super().disable_ui)
        self._ui.pushButton_logout.clicked.connect(
            lambda: self._logout_accept.show_message(
                title="Вы точно хотите выйти из аккаунта?",
                close_button_text="не хочу",
            )
        )

        self._logout_accept.logout_button.clicked.connect(self._logout_user)
        self._logout_accept.accepted.connect(self.enable_ui)

    def _init_ui(self):
        """Initialize the user interface components."""
        self._ui.pushButton_error_info.hide()

        self._validate_user_input()

    @Slot()
    def _logout_user(self):
        self._settings.set_user_value(
            self._launcher_config.IS_AUTHENTICATED_KEY,
            0,
        )
        self._settings.set_ui_value("lineEdit_nickname", "")
        self._settings.set_ui_value("lineEdit_password", "")
        self._erase_auth_data()
        self._ui.stackedWidget.setCurrentWidget(self._ui.login_page)

    @Slot()
    def _validate_user_input(self):
        """Validate user input for login fields."""
        self._ui.pushButton_login.setEnabled(
            bool(
                len(self._ui.lineEdit_nickname.text()) > 3
                and len(self._ui.lineEdit_password.text()) > 3
            )
        )

    @Slot()
    def _make_authorization(self) -> None:
        """Initiate the authentication process."""
        login = self._ui.lineEdit_nickname.text()
        password = self._ui.lineEdit_password.text()

        self._worker.set_auth_data(login, password)

        self._worker.start()
        # self._authorization_thread.set_auth_data(login, password)
        # self._authorization_thread.start()

    @Slot()
    def _complete_authentication(self):
        """Handle successful authentication."""
        self._settings.set_user_value(
            self._launcher_config.IS_AUTHENTICATED_KEY,
            1,
        )
        self._auth_data = self._worker.auth_data
        self.authentication_complete.emit()

    def _erase_auth_data(self) -> None:
        """Erase authentication data before logout."""
        self._auth_data = None
