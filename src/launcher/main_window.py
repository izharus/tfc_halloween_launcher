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

import win32con
import win32console
import win32gui
from log_wizard import log as get_logger
from PyQt6 import QtWidgets
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon, QPixmap

from .data_validation import Validator
from .design.design import Ui_MainWindow
from .design.utillity import MainButton, MessageBoxManager, open_directory
from .launcher_configs import (
    LauncherConfig,
    MinecraftLauncherConfig,
    get_config,
)
from .launcher_installer import InstallThread, MinecraftExecutorThread
from .utillity.path_manager import PathManager
from .utillity.thread_data_utils import ThreadUiInputData

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

        self.main_button = MainButton(
            self._ui_instance.pushButton_install_and_launch,
        )

        self._ui_instance.comboBox_server_type.currentTextChanged.connect(
            self.update_config
        )
        self._ui_instance.comboBox_server_type.currentTextChanged.connect(
            self.update_main_button_text
        )

        self.input_data = self.get_input_data()

        self.config: MinecraftLauncherConfig

        # init self.config here:
        self.update_config()
        self.update_main_button_text()
        self._ui_instance.progressBar.hide()
        self._ui_instance.progressBar.setTextVisible(True)

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
            self._install_minecraft_multi_thread
        )

        self.setWindowTitle("TFC-Halloween 1.0.0")

        # pylint: disable = C0301
        self._ui_instance.pushButton_minecraft_dir_disable_long_tern_save.clicked.connect(
            lambda: open_directory(self.config.minecraft_directory)
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

    def update_config(self):
        """
        Update configuration based on UI input.

        Fetches the selected server type, updates input data,
        creates a new configuration, retrieves stored data, and
        sets the configuration for the installation thread.
        """
        self.input_data.update_input_data_from_ui()
        self.config = get_config(
            self.input_data.extract_element("comboBox_server_type")
        )()
        self.config.get_stored_data()
        self._install_thread.set_config(self.config)

    def update_main_button_text(self):
        """
        Updates the text of the main button based on whether
        Minecraft is installed or not.
        """
        if self.config.is_minecraft_installed():
            self.main_button.set_launch_text()
        else:
            self.main_button.set_install_title()

    def get_input_data(self):
        """
        Returns a class instance of ThreadUiInputData with
        values of all fields in frontend inputs.

        Returns:
            ThreadUiInputData : an instance of ThreadUiInputData class
        """
        ui_data_file_path = LauncherConfig.ui_data_path
        return ThreadUiInputData(self._ui_instance, str_path=ui_data_file_path)

    def _install_minecraft_multi_thread(self) -> None:
        """
        Initiates the multi-threaded installation of Minecraft.

        This method shows the progress bar, disables input editing, updates
        input data from the UI, and starts the installation thread. It also
        initiates the execution of Minecraft and waits for its completion.

        Returns:
            None
        """
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
                    LauncherConfig.logging_dir,
                ),
            )
            self.input_data.change_input_edit_status(bool_stop_edit=False)
            return
        self.hide()

        nickname = self.input_data.extract_element("lineEdit_nickname")
        self._executor = MinecraftExecutorThread(nickname, self.config)
        self._executor.finished.connect(self._executor_thread_finished)
        self._executor.start()

        self.input_data.change_input_edit_status(bool_stop_edit=False)

    def _executor_thread_finished(self):
        if self._executor.runtime_error:
            self.msg_box.warn(
                "Запуск игры завершлися с ошибкой",
                "При нажатии 'Ок' откроется папка с логом. ",
                callback=lambda: webbrowser.open(
                    LauncherConfig.logging_dir,
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
    log.critical(traceback.format_tb(exc_traceback))
    msg_box = MessageBoxManager("")

    msg_box.warn(
        "Критическая ошибка!",
        (
            "Отправьте последний файл 'log.debug' разработчику. "
            "При нажатии 'Ок' откроется папка с логом. "
        ),
        callback=lambda: webbrowser.open(LauncherConfig.logging_dir),
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
