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
from typing import Dict, Optional, Union

import win32con
import win32console
import win32gui
from loguru import logger as log
from qtpy import QtWidgets
from qtpy.QtCore import QPoint, Qt, QTimer, Slot
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QFileDialog
from src.launcher.boto3_cred import BOTO3_ACCESS_KEY, BOTO3_SECRET_KEY

from .choose_server import ChoseServer
from .data_validation import Validator
from .design.design import Ui_MainWindow
from .design.utility import (
    CustomMessageBox,
    NotificationWidget,
    open_directory,
)
from .launcher_authorization import CapeUploaderThread, SkinUploaderThread
from .launcher_configs import LauncherConfig, ServerConfig, ServerConfigManager
from .launcher_installer import (
    ConfigInstallerThread,
    InstallThread,
    MinecraftExecutorThread,
)
from .login_widget import LoginWidget
from .utility.custom_exceptions import (
    ConfigDownloadError,
    ConfigProcessingError,
    DownloadServerHandshakeError,
)
from .utility.file_downloader import FileYOSDownloader
from .utility.path_manager import PathManager
from .utility.thread_data_utils import ThreadUiInputData

OFFLINE_MAP_JSON: Dict = {
    "ОБНОВИТЬ": {},
}


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
        self.msg_box = CustomMessageBox()

        self.notif_widget = NotificationWidget(
            self._ui_instance.label_information_text
        )

        try:
            self.file_downloader = FileYOSDownloader(
                aws_access_key_id=BOTO3_ACCESS_KEY,
                aws_secret_access_key=BOTO3_SECRET_KEY,
                bucket_name=LauncherConfig.BUCKET_NAME,
            )

        except DownloadServerHandshakeError as error:
            log.critical(f"Failed to install boto3: {error}")
            self.msg_box.close_button.setText("закрыть приложение")
            self.msg_box.show_message_with_logs(
                "Сетевая ошибка!", "Не удалось связаться с сервером загрузки."
            )
            sys.exit(1)

        self._install_thread = InstallThread(self.file_downloader)

        self.input_data = self.get_input_data()
        self._skin_uploader_thread = SkinUploaderThread(
            self._launcher_config.API_URL_PUSH_SKIN,
        )

        self.config_manager: ServerConfigManager
        self._choose_server: ChoseServer
        self._server_config: ServerConfig
        # This widget connects signals in _connect_signals
        self._login_widget = LoginWidget(
            self._ui_instance, self._launcher_config.MINECRAFT_LAUNCHER_IP_ADDR
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
                self._launcher_config.minecraft_skin_directory
            )
        )
        self._skin_uploader_thread.finished.connect(
            self._skin_uploader_thread_finished
        )

        self._ui_instance.pushButton_choose_cape.clicked.connect(
            lambda: self._choose_cape_and_upload(
                self._launcher_config.minecraft_cape_directory
            )
        )
        self._cape_uploader_thread.finished.connect(
            self._cape_uploader_thread_finished
        )
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
        self.safe_inputs_timer = QTimer()
        self.safe_inputs_timer.timeout.connect(
            self.input_data.update_input_data_from_ui
        )
        self.safe_inputs_timer.setInterval(self.input_data.time_delay)
        self.safe_inputs_timer.start()

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
        self._choose_server = ChoseServer(
            self._ui_instance, self.config_manager
        )

        self._choose_server.launch_game.connect(
            self._install_minecraft_multi_thread
        )
        self._ui_instance.stackedWidget.setCurrentWidget(
            self._ui_instance.choose_server_page
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

    def get_input_data(self):
        """
        Returns a class instance of ThreadUiInputData with
        values of all fields in frontend inputs.

        Returns:
            ThreadUiInputData : an instance of ThreadUiInputData class
        """
        ui_data_file_path = self._launcher_config.ui_data_path
        return ThreadUiInputData(self._ui_instance, str_path=ui_data_file_path)

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
        self._choose_server.block_ui()

        try:
            self.config_manager.update_config()
        except ConfigProcessingError:
            self.msg_box.show_message_with_logs(
                "Ошибка на нашей стороне!",
                "Не удалось обработать конфиг обновления. "
                "Отправьте лог разработчику.",
            )
            # TODO: context manager or other solution
            self._choose_server.enable_ui()
            return
        except ConfigDownloadError:
            self.msg_box.show_message(
                "Не удалось получить обновления.",
                "Проверьте соединение с сетью.",
            )
            self._choose_server.enable_ui()
            return
        modpack_model = self.config_manager.get_config(config_name)
        if not modpack_model:

            self.msg_box.show_message(
                "Получены обновления", "Попробуйте запустить игру снова."
            )

            self._choose_server.enable_ui()
            return

        self._server_config = ServerConfig(
            config_name,
            modpack_model.model_dump(),
            self._launcher_config,
        )
        self._install_thread.set_config(self._server_config)
        self.input_data.update_input_data_from_ui()

        if not self._validator.is_java_installed():
            java_install_url = self._launcher_config.JAVA_INSTALL_URL
            self.msg_box.close_button.setText("закрыть приложение")
            self.msg_box.show_message(
                "Ошибка Java",
                "Загрузите последнюю версию Java.\n" + java_install_url,
            )
            # After installation user should restart app
            sys.exit(1)
        self._ui_instance.progressBar.show()

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
            self.msg_box.show_message_with_logs(
                msg_title,
                "Подробная информация в логе.",
            )
            self._choose_server.enable_ui()
            return
        self._server_config.is_minecraft_installed = True
        self.hide()
        auth_data = self._login_widget.auth_data
        if not auth_data:
            self.msg_box.close_button.setText("закрыть приложение")
            self.msg_box.show_message_with_logs(
                "Критическая ошибка",
                "Tокены авторизации не инициализированы.",
            )
            sys.exit(1)
        nickname = self.input_data.extract_element("lineEdit_nickname")
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
            self.msg_box.show_message_with_logs(
                "Ошибка при запуске игры.",
                "Подробная информация в логе.",
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
        self.input_data.update_input_data_from_ui()
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
    msg_box = CustomMessageBox()
    msg_box.close_button.setText("Закрыть приложение")
    msg_box.show_message_with_logs(
        "Критическая ошибка!",
        "Отправьте последний текстовый файл разработчику: "
        + f"{config.DEVELOPER_EMAIL}",
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
