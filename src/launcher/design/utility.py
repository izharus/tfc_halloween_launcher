"""Utility module for creating and managing UI elements."""

from typing import Optional

from qtpy.QtCore import Qt, QUrl
from qtpy.QtGui import QDesktopServices, QFont, QPixmap
from qtpy.QtWidgets import (
    QDialog,
    QGraphicsBlurEffect,
    QHBoxLayout,
    QLabel,
    QLayout,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .styles import CUSTOM_MESSAGE_BOX_STYLE, MainButtonData, ServerWidgetCSS
from ..launcher_configs import LauncherConfig
import webbrowser
class CustomMessageBox(QDialog):
    """
    A custom message box that displays a message
    and allows the user to close it.

    Attributes:
        widget (QWidget): The main container widget for the message box.
        main_layout (QVBoxLayout): The main layout for the dialog.
        close_button (QPushButton): The button to close the message box.
        button_layout (QHBoxLayout): The layout for positioning
            the close button.
        _text_edit (QTextEdit): A text edit widget that displays the message.
    """

    def __init__(self):
        """Initializes the CustomMessageBox with a translucent background
        and a close button.
        """
        super().__init__()
        self.setWindowFlags(
            Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Implement the custom widget to avoid visual bugs with border-radius
        container_widget = QWidget()

        self.widget = container_widget
        # User copy-able textEdit.
        self._text_edit = QTextEdit(self.widget)
        self._text_edit.setText("Критическая ошибка!")
        self._text_edit.setReadOnly(True)
        self._text_edit.setFrameStyle(QTextEdit.NoFrame)
        self._text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._text_edit.setAcceptRichText(False)
        self._text_edit.setFixedSize(300, 150)

        # Button for closing this widget
        self.close_button = QPushButton("закрыть")
        self.close_button.clicked.connect(self.accept)

        # Adjust button size as its text
        # Put button into the middle of widget
        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.close_button)
        self.button_layout.addStretch()

        # Create a button for opening logs
        self._log_button = QPushButton(self.widget)
        self._log_button.setText("папка с логами")
        self.button_layout.addWidget(self._log_button)
        self._log_button.clicked.connect(
            lambda: webbrowser.open(LauncherConfig().logging_dir))
        # Main widget's layout
        layout = QVBoxLayout()
        layout.addWidget(self._text_edit)
        layout.addLayout(self.button_layout)

        container_widget.setLayout(layout)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(container_widget)

        self.setStyleSheet(CUSTOM_MESSAGE_BOX_STYLE)

        self._widget = container_widget
    @staticmethod
    def _format_title(title: str) -> str:
        return ("<h2 style='text-align: center;'>"
                f"{title}</h2>\n"
        )
    @staticmethod
    def _format_msg(msg: str) -> str:
        return ("<p style='text-align: center;'>"
                f"{msg}</p>\n"
        )
    
    def show_message(self, title: str, msg: str) -> None:
        """Show message box."""

        self._log_button.hide()
        self._text_edit.setText(
            self._format_title(title) + self._format_msg(msg)
            )
        self.exec()
    def show_message_with_logs(self, title: str, msg: str) -> None:
        """Show message box with button for opening logs."""
        self._log_button.show()
        self._text_edit.setText(
            self._format_title(title) + self._format_msg(msg)
            )

        self.exec()
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

    def set_launch_title(self):
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


def clear_layout(layout: QLayout) -> None:
    """Recursively removes all widgets and layouts from the given layout.

    Args:
        layout (QLayout): The layout to clear.
    """

    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
        else:
            if item.layout() is not None:
                clear_layout(item.layout())


class BaseWidget:
    """
    A base class for creating a widget with blur effect and an info widget.

    To change the info message, set new text to the `info_label`.
    To add a new widget, add it to the `info_widget`.
    """

    def __init__(self, widget: QWidget, widget_parent: QWidget):
        self._widget = widget
        self._widget_parent = widget_parent
        self._blur_effect: QGraphicsBlurEffect

        # Create an info widget that will contain the info label
        self.info_widget = QWidget(self._widget_parent)

        # Use QGridLayout for grid layout
        self.layout = QVBoxLayout(self.info_widget)
        self.info_label = QLabel("", self._widget_parent)
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("font-size: 24px; color: white;")

        # Add info_label to the grid layout at row 0, column 0
        self.layout.addWidget(self.info_label)

        self.info_widget.setGeometry(self._widget_parent.geometry())
        self.info_widget.hide()

    def block_ui(self):
        """Disable and blur widget."""
        self._widget.setEnabled(False)
        self._blur_window()
        self.info_widget.show()

    def enable_ui(self):
        """Enable widget and disable blur.."""
        self._widget.setEnabled(True)
        self._remove_blur()
        self.info_widget.hide()

    def _blur_window(self):
        """Apply a blur effect to the login window."""
        self._blur_effect = QGraphicsBlurEffect()
        self._blur_effect.setBlurRadius(15)
        self._widget.setGraphicsEffect(self._blur_effect)

    def _remove_blur(self):
        """Remove the blur effect from the login window."""
        self._widget.setGraphicsEffect(None)


class ServerWidget(QPushButton):
    """
    Template widget for server data: Image, server information, play button.
    """

    # pylint: disable=R0913, R0917
    def __init__(
        self,
        title: str,
        subtitle: str,
        cur_online: int = 0,
        max_online: int = 0,
        image_path: str = ":/data/background/server-icon.png",
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)

        # Set widget size
        self.setFixedSize(200, 300)
        self.setStyleSheet(ServerWidgetCSS.main_widget)

        # Main layout of the widget
        layout = QVBoxLayout(self)

        # Add an image
        self.image_label = QLabel(self)
        pixmap = QPixmap(image_path)
        self.image_label.setPixmap(pixmap.scaled(180, 180, Qt.KeepAspectRatio))
        layout.addWidget(self.image_label)

        # Set server title
        self.title_label = QLabel(title, self)
        self.title_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setBold(True)
        self.title_label.setFont(font)
        layout.addWidget(self.title_label)

        # Set server subtitle
        self.subtitle_label = QLabel(subtitle, self)
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.subtitle_label)

        # Progress bar for current server online status
        self.progress_bar = QProgressBar(self)

        self.progress_bar.setMinimum(0)
        if cur_online and max_online:
            self.progress_bar.setMaximum(max_online)
            self.progress_bar.setValue(cur_online)
            self.progress_bar.setFormat(f"{cur_online} В ИГРЕ")
            self.progress_bar.setStyleSheet(
                ServerWidgetCSS.progress_bar_online
            )
        else:
            self.progress_bar.setMaximum(1)
            self.progress_bar.setValue(1)
            self.progress_bar.setFormat("СЕРВЕР ОФЛАЙН")
            self.progress_bar.setStyleSheet(
                ServerWidgetCSS.progress_bar_offline
            )

        # Setting alignment to centre
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        self.push_button = QPushButton("ИГРАТЬ", self)
        self.push_button.setStyleSheet(ServerWidgetCSS.play_button)
        layout.addWidget(self.push_button)
        layout.addStretch()
