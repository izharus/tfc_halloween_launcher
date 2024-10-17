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
from typing import Optional

import win32con
import win32console
import win32gui
from loguru import logger as log
from qtpy import QtWidgets
from qtpy.QtCore import QPoint, Qt, Slot
from qtpy.QtGui import QIcon
from src.launcher.boto3_cred import BOTO3_ACCESS_KEY, BOTO3_SECRET_KEY

from .choose_server import ChoseServer
from .data_validation import Validator
from .design.design import Ui_MainWindow
from .design.thread_data_utils import SettingsManager
from .design.utility import LogMessageBox, MessageBox, open_directory
from .launcher_configs import LauncherConfig, ServerConfig, ServerConfigManager
from .launcher_installer import (
    ConfigInstallerThread,
    InstallThread,
    MinecraftExecutorThread,
)
from .login_widget import LoginWidget
from .settings_widget import SettingsWidget
from .utility.custom_exceptions import (
    ConfigDownloadError,
    ConfigProcessingError,
    DownloadServerHandshakeError,
)
from .utility.file_downloader import FileYOSDownloader
from .utility.path_manager import PathManager


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

        # For mouse events
        self._mouse_click_pos: Optional[QPoint] = None

        logging_dir = self._launcher_config.logging_dir
        logging_dir += "/launcher_{time:YYYY-MM}.log"
        log.add(
            logging_dir,
            rotation="1 month",
            retention="1 month",  # Retain log files for 1 month after rotation
            compression="zip",  # Optional: Enable compression for rotated logs
            level="DEBUG",
            serialize=False,
        )
        self._ui_instance.setupUi(self)
        self.resize(500, 125)  # Adjust 800 to your desired width

        script_dir = os.getcwd()
        self.path_manager = PathManager(script_dir)
        self.icon_file_path = self.path_manager.get_current_root_path(
            "icon.ico"
        )
        self._validator = Validator()
        self.msg_box = MessageBox(self._ui_instance.widget_main_window)
        self.log_msg_box = LogMessageBox(self._ui_instance.widget_main_window)

        try:
            self.file_downloader = FileYOSDownloader(
                aws_access_key_id=BOTO3_ACCESS_KEY,
                aws_secret_access_key=BOTO3_SECRET_KEY,
                bucket_name=LauncherConfig.BUCKET_NAME,
            )
        except DownloadServerHandshakeError as error:
            log.critical(f"Failed to install boto3: {error}")
            self.log_msg_box.show_message(
                title="Сетевая ошибка!",
                msg="Не удалось связаться с сервером загрузки.",
                close_button_text="закрыть приложение",
            )
            sys.exit(1)

        self._install_thread = InstallThread(self.file_downloader)

        self._settings = SettingsManager(
            ui_instance=self._ui_instance.centralwidget,
            company_name="IzharusTest",
            app_name="TestApp",
        )
        self._settings.update_ui_signal.connect(self._settings.set_value_to_ui)
        self.config_manager: ServerConfigManager
        self._choose_server: ChoseServer
        self._server_config: ServerConfig

        # This widget connects signals in _connect_signals
        self._settings_widget = SettingsWidget
        # This widget connects signals in _connect_signals
        self._login_widget = LoginWidget(
            self._ui_instance,
            self._launcher_config,
            settings=self._settings,
        )
        self._config_installer_thread = ConfigInstallerThread(
            file_downloader=self.file_downloader,
            map_json_object_key=self._launcher_config.MAP_JSON_YOS_OBJ_KEY,
        )

        # Start _config_installer_thread only after successful authentication
        self._login_widget.authentication_complete.connect(
            self._config_installer_thread.start
        )
        # Connect _config_installer_thread to the error log widget
        self._config_installer_thread.write_error.connect(
            self._login_widget.write_error
        )
        # Connect _config_installer_thread to the info log widget
        self._config_installer_thread.write_info.connect(
            self._login_widget.info_label.setText
        )

        # Update config after successful config installation
        self._config_installer_thread.success.connect(
            self._config_installer_complete
        )

        # Enable UI until all operations are completed
        self._config_installer_thread.finished.connect(
            self._login_widget.enable_ui
        )

        self._install_thread.finished.connect(self._install_thread_finished)
        self.setWindowTitle("TFC-Halloween 3.0.3")
        self._ui_instance.pushButton_close_app.clicked.connect(self.close)
        self._ui_instance.pushButton_collapse_app.clicked.connect(
            self.showMinimized
        )
        # pylint: disable = C0301
        self._ui_instance.pushButton_minecraft_dir_disable_long_tern_save.clicked.connect(
            lambda: open_directory(
                self._launcher_config.minecraft_root_directory
            )
        )
        self.is_working = True

        self.setWindowIcon(QIcon(self.icon_file_path))
        self._executor: MinecraftExecutorThread
        self._init_background()
        hide_console()

    def _init_background(self):
        self.setWindowFlags(
            Qt.Window | Qt.FramelessWindowHint | Qt.WindowSystemMenuHint
        )

        # remove frame
        self.setWindowFlag(Qt.FramelessWindowHint)
        # make the main window transparent
        self.setAttribute(Qt.WA_TranslucentBackground)

        self._ui_instance.widget_main_window.setStyleSheet(
            """
            #widget_main_window {
            background-image: url(:/data/background/main_back.jpg);
            border-radius: 50px;
            }
            """
        )

    def _config_installer_complete(self):
        self.config_manager = self._config_installer_thread.config_manager
        # This widget connects signals in _connect_signals
        self._settings_widget = SettingsWidget(
            self._ui_instance,
            self._launcher_config,
            settings=self._settings,
        )
        self._choose_server = ChoseServer(
            self._ui_instance, self.config_manager
        )

        self._choose_server.launch_game.connect(
            self._install_minecraft_multi_thread
        )
        self._ui_instance.stackedWidget.setCurrentWidget(
            self._ui_instance.choose_server_page
        )

        self._install_thread.progress_max.connect(
            lambda maximum: self._choose_server.progress_bar.setMaximum(
                maximum
            )
        )
        self._install_thread.progress.connect(
            lambda value: self._choose_server.progress_bar.setValue(value)
        )
        self._install_thread.text.connect(
            lambda text: self._choose_server.progress_bar.setFormat(text)
        )

    # pylint: disable=C0103
    def mousePressEvent(self, event):
        """
        Handles the mouse button press event.

        If the left mouse button is pressed, stores the position of the mouse
        relative to the top-left corner of the widget's frame.
        """
        if event.button() == Qt.LeftButton:
            self._mouse_click_pos = (
                event.globalPos() - self.frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event):
        """
        Handles the mouse movement event.

        If the left mouse button is pressed and a click position is stored,
        moves the widget to the new position based on the current mouse
        position.
        """
        if (
            event.buttons() == Qt.LeftButton
            and self._mouse_click_pos is not None
        ):
            self.move(event.globalPos() - self._mouse_click_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Handles the mouse button release event.

        If the left mouse button is released, resets the stored click position
        to None.
        """
        if event.button() == Qt.LeftButton:
            self._mouse_click_pos = None
            # event.accept()

    @Slot(str)
    def _install_minecraft_multi_thread(self, config_name: str) -> None:
        """
        Initiates the multi-threaded installation of Minecraft.

        This method shows the progress bar, disables input editing, updates
        input data from the UI, and starts the installation thread. It also
        initiates the execution of Minecraft and waits for its completion.

        Returns:
            None
        """
        self._choose_server.info_label.setText("Получение обновлений...")
        self._choose_server.disable_ui(show_progress=True)

        try:
            self.config_manager.update_config()
        except ConfigProcessingError:
            self.log_msg_box.show_message(
                title="Ошибка на нашей стороне!",
                msg="Не удалось обработать конфиг обновления. "
                "Отправьте лог разработчику.",
            )
            # TODO: context manager or other solution
            self._choose_server.enable_ui()
            return
        except ConfigDownloadError:
            self.msg_box.show_message(
                title="Не удалось получить обновления.",
                msg="Проверьте соединение с сетью.",
            )
            self._choose_server.enable_ui()
            return
        modpack_model = self.config_manager.get_config(config_name)
        if not modpack_model:

            self.msg_box.show_message(
                title="Получены обновления",
                msg="Попробуйте запустить игру снова.",
            )

            self._choose_server.enable_ui()
            return

        self._server_config = ServerConfig(
            config_name,
            modpack_model,
            self._launcher_config,
            self._settings,
        )
        self._install_thread.set_config(self._server_config)

        if not self._validator.is_java_installed():
            java_install_url = self._launcher_config.JAVA_INSTALL_URL
            self.msg_box.show_message(
                title="Ошибка Java",
                msg="Загрузите последнюю версию Java.\n" + java_install_url,
                close_button_text="закрыть приложение",
            )
            # After installation user should restart app
            sys.exit(1)

        is_install_shaders = self._settings.get_ui_value(
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
        if self._install_thread.runtime_error:
            msg_title = "Не удалось установить майнкрафт."
            log.error(msg_title)
            self.log_msg_box.show_message(
                title=msg_title,
                msg="Подробная информация в логе.",
            )
            self._choose_server.enable_ui()
            return
        self._server_config.is_minecraft_installed = True
        self.hide()
        auth_data = self._login_widget.auth_data
        if not auth_data:
            self.log_msg_box.show_message(
                title="Критическая ошибка",
                msg="Tокены авторизации не инициализированы.",
                close_button_text="закрыть приложение",
            )
            sys.exit(1)
        nickname = self._settings.get_ui_value("lineEdit_nickname")
        uuid = auth_data.uuid
        access_token = auth_data.accessToken
        self._executor = MinecraftExecutorThread(
            nickname,
            uuid,
            access_token,
            self._server_config,
        )
        self._executor.finished.connect(self._executor_thread_finished)
        self._executor.start()

    def _executor_thread_finished(self):
        if self._executor.runtime_error:
            self.log_msg_box(
                title="Ошибка при запуске игры.",
                msg="Подробная информация в логе.",
            )
        self._choose_server.enable_ui()
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
        self.is_working = False
        event.accept()


def handle_exception(exc_type, exc_value, exc_traceback):
    """
    Custom exception handler to catch all exceptions.
    """

    config = LauncherConfig()
    log.critical("Exception occurred:")
    log.critical(exc_type)
    log.critical(exc_value)
    log.critical(" ".join(traceback.format_tb(exc_traceback)))
    msg_box = LogMessageBox(None)
    msg_box.show_message(
        title="Критическая ошибка!",
        msg="Отправьте последний текстовый файл разработчику: "
        + f"{config.DEVELOPER_EMAIL}",
        close_button_text="закрыть приложение",
    )
    sys.exit(1)


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
