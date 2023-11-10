"""Utillity module for creating and managing UI elements."""
from typing import Callable, Optional

from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices


class MessageBoxManager:
    """
    A utility class for creating message boxes in a PyQt application.

    Args:
        icon_file_path (str): The file path to the icon to be used in
            message boxes.

    Attributes:
        icon_file_path (str): The file path to the icon used in message boxes.
    """

    def __init__(self, icon_file_path: str):
        self.icon_file_path = icon_file_path

    # pylint: disable = R0913
    def create_msg_box(
        self,
        msg_box_title: str,
        msg_box_icon: QtWidgets.QMessageBox.Icon,
        msg_box_info: str = "",
        msg_box_window_title: Optional[str] = "Ошибка",
        callback: Optional[Callable[[], None]] = None,
    ) -> None:
        """
        Create a simple message box with the specified parameters and execute
        an optional callback function after it's closed.

        Args:
            msg_box_title (str): The title of the message box.
            msg_box_icon (QtWidgets.QMessageBox.Icon): The icon for
                the message box.
            msg_box_info (str, optional): Additional informative text for
                the message box.
            msg_box_window_title: Optional[str] : Title text of msg_box.
            callback (Optional[Callable[[], None]]): A callback function to be
                executed after the message box is closed.
        """
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle(msg_box_window_title)
        msg.setIcon(msg_box_icon)
        msg.setWindowIcon(QtGui.QIcon(self.icon_file_path))
        msg.setText(msg_box_title)
        msg.setInformativeText(msg_box_info)
        msg.exec()
        if callback is not None:
            callback()

    def info(
        self,
        msg_box_title: str,
        msg_box_info: str = "",
        callback: Optional[Callable[[], None]] = None,
    ) -> None:
        """Create an information message box"""
        self.create_msg_box(
            msg_box_title=msg_box_title,
            msg_box_icon=QtWidgets.QMessageBox.Icon.Information,
            msg_box_info=msg_box_info,
            msg_box_window_title="Уведомление",
            callback=callback,
        )

    def warn(
        self,
        msg_box_title: str,
        msg_box_info: str = "",
        callback: Optional[Callable[[], None]] = None,
    ) -> None:
        """Create a warning message box."""
        self.create_msg_box(
            msg_box_title=msg_box_title,
            msg_box_icon=QtWidgets.QMessageBox.Icon.Warning,
            msg_box_info=msg_box_info,
            msg_box_window_title="Ошибка",
            callback=callback,
        )


def open_directory(path_to_directory: str):
    """
    Open the file explorer at the specified directory.

    Args:
        path_to_directory (str): The path to the directory to be opened.
    """
    url = QUrl.fromLocalFile(path_to_directory)
    QDesktopServices.openUrl(url)
