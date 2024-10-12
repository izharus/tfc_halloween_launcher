"""Implementation of launcher login logic."""

import time
from typing import Optional

from loguru import logger as log
from PySide6.QtCore import QThread, QTimer, Signal, Slot
from .design.design import Ui_MainWindow
from .launcher_authorization import authenticate_user
from .utility.custom_exceptions import (
    AuthDataNotSet,
    AuthenticationError,
    InvalidUserNameOrPassword,
)
from .utility.pydantic_models import AuthData
from .design.utility import BaseWidget

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
            self.write_message.emit("Обновление списка серверов...")
            time.sleep(3)
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


class LoginWidget(BaseWidget):
    """
    A widget for user login interface.

    This widget handles user input for login and communicates with the
    authentication worker to manage the login process. It provides feedback
    to the user through UI elements and manages the visibility of
    different UI components based on the authentication state.
    """

    def __init__(self, main_window: Ui_MainWindow, login_api_url: str):
        """
        Initialize the LoginWidget.

        Args:
            main_window (Ui_MainWindow): The main window UI instance to
                which this widget is attached.
            login_api_url (str): The API URL for user authentication.
        """

        super().__init__(main_window.login_page, main_window.stackedWidget)
        self._ui = main_window

        self._error_timer: Optional[QTimer] = None
        self._auth_data: Optional[AuthData] = None

        # Initialize UI components and settings.
        self._init_ui()

        # Initialize the authentication worker.
        self.worker = AuthenticationWorker(login_api_url)

        # Connect signals to their respective slots.
        self._connect_signals()

    def _connect_signals(self):
        """Connect UI elements to their respective slots."""
        self._ui.pushButton_login.clicked.connect(self.block_ui)
        self._ui.pushButton_login.clicked.connect(self._make_authorization)

        self.worker.write_message.connect(self.info_label.setText)
        self.worker.error_message.connect(self._write_error)

        self.worker.success.connect(self._complete_authentication)
        self.worker.finished.connect(self.enable_ui)

        self._ui.lineEdit_nickname.textChanged.connect(
            self._validate_user_input
        )
        self._ui.lineEdit_password.textChanged.connect(
            self._validate_user_input
        )

        self._ui.pushButton_error_info.clicked.connect(
            self._ui.pushButton_error_info.hide
        )

    def _init_ui(self):
        """Initialize the user interface components."""
        self._ui.pushButton_error_info.hide()

        self._validate_user_input()

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
    def _write_error(self, message: str):
        """Display an error message in the UI."""
        self._ui.pushButton_error_info.setText(message)
        self._ui.pushButton_error_info.show()


    @Slot()
    def _make_authorization(self) -> None:
        """Initiate the authentication process."""
        login = self._ui.lineEdit_nickname.text()
        password = self._ui.lineEdit_password.text()

        self.worker.set_auth_data(login, password)

        self.worker.start()
        # self._authorization_thread.set_auth_data(login, password)
        # self._authorization_thread.start()

    @Slot()
    def _complete_authentication(self):
        """Handle successful authentication."""
        self._auth_data = self.worker.auth_data
        self._ui.stackedWidget.setCurrentIndex(1)

    @Slot()
    def block_ui(self):
        """Disable the login UI during the authentication process."""
        super().block_ui()
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
