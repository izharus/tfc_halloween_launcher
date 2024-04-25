"""
Main entry point of the TFC-Halloween application.

This module provides the main entry point for the TFC-Halloween application,
which allows users to install Minecraft with a ProgressBar in PyQt. It defines
the main window, installation threads, and various utility functions.

It uses PyQt for the GUI, installation threads to handle Minecraft and shader
installation, and provides progress updates with a ProgressBar. Users can
install shaders and Minecraft, launch the game, and receive status
notifications about the installation process.

The application also handles the visibility of the console window, sets the
icon, and provides safety timers for updating input data from the UI.

"""
# pylint: disable=unnecessary-lambda
import os
import sys
import traceback
import webbrowser
from typing import Dict, Union

import boto3
import boto3.exceptions
import win32con
import win32console
import win32gui
from log_wizard import log as get_logger
from PyQt6 import QtWidgets
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QFileDialog

from .data_validation import Validator
from .design.design import Ui_MainWindow
from .design.utillity import (
    MainButton,
    MessageBoxManager,
    NotificationWidget,
    open_directory,
)
from .launcher_authorization import (
    AuthorizationThread,
    CapeUploaderThread,
    SkinUploaderThread,
)
from .launcher_configs import (
    ConfigLoader,
    LauncherConfig,
    MinecraftLauncherConfig,
)
from .launcher_installer import InstallThread, MinecraftExecutorThread
from .utillity.custom_exceptions import (
    ConfigProcessingError,
    RequestDownloadError,
)
from .utillity.path_manager import PathManager
from .utillity.thread_data_utils import ThreadUiInputData
from .utillity.yos import get_boto3_instance

OFFLINE_MAP_JSON: Dict = {
    "ОБНОВИТЬ": {},
}
log = get_logger()


def hide_console() -> None:
    """
    Hides console windows.

    Returns:
        None
    """
    window = win32console.GetConsoleWindow()
    win32gui.ShowWindow(window, win32con.SW_HIDE)


