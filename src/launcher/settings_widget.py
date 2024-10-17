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


class SettingsWidget(QObject, BaseWidget):

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
        # self._logout_accept = LogoutMessageBox(self._ui.widget_main_window)
        self._launcher_config = launcher_config
        self._error_timer: Optional[QTimer] = None
        self._auth_data: Optional[AuthData] = None
        self._settings = settings

        # Initialize UI components and settings.
        # self._init_ui()

        # Connect signals to their respective slots.
        self._connect_signals()

        if self._settings.get_user_value("is_authenticated"):
            self._ui.pushButton_login.clicked.emit()

    def _connect_signals(self):
        # Go to the settings
        self._ui.pushButton_settings.clicked.connect(
            lambda: self._ui.stackedWidget.setCurrentWidget(
                self._ui.launcher_settings_page
            )
        )
        # Close the settings
        self._ui.pushButton_back_arrow.clicked.connect(
            lambda: self._ui.stackedWidget.setCurrentWidget(
                self._ui.choose_server_page
            )
        )
