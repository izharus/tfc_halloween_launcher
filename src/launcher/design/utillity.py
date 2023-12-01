"""Utillity module for creating and managing UI elements."""
from typing import Any, Callable, Optional

from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QLabel, QPushButton, QWidget

from .styles import MainButtonData


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

        if callback is not None and msg.clickedButton() == ok_button:
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


class NotificationWidget(QWidget):
    """
    Custom widget for displaying notifications with optional animations.
    """

    def __init__(self, qlabel: QLabel) -> None:
        """Initialize the NotificationWidget."""
        super().__init__()
        self.qlabel = qlabel
        self.qlabel.hide()
        self.timer: int = 0

    def show_and_close(self, message: str, duration_ms=6000):
        """
        Display the notification with the given message for the specified
        duration.
        """
        self.qlabel.setText(message)
        self.qlabel.show()
        self.timer = self.startTimer(duration_ms)

    # pylint: disable=C0103
    def timerEvent(self, event):
        """
        Handle the timer event to hide the notification when the
        timer expires.
        """
        self.killTimer(event.timerId())
        self.qlabel.hide()


# pylint: disable=R0903
class ButtonBase:
    """
    Base class for managing the title of a QPushButton instance.
    """

    def __init__(self, button_instance: QPushButton) -> None:
        self._instance = button_instance

    def set_title(self, text: str) -> None:
        """
        Set the title of the associated QPushButton.
        """
        self._instance.setText(text)


class MainButton(MainButtonData):
    """
    Subclass of MainButtonData for managing titles of specific buttons.
    """

    def __init__(self, object_instance):
        MainButtonData.__init__(object_instance)
        self._instance = object_instance

    def set_install_title(self):
        """
        Set the title of the associated button to the install text.
        """
        self._instance.setText(self.install_text)

    def set_launch_text(self):
        """
        Set the title of the associated button to the launch text.
        """
        self._instance.setText(self.launch_text)


def open_directory(path_to_directory: str):
    """
    Open the file explorer at the specified directory.

    Args:
        path_to_directory (str): The path to the directory to be opened.
    """
    url = QUrl.fromLocalFile(path_to_directory)
    QDesktopServices.openUrl(url)
