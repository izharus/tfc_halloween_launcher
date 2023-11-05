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

    def create_msg_box(
        self,
        msg_box_title: str,
        msg_box_icon: QtWidgets.QMessageBox.Icon,
        msg_box_info: str = "",
        callback_function: Optional[Callable] = None,
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
            callback_function (Callable, optional): A function to be
                executed after the message box is closed.
        """
        msg = QtWidgets.QMessageBox()
        msg.setIcon(msg_box_icon)
        msg.setWindowIcon(QtGui.QIcon(self.icon_file_path))
        msg.setText(msg_box_title)
        msg.setInformativeText(msg_box_info)
        msg.exec()
        if callback_function and callable(callback_function):
            callback_function()

    def info(
        self,
        msg_box_title: str,
        msg_box_info: str = "",
        callback_function: Optional[Callable] = None,
    ) -> None:
        """Create an information message box"""
        self.create_msg_box(
            msg_box_title=msg_box_title,
            msg_box_icon=QtWidgets.QMessageBox.Icon.Information,
            msg_box_info=msg_box_info,
            callback_function=callback_function,
        )

    def warn(
        self,
        msg_box_title: str,
        msg_box_info: str = "",
        callback_function: Optional[Callable] = None,
    ) -> None:
        """Create a warning message box."""
        self.create_msg_box(
            msg_box_title=msg_box_title,
            msg_box_icon=QtWidgets.QMessageBox.Icon.Warning,
            msg_box_info=msg_box_info,
            callback_function=callback_function,
        )


def open_directory(path_to_directory: str):
    """
    Open the file explorer at the specified directory.

    Args:
        path_to_directory (str): The path to the directory to be opened.
    """
    url = QUrl.fromLocalFile(path_to_directory)
    QDesktopServices.openUrl(url)
