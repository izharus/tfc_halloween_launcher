"""Utility module for creating and managing UI elements."""

import webbrowser
from typing import Optional

from qtpy.QtCore import Qt, QUrl
from qtpy.QtGui import QDesktopServices, QFont, QPixmap
from qtpy.QtWidgets import (
    QDialog,
    QGraphicsBlurEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLayout,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..launcher_configs import LauncherConfig
from .styles import (
    CUSTOM_MESSAGE_BOX_STYLE,
    INSTALL_PROGRESS_BAR,
    MainButtonData,
    ServerWidgetCSS,
)


class MessageBox(QDialog):
    """
    A custom message box that displays a message
    and allows the user to close it.

    Attributes:
        button_layout (QHBoxLayout): The layout for adding new custom buttons.
    """

    def __init__(self, parent: QWidget):
        """Initializes the CustomMessageBox with a translucent background
        and a close button.
        """
        super().__init__(parent)
        self.setWindowFlags(
            Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Implement the custom widget to avoid visual bugs with border-radius
        container_widget = QWidget()

        self._widget = container_widget
        # User copy-able textEdit.
        self._text_edit = QTextEdit(self._widget)
        self._text_edit.setText("Критическая ошибка!")
        self._text_edit.setReadOnly(True)
        self._text_edit.setFrameStyle(QTextEdit.NoFrame)
        self._text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._text_edit.setAcceptRichText(False)
        self._text_edit.setFixedSize(300, 150)

        # Button for closing this widget
        self._close_button = QPushButton("закрыть")
        self._close_button.clicked.connect(self.accept)

        main_button_layout = QHBoxLayout()
        main_button_layout.addStretch()

        # Put button into the middle of widget
        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(50)
        self.button_layout.addWidget(self._close_button)

        main_button_layout.addLayout(self.button_layout)
        main_button_layout.addStretch()

        # Main widget's layout
        layout = QVBoxLayout()
        layout.addWidget(self._text_edit)
        layout.addLayout(main_button_layout)

        container_widget.setLayout(layout)

        self._main_layout = QVBoxLayout(self)
        self._main_layout.addWidget(container_widget)

        self.setStyleSheet(CUSTOM_MESSAGE_BOX_STYLE)

        self._widget = container_widget

    @staticmethod
    def _format_title(title: str) -> str:
        return "<h2 style='text-align: center;'>" f"{title}</h2>\n"

    @staticmethod
    def _format_msg(msg: str) -> str:
        return "<p style='text-align: center;'>" f"{msg}</p>\n"

    def show_message(
        self, title: str, msg: str = "", close_button_text: str = "закрыть"
    ) -> None:
        """Show message box."""
        self._close_button.setText(close_button_text)
        self._text_edit.setText(
            self._format_title(title) + self._format_msg(msg)
        )
        self.exec()


class LogMessageBox(MessageBox):
    """
    A custom message box that displays a message, and a log button
    for opening the log dir.
    """

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._log_button = QPushButton(self._widget)
        self._log_button.setText("папка с логами")
        self.button_layout.addWidget(self._log_button)
        self._log_button.clicked.connect(
            lambda: webbrowser.open(str(LauncherConfig().LOGGING_DIR))
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

    To change the info message, set new text to the `_info_label`.
    To add a new widget, add it to the `_info_widget`.
    """

    def __init__(self, widget: QWidget, parent_widget: QWidget):
        self._widget = widget
        self._parent_widget = parent_widget
        self._blur_effect: QGraphicsBlurEffect

        # Create a label to display information
        self._info_label = QLabel("", self._parent_widget)
        self._info_label.setAlignment(Qt.AlignCenter)
        self._info_label.setStyleSheet("font-size: 24px; color: white;")

        # Create a stylish progress bar
        self._progress_bar = InstallProgressBar(self._parent_widget)
        self._progress_bar.setFixedSize(400, 50)

        # Main widget for all info widgets
        self._info_widget = QWidget(self._parent_widget)
        # Set the geometry of the info widget
        self._info_widget.setGeometry(self._parent_widget.geometry())

        internal_widget = QWidget(self._info_widget)

        # Use QVBoxLayout for vertical stacking of elements
        vertical_layout = QVBoxLayout(self._info_widget)
        vertical_layout.addWidget(self._info_label)
        vertical_layout.addWidget(self._progress_bar)
        internal_widget.setLayout(vertical_layout)

        # Create a QGridLayout for arranging elements
        grid_layout = QGridLayout(self._info_widget)

        # Add a spacer at the top
        grid_layout.addItem(
            QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding),
            0,
            1,
        )

        # Add a spacer on the left
        grid_layout.addItem(
            QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum),
            1,
            0,
        )

        # Add the internal widget (label and progress bar) to the center
        grid_layout.addWidget(internal_widget, 1, 1)

        # Add a spacer on the right
        grid_layout.addItem(
            QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum),
            1,
            2,
        )

        # Add a spacer at the bottom
        grid_layout.addItem(
            QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding),
            2,
            1,
        )

        # Set the layout for the info widget
        self._info_widget.setLayout(grid_layout)

        # Hide the info widget initially
        self._info_widget.hide()
        self._info_label.hide()
        self._progress_bar.hide()

    def disable_ui(self, show_text: bool = True, show_progress: bool = False):
        """Disable and blur widget."""
        self._widget.setEnabled(False)
        self._blur_window()
        self._info_widget.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._info_widget.show()

        self.show_widget(self._info_label, show_text)
        self.show_widget(self._progress_bar, show_progress)

    def enable_ui(self):
        """Enable widget and disable blur.."""
        self._widget.setEnabled(True)
        self._remove_blur()
        self._info_widget.hide()

    @property
    def info_label(self) -> QLabel:
        """Return info label for signals."""
        return self._info_label

    @property
    def progress_bar(self) -> QProgressBar:
        """Return progress bar for signals."""
        return self._progress_bar

    @staticmethod
    def show_widget(target_widget: QWidget, should_show: bool) -> None:
        """
        Show or hide a specified widget.

        Args:
            target_widget (QWidget): The widget to show or hide.
            should_show (bool): A flag indicating whether to show the widget
                (`True`) or hide it (`False`).

        Returns:
            None
        """
        (target_widget.show if should_show else target_widget.hide)()

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
        self._progress_bar = QProgressBar(self)

        self._progress_bar.setMinimum(0)
        if cur_online and max_online:
            self._progress_bar.setMaximum(max_online)
            self._progress_bar.setValue(cur_online)
            self._progress_bar.setFormat(f"{cur_online} В ИГРЕ")
            self._progress_bar.setStyleSheet(
                ServerWidgetCSS.progress_bar_online
            )
        else:
            self._progress_bar.setMaximum(1)
            self._progress_bar.setValue(1)
            self._progress_bar.setFormat("СЕРВЕР ОФЛАЙН")
            self._progress_bar.setStyleSheet(
                ServerWidgetCSS.progress_bar_offline
            )

        # Setting alignment to centre
        self._progress_bar.setAlignment(Qt.AlignCenter)
        self._progress_bar.setTextVisible(True)
        layout.addWidget(self._progress_bar)

        self.push_button = QPushButton("ИГРАТЬ", self)
        self.push_button.setStyleSheet(ServerWidgetCSS.play_button)
        layout.addWidget(self.push_button)
        layout.addStretch()


class InstallProgressBar(QProgressBar):
    """A progress bar for installation process."""

    def __init__(self, parent):
        super().__init__(parent)

        # Создание прогресс-бара
        self.setMinimum(0)
        self.setMaximum(100)
        self.setValue(0)
        self.setTextVisible(True)
        self.setFormat("%p%")

        # Применение стилей
        self.setStyleSheet(INSTALL_PROGRESS_BAR)
