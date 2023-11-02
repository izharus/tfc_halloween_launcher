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

import logging
import os
import sys
import threading

import win32con
import win32console
import win32gui
from PyQt6 import QtWidgets
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon

from .design.design import Ui_MainWindow
from .launcher_installer import (
    InstallShadersThread,
    InstallThread,
    MinecraftExecuterThread,
    MinecraftLauncherConfig,
    init_logging_basic_config,
)
from .utillity.path_manager import PathManager
from .utillity.thread_data_utils import ThreadUiInputData


def hide_console() -> None:
    """
    Hides console windows.

    Returns:
        None
    """
    window = win32console.GetConsoleWindow()
    win32gui.ShowWindow(window, win32con.SW_HIDE)


hide_console()


class Window(QtWidgets.QMainWindow):
    """Main window of app"""

    def __init__(self) -> None:
        super().__init__()
        self._ui_instance = Ui_MainWindow()

        self._ui_instance.setupUi(self)
        self.resize(500, 125)  # Adjust 800 to your desired width

        self._install_thread = InstallThread()
        self._install_shaders_thread = InstallShadersThread()

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

        self._install_shaders_thread.progress_max.connect(
            lambda maximum: self._ui_instance.progressBar.setMaximum(maximum)
        )
        self._install_shaders_thread.progress.connect(
            lambda value: self._ui_instance.progressBar.setValue(value)
        )
        self._install_shaders_thread.text.connect(
            lambda text: self._ui_instance.progressBar.setFormat(text)
        )
        self._install_shaders_thread.finished.connect(
            self._install_shaders_thread_finished
        )

        self._ui_instance.pushButton_install_shaders.clicked.connect(
            self._install_shaders
        )
        self._ui_instance.pushButton_install_and_launch.clicked.connect(
            self._install_minecraft_multi_thread
        )

        ui_data_file_path = MinecraftLauncherConfig.minecraft_directory
        ui_data_file_path = os.path.join(
            ui_data_file_path,
            "halloween_data\\ui_inputs_data\\input_data",
        )
        self.setWindowTitle("TFC-Halloween")
        self.input_data = ThreadUiInputData(
            self._ui_instance, str_path=ui_data_file_path
        )

        self.is_working = True
        self.safe_inputs_timer = QTimer()
        self.safe_inputs_timer.timeout.connect(
            self.input_data.update_input_data_from_ui
        )
        self.safe_inputs_timer.setInterval(self.input_data.time_delay)
        self.safe_inputs_timer.start()

        log_dir = MinecraftLauncherConfig.minecraft_directory
        log_dir = os.path.join(log_dir, "halloween_logs")

        init_logging_basic_config(log_dir)
        script_dir = os.path.dirname(__file__)
        self.path_manager = PathManager(script_dir)
        icon_file_path = self.path_manager.get_current_root_path("icon.ico")
        self.setWindowIcon(QIcon(icon_file_path))

    def _install_shaders(self) -> None:
        """
        Initiates the installation of shaders.

        This method shows the progress bar and disables input editing to start
        the installation of shaders in a separate thread.

        Returns:
            None
        """
        self._ui_instance.progressBar.show()
        self.input_data.change_input_edit_status(bool_stop_edit=True)
        self._install_shaders_thread.start()

    def _install_thread_finished(self) -> None:
        """
        Handles the completion of the installation thread.

        This method hides the progress bar and enables input editing.

        Returns:
            None
        """
        self._ui_instance.progressBar.hide()
        self.input_data.change_input_edit_status(bool_stop_edit=False)

    def _install_shaders_thread_finished(self) -> None:
        """
        Handles the completion of the shaders installation thread.

        This method hides the progress bar, enables input editing, and displays
        a message box indicating the result of the shaders installation.

        Returns:
            None
        """
        self._ui_instance.progressBar.hide()
        self.input_data.change_input_edit_status(bool_stop_edit=False)
        if self._install_shaders_thread.is_last_install_failed():
            logging.error("Не удалось установить шейдеры")
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
            msg.setText("Не удалось установить шейдеры.")
            self._ui_instance.progressBar.hide()
            msg.exec()
            return
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
        msg.setText("Shaders were installed!")
        msg.setInformativeText("Turn on shaders in the game settings.")

        msg.exec()

    def execute_minecraft_and_wait(self, set_visibility_flag):
        """
        Executes Minecraft and waits for the execution to complete.

        This method initiates the execution of Minecraft with the specified
        nickname and waits for the execution to finish. It also handles the
        visibility of the progress bar and displays error messages if
        necessary.

        Args:
            set_visibility_flag (function): A function to set the visibility
                state of UI elements.

        Returns:
            None
        """
        if not self.is_working:
            return
        if self._install_thread.is_working:
            logging.info("Ожиданию установку..")
            threading.Timer(
                2, self.execute_minecraft_and_wait, args=[set_visibility_flag]
            ).start()
            return

        if self._install_thread.is_last_install_failed():
            logging.critical("Не удалось установить майнкрафт.")
            msg = QtWidgets.QMessageBox()
            msg.setText("Не удалось установить майнкрафт.")
            msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
            msg.exec()
            return
        nickname = self.input_data.extract_element("lineEdit_nickname")
        executer = MinecraftExecuterThread(nickname)
        thread = threading.Thread(target=executer.execute_minecraft)
        set_visibility_flag(False)
        thread.start()
        thread.join()
        set_visibility_flag(True)
        self._ui_instance.progressBar.hide()
        self._ui_instance.progressBar.setFormat("")

    def _install_minecraft_multi_thread(self) -> None:
        """
        Initiates the multi-threaded installation of Minecraft.

        This method shows the progress bar, disables input editing, updates
        input data from the UI, and starts the installation thread. It also
        initiates the execution of Minecraft and waits for its completion.

        Returns:
            None
        """
        self._ui_instance.progressBar.show()
        self.input_data.change_input_edit_status(bool_stop_edit=True)
        self.input_data.update_input_data_from_ui()
        self._install_thread.start()

        threading.Timer(
            1,
            self.execute_minecraft_and_wait,
            args=[lambda flag: self.setVisible(flag)],
        ).start()

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
        logging.debug("closeEvent entry")
        self.input_data.update_input_data_from_ui()
        self.is_working = False
        event.accept()


def main():
    """Start application main loot"""
    app = QtWidgets.QApplication(sys.argv)

    w = Window()
    w.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
