"""Utillity module for creating and managing UI elements."""
from typing import Any, Callable, Optional

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
        msg_box_window_title: str = "Ошибка",
        callback: Optional[Callable[[], Any]] = None,
    ) -> None:
        """
        Create and display a QMessageBox with customizable parameters.

        Parameters:
        - msg_box_title (str): The title of the QMessageBox.
        - msg_box_icon (QtWidgets.QMessageBox.Icon): The icon to be
            displayed in the QMessageBox.
        - msg_box_info (str, optional): Additional information to be
            displayed in the QMessageBox.
        - msg_box_window_title (str, optional): The title of the QMessageBox
            window.
        - callback (Optional[Callable[[], None]], optional): A callback
            function to be executed on button click.

        Returns:
        None
        """
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle(msg_box_window_title)
        msg.setIcon(msg_box_icon)
        msg.setWindowIcon(QtGui.QIcon(self.icon_file_path))
        msg.setText(msg_box_title)
        msg.setInformativeText(msg_box_info)

        if callback:
            # Add custom buttons
            ok_button = msg.addButton(
                "OK",
                QtWidgets.QMessageBox.ButtonRole.AcceptRole,
            )
            msg.addButton(
                "Cancel",
                QtWidgets.QMessageBox.ButtonRole.RejectRole,
            )

        msg.exec()

        if msg.clickedButton() == ok_button and callback is not None:
            callback()

    def info(
        self,
        msg_box_title: str,
        msg_box_info: str = "",
        callback: Optional[Callable[[], Any]] = None,
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
        callback: Optional[Callable[[], Any]] = None,
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