# pylint: disable = R0903
class Window(QtWidgets.QMainWindow):
    """Main window of app"""

    # pylint: disable = R0902
    def __init__(self) -> None:
        log.debug("Window class __init__ entered.")
        super().__init__()
        self._ui_instance = Ui_MainWindow()
        self._launcher_config = LauncherConfig()
        self._ui_instance.setupUi(self)
        self.resize(500, 125)  # Adjust 800 to your desired width

        script_dir = os.getcwd()
        self.path_manager = PathManager(script_dir)
        self.icon_file_path = self.path_manager.get_current_root_path(
            "icon.ico"
        )
        self._validator = Validator(self.icon_file_path)
        self.msg_box = MessageBoxManager(self.icon_file_path)
        self._install_thread = InstallThread()
        self.notif_widget = NotificationWidget(
            self._ui_instance.label_information_text
        )
        self.main_button = MainButton(
            self._ui_instance.pushButton_install_and_launch,
        )

        self.input_data = self.get_input_data()
        self._boto3_client = get_boto3_instance()
        if not self._boto3_client:
            # TODO: offline mode
            sys.exit()
        self.config_loader = self.get_config_loader()
        self._update_server_type_combobox(self.config_loader)
        self.config: MinecraftLauncherConfig
        # init self.config and config_loader here:
        self.update_config()
        self.update_main_button_text()
        self._ui_instance.comboBox_server_type.currentTextChanged.connect(
            self.update_config
        )

        self._ui_instance.comboBox_server_type.currentTextChanged.connect(
            self.update_main_button_text
        )

        self._skin_uploader_thread = SkinUploaderThread(
            self._launcher_config.API_URL_PUSH_SKIN,
        )
        self._cape_uploader_thread = CapeUploaderThread(
            self._launcher_config.API_URL_PUSH_CAPE,
        )
        self._ui_instance.pushButton_delete_skin.clicked.connect(
            lambda: self._delete_user_texture(
                self._skin_uploader_thread,
            )
        )
        self._ui_instance.pushButton_delete_cape.clicked.connect(
            lambda: self._delete_user_texture(
                self._cape_uploader_thread,
            )
        )
        self._ui_instance.pushButton_choose_skin.clicked.connect(
            lambda: self._choose_skin_and_upload(
                self.config.minecraft_skin_directory
            )
        )
        self._skin_uploader_thread.finished.connect(
            self._skin_uploader_thread_finished
        )

        self._ui_instance.pushButton_choose_cape.clicked.connect(
            lambda: self._choose_cape_and_upload(
                self.config.minecraft_cape_directory
            )
        )
        self._cape_uploader_thread.finished.connect(
            self._cape_uploader_thread_finished
        )
        self._ui_instance.progressBar.hide()
        self._ui_instance.progressBar.setTextVisible(True)
        self._authorization_thread = AuthorizationThread(
            self._launcher_config.MINECRAFT_LAUNCHER_IP_ADDR
        )
        self._install_thread.progress_max.connect(
            lambda maximum: self._ui_instance.progressBar.setMaximum(maximum)
        )
        self._install_thread.progress.connect(
            lambda value: self._ui_instance.progressBar.setValue(value)
        )
        self._install_thread.text.connect(
            lambda text: self._ui_instance.progressBar.setFormat(text)
        )
        self._install_thread.finished.connect(self._install_thread_finished)

        self._ui_instance.pushButton_install_and_launch.clicked.connect(
            self._make_authorization
        )
        self._authorization_thread.finished.connect(
            self._make_authorization_finished
        )

        self.setWindowTitle("TFC-Halloween 2.0.0")

        # pylint: disable = C0301
        self._ui_instance.pushButton_minecraft_dir_disable_long_tern_save.clicked.connect(
            lambda: open_directory(
                self._launcher_config.minecraft_root_directory
            )
        )
        self.is_working = True
        self.safe_inputs_timer = QTimer()
        self.safe_inputs_timer.timeout.connect(
            self.input_data.update_input_data_from_ui
        )
        self.safe_inputs_timer.setInterval(self.input_data.time_delay)
        self.safe_inputs_timer.start()

        self.setWindowIcon(QIcon(self.icon_file_path))
        self._executor: MinecraftExecutorThread
        background_image_path = self.path_manager.get_image_path(
            "background.jpg"
        )
        self._ui_instance.label_background.setPixmap(
            QPixmap(background_image_path)
        )

        hide_console()

    def show_config_error_message(self, error: Exception) -> None:
        """Show an error message box for config updating fail."""
        msg_title = "Не удалось загрузить конфиг обновления."
        log.error(f"Failed to download a map config: {error}")
        self.msg_box.warn(
            msg_title,
            "При нажатии 'Ок' откроется папка с логом. ",
            callback=lambda: webbrowser.open(
                self._launcher_config.logging_dir,
            ),
        )

    def get_config_loader(self) -> ConfigLoader:
        """Create the configuration loader."""
        try:
            return ConfigLoader.download_from_url(self._launcher_config)
        except (RequestDownloadError, ConfigProcessingError) as error:
            log.error("Failed to download a config file from url.")
            try:
                return ConfigLoader.download_from_yos(
                    self._boto3_client,
                    self._launcher_config,
                )
            except (boto3.exceptions.Boto3Error, ConfigProcessingError):
                log.error("Failed to download a config file from yos.")
                self.show_config_error_message(error)
                # TODO: offline mode
                sys.exit()

    def _update_server_type_combobox(
        self,
        config_loader: ConfigLoader,
    ) -> None:
        """
        Update server type combobox in ui interface
        with the information from map.json.
        """
        self._ui_instance.comboBox_server_type.blockSignals(True)
        current_text = self._ui_instance.comboBox_server_type.currentText()
        self._ui_instance.comboBox_server_type.clear()
        self._ui_instance.comboBox_server_type.addItems(
            config_loader.config_list
        )
        if current_text in config_loader.config_list:
            self._ui_instance.comboBox_server_type.setCurrentText(current_text)
        else:
            self._ui_instance.comboBox_server_type.setCurrentIndex(0)
        self._ui_instance.comboBox_server_type.blockSignals(False)

    def update_config_loader(self) -> bool:
        """
        Update the configuration loader with the latest configuration.

        Returns:
            bool: False if the configuration is updated, True otherwise.
        """
        new_config_loader = self.get_config_loader()
        if new_config_loader != self.config_loader:
            self.config_loader = new_config_loader
            log.error("Config was updated.")
            msg_title = "Конфигурация серверов обновилась."
            self.msg_box.warn(
                msg_title,
                "Выберите сервер еще раз.",
            )
            # Update latest configuration in ui interface
            self._update_server_type_combobox(self.config_loader)
            return False
        return True

    def update_config(self) -> bool:
        """
        Update the configuration based on input data from the UI.

        Returns:
            bool: True if the configuration update process completes
                successfully, False otherwise.

        Notes:
            This method assumes the existence of the following attributes:
                - self.config_loader: An instance of ConfigLoader used
                    to retrieve configuration data.
                - self.input_data: An object containing input data from the UI.
                - self._install_thread: An instance of the installation thread.

        Raises:
            ConfigProcessingError: If an error occurs while processing
                the configuration.
        """

        self.input_data.update_input_data_from_ui()
        # Save user server choice
        server_type = self.input_data.extract_element("comboBox_server_type")
        try:
            self.config = self.config_loader.get_config(
                server_type,
            )
        except ConfigProcessingError as error:
            log.error(f"File to update config '{server_type}': {error}")
            msg_title = "Неизвестная ошибка."
            self.msg_box.warn(
                msg_title,
                f"Не удалось извлечь конфигурацию сервера: {server_type}.",
            )
            return False
        self._install_thread.set_config(self.config)
        return True

    def update_main_button_text(self):
        """
        Updates the text of the main button based on whether
        Minecraft is installed or not.
        """
        if self.config.is_minecraft_installed():
            self.main_button.set_launch_title()
        else:
            self.main_button.set_install_title()

    def get_input_data(self):
        """
        Returns a class instance of ThreadUiInputData with
        values of all fields in frontend inputs.

        Returns:
            ThreadUiInputData : an instance of ThreadUiInputData class
        """
        ui_data_file_path = self._launcher_config.ui_data_path
        return ThreadUiInputData(self._ui_instance, str_path=ui_data_file_path)

    def _make_authorization(self) -> None:
        if not self.update_config():
            return
        login = self.input_data.extract_element("lineEdit_nickname")
        password = self.input_data.extract_element("lineEdit_password")
        if not login or not password:
            self.msg_box.warn(
                "Не заполнен логин или пароль",
            )
            return
        self._authorization_thread.set_auth_data(login, password)
        self._authorization_thread.start()

    def _choose_skin_and_upload(self, directory: str) -> None:
        # Open a file dialog and get the selected file path
        if not os.path.exists(directory):
            os.makedirs(directory)
        username = self.input_data.extract_element("lineEdit_nickname")
        password = self.input_data.extract_element("lineEdit_password")
        skin_file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", directory
        )
        is_skin_slim = self.input_data.extract_element("radioButton_female")
        if not skin_file_path:
            self.notif_widget.show_and_close("Файл скина не выбран.")
            return
        self._skin_uploader_thread.set_data(
            username=username,
            password=password,
            selected_skin_path=skin_file_path,
            is_skin_slim=is_skin_slim,
        )
        self.notif_widget.show_and_close("Загружаю скин...")
        self._skin_uploader_thread.start()

    def _delete_user_texture(
        self, worker_thread: Union[SkinUploaderThread, CapeUploaderThread]
    ) -> None:
        username = self.input_data.extract_element("lineEdit_nickname")
        password = self.input_data.extract_element("lineEdit_password")

        worker_thread.set_data(
            username=username,
            password=password,
        )
        self.notif_widget.show_and_close("Удаляю текстуры...")
        worker_thread.start()

    def _skin_uploader_thread_finished(self):
        run_time_error = self._skin_uploader_thread.runtime_error
        if run_time_error:
            self.notif_widget.show_and_close(str(run_time_error))
            log.error(str(run_time_error))
        else:
            self.notif_widget.show_and_close("Операция завершена!")
            log.info("Операция завершена!")

    def _choose_cape_and_upload(self, directory: str) -> None:
        # Open a file dialog and get the selected file path
        if not os.path.exists(directory):
            os.makedirs(directory)
        username = self.input_data.extract_element("lineEdit_nickname")
        password = self.input_data.extract_element("lineEdit_password")
        cape_file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", directory
        )
        if not cape_file_path:
            self.notif_widget.show_and_close("Файл плаща не выбран.")
            return
        self._cape_uploader_thread.set_data(
            username=username,
            password=password,
            selected_skin_path=cape_file_path,
        )
        self.notif_widget.show_and_close("Загружаю плащ...")
        self._cape_uploader_thread.start()

    def _cape_uploader_thread_finished(self):
        run_time_error = self._cape_uploader_thread.runtime_error
        if run_time_error:
            self.notif_widget.show_and_close(str(run_time_error))
            log.error(str(run_time_error))
        else:
            self.notif_widget.show_and_close("Операция завершена!")
            log.info("Операция завершена!")

    def _make_authorization_finished(self) -> None:
        if not self._authorization_thread.runtime_error:
            self._install_minecraft_multi_thread()
        else:
            self.msg_box.warn(
                "Ошибка авторизации.",
                str(self._authorization_thread.runtime_error),
            )
            log.error(self._authorization_thread.runtime_error)

    def _install_minecraft_multi_thread(self) -> None:
        """
        Initiates the multi-threaded installation of Minecraft.

        This method shows the progress bar, disables input editing, updates
        input data from the UI, and starts the installation thread. It also
        initiates the execution of Minecraft and waits for its completion.

        Returns:
            None
        """
        if not self.update_config_loader():
            return
        self.input_data.update_input_data_from_ui()
        nickname = self.input_data.extract_element("lineEdit_nickname")
        if not self._validator.is_valid_nickname(nickname):
            return
        if not self._validator.is_java_installed():
            java_install_url = self.config.java_install_url
            install_java_link = f'<a href="{java_install_url}">\
    Я хочу установить Java сейчас!</a> '
            self.msg_box.warn(
                "Не удалось найти Java в система.",
                msg_box_info=install_java_link,
            )
            return
        self._ui_instance.progressBar.show()
        self.input_data.change_input_edit_status(bool_stop_edit=True)

        is_install_shaders = self.input_data.extract_element(
            "checkBox_is_install_shaders"
        )
        self._install_thread.change_install_shaders_status(is_install_shaders)
        self._install_thread.start()

    def _install_thread_finished(self) -> None:
        """
        Handle the completion of the installation thread.

        This method is called when the installation thread has finished
        its task. It hides the progress bar and re-enables input
        editing. It also initiates the execution of Minecraft and waits
        for its completion.
        Returns:
            None
        """
        self._ui_instance.progressBar.hide()
        if self._install_thread.runtime_error:
            msg_title = "Не удалось установить майнкрафт."
            log.error(msg_title)
            self.msg_box.warn(
                msg_title,
                "При нажатии 'Ок' откроется папка с логом. ",
                callback=lambda: webbrowser.open(
                    self._launcher_config.logging_dir,
                ),
            )
            self.input_data.change_input_edit_status(bool_stop_edit=False)
            return
        self.config.set_minecraft_installed()
        self.update_main_button_text()
        self.hide()
        auth_data = self._authorization_thread.get_last_auth_data()
        if not auth_data:
            self.msg_box.warn(
                "Критическая ошибка",
                "Tокены авторизации не инициализированы.",
            )
            return
        nickname = self.input_data.extract_element("lineEdit_nickname")
        uuid = auth_data["uuid"]
        access_token = auth_data["accessToken"]
        self._executor = MinecraftExecutorThread(
            nickname,
            uuid,
            access_token,
            self.config,
        )
        self._executor.finished.connect(self._executor_thread_finished)
        self._executor.start()

        self.input_data.change_input_edit_status(bool_stop_edit=False)

    def _executor_thread_finished(self):
        if self._executor.runtime_error:
            self.msg_box.warn(
                "Запуск игры завершился с ошибкой",
                "При нажатии 'Ок' откроется папка с логом. ",
                callback=lambda: webbrowser.open(
                    self._launcher_config.logging_dir,
                ),
            )
        self.show()

    # pylint: disable = C0103
    def closeEvent(self, event) -> None:
        """
        Override the close event of the main window.

        This method is called when the user attempts to close the application.
        It updates the input data from the UI elements and checks if all
        threads have completed their work. If not, a confirmation dialog is
        shown to confirm the user's intention to exit.

        Returns:
            None
        """
        log.debug("closeEvent entry")
        self.input_data.update_input_data_from_ui()
        self.is_working = False
        event.accept()


def handle_exception(exc_type, exc_value, exc_traceback):
    """
    Custom exception handler to catch all exceptions.
    """
    log.critical("Exception occurred:")
    log.critical(exc_type)
    log.critical(exc_value)
    log.critical(" ".join(traceback.format_tb(exc_traceback)))
    msg_box = MessageBoxManager("")

    msg_box.warn(
        "Критическая ошибка!",
        (
            "Отправьте последний файл 'log.debug' разработчику. "
            "При нажатии 'Ок' откроется папка с логом. "
        ),
        callback=lambda: webbrowser.open(LauncherConfig().logging_dir),
    )
    sys.exit(1)
    # Handle the exception or log it as needed


# Set the custom exception handler
sys.excepthook = handle_exception


def main():
    """Start application main loot"""
    app = QtWidgets.QApplication(sys.argv)

    w = Window()
    w.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
