"""Implementation of launcher login logic."""

import os
import time
from pathlib import Path
from typing import Callable, Optional

import psutil
from loguru import logger as log
from qtpy.QtCore import QObject, QThread, Signal, Slot
from qtpy.QtWidgets import QFileDialog

from .design.design import Ui_MainWindow
from .design.thread_data_utils import SettingsManager
from .design.utility import BaseWidget, LabeledSlider, MessageBox
from .launcher_authorization import SkinUploader
from .launcher_configs import LauncherConfig
from .utility.custom_exceptions import (
    AuthenticationServiceUnavailable,
    Base64ParsingError,
    InternalAuthenticationError,
    InvalidAuthenticationResponse,
    InvalidUserNameOrPassword,
)

MSG_BOX_HEIGHT = 150


class UploadWorker(QThread):
    """
    A worker thread for handling upload operations in a PyQt application.

    Signals:
        error_message (str): Emitted when an error occurs during the upload
            process, providing details about the error.
        success (): Emitted when the upload operation completes successfully.
        write_message (str): Emitted to communicate messages related to
            the upload process, such as progress updates or status messages.
    """

    error_message = Signal(str)
    success = Signal()
    write_message = Signal(str)

    def __init__(self):
        self._function: Optional[Callable[..., None]] = None
        super().__init__()

    def run(self):
        """
        Run the upload process.

        This method executes the upload function set by `set_function`.
        Emits progress messages and handles exceptions related to the
        upload process. Signals errors if they occur.

        Raises:
            Exception: Any exception raised during the upload process
                will be caught and emitted as an error message.
        """
        try:
            log.debug("Upload operation started.")
            self.write_message.emit("Выполняю...")
            if not self._function:
                self.write_message.emit("Функция загрузки не задана")
                return
            self._function()
            self.write_message.emit("Операция выполнена!")
            time.sleep(1.5)
            self.success.emit()
            self.write_message.emit("")
            log.debug("Upload operation success.")
        except (
            AuthenticationServiceUnavailable,
            Base64ParsingError,
            InternalAuthenticationError,
            InvalidAuthenticationResponse,
            InvalidUserNameOrPassword,
        ) as error:
            log.debug(f"Upload operation failed: {error}")
            self.write_message.emit("")
            self.error_message.emit(str(error))

    def set_function(self, function: Callable) -> None:
        """Set the upload function to be executed in the thread."""
        self._function = function


class SettingsWidget(QObject, BaseWidget):
    """
    A widget that manages user settings for the launcher interface.
    """

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
            parent_widget=main_window.widget_main_window_child,
        )

        self._ui = main_window

        self._msg_box = MessageBox(self._ui.widget_main_window)
        self._msg_box.setFixedHeight(MSG_BOX_HEIGHT)
        self._launcher_config = launcher_config
        self._settings = settings
        username = self._settings.get_ui_value("lineEdit_nickname")
        password = self._settings.get_ui_value("lineEdit_password")
        self._skin_loader = SkinUploader(
            username=username,
            password=password,
            push_skin_api_url=self._launcher_config.API_URL_PUSH_SKIN,
            push_cape_api_url=self._launcher_config.API_URL_PUSH_CAPE,
        )
        self._upload_worker = UploadWorker()

        # Configure RAM slider
        max_ram = psutil.virtual_memory().total // (1024 * 1024)  # RAM in MB
        self._memory_slider = LabeledSlider(
            minimum=0, maximum=max_ram, max_typos=20
        )
        self._ui.verticalLayout_main_settings.insertWidget(
            0, self._memory_slider
        )
        self._settings.update_ui_inputs()

        self._memory_slider.show()

        self._connect_signals()

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

        # Choose and upload skin
        self._ui.pushButton_choose_skin.clicked.connect(
            lambda: self._choose_and_upload(
                directory=self._launcher_config.MINECRAFT_SKIN_DIR,
                is_skin=True,
            )
        )

        # Delete user skin
        self._ui.pushButton_delete_skin.clicked.connect(
            lambda: self._delete_user_texture(self._skin_loader.push_skin)
        )

        # Choose and upload cape
        self._ui.pushButton_choose_cape.clicked.connect(
            lambda: self._choose_and_upload(
                self._launcher_config.MINECRAFT_CAPE_DIR,
                is_skin=False,
            )
        )

        # Delete user cape
        self._ui.pushButton_delete_cape.clicked.connect(
            lambda: self._delete_user_texture(self._skin_loader.push_cape)
        )

        # Info messages due uploading skins
        self._upload_worker.write_message.connect(self.info_label.setText)

        # Enable ui after success operation
        self._upload_worker.success.connect(self.enable_ui)

        # Error messages for uploading errors
        self._upload_worker.error_message.connect(self._msg_box.show_message)

        # Enable ui after failed operation only after user input
        self._msg_box.accepted.connect(self.enable_ui)

    @Slot(str)
    def _choose_and_upload(self, directory: Path, is_skin: bool) -> None:
        self.disable_ui()
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_path, _ = QFileDialog.getOpenFileName(
            self._ui.stackedWidget, "Open File", str(directory)
        )
        if not file_path:
            self.enable_ui()
            return
        upload_function = (
            self._skin_loader.push_skin
            if is_skin
            else self._skin_loader.push_cape
        )
        self._upload_worker.set_function(
            lambda: upload_function(selected_skin_path=file_path)
        )
        self._upload_worker.start()

    @Slot()
    def _delete_user_texture(
        self,
        function: Callable,
    ) -> None:
        self.disable_ui()
        self._upload_worker.set_function(function)
        self._upload_worker.start()
