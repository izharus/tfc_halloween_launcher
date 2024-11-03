"""Tests for src.launcher.server_widget.py"""

# pylint: disable=R0903,W0621,W0212,W0613,E0401,R0904

from unittest.mock import MagicMock

from pytestqt.qtbot import QtBot
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QPushButton
from src.launcher.main_window import Window

CONFIG_NAME_1 = "TestModpack1"
CONFIG_NAME_2 = "TestModpack2"


class TestServerWidgetPage:
    """Test suite for the ServerWidgetPage class."""

    def test_initialization(self, auth_window: Window):
        """Tests the initialization of ServerWidgetPage."""
        assert auth_window._server_page._config is not None
        assert auth_window._server_page._ui is not None
        assert auth_window._server_page._server_widget is None
        assert auth_window._server_page._last_layout_pos == 0

    def test_page_switching(self, auth_window: Window, qtbot: QtBot):
        """Tests switching between pages in the stacked widget."""
        modpack_button = auth_window.findChild(QPushButton, "TestModpack1")
        qtbot.mouseClick(modpack_button, Qt.LeftButton)
        assert (
            auth_window._ui_instance.stackedWidget.currentWidget()
            == auth_window._ui_instance.server_settings_page
        )
        qtbot.mouseClick(
            auth_window._ui_instance.pushButton_back_from_server_settings,
            Qt.LeftButton,
        )

        assert (
            auth_window._ui_instance.stackedWidget.currentWidget()
            == auth_window._ui_instance.choose_server_page
        )

    def test_switch_to_server_page_updates_widget(self, auth_window: Window):
        """
        Tests that switching to a server page updates
        the widget and description.
        """
        # Arrange
        server_config = auth_window.config_manager.get_modpack(CONFIG_NAME_1)
        server_widget = auth_window._choose_server._buttons[0]
        expected_pos = auth_window._ui_instance.horizontalLayout_2.indexOf(
            server_widget
        )
        # Act
        auth_window._server_page.switch_to_server_page(
            CONFIG_NAME_1, server_widget
        )

        # Assert
        assert (
            auth_window._ui_instance.stackedWidget.currentWidget()
            == auth_window._ui_instance.server_settings_page
        )
        assert (
            auth_window._server_page._ui.label_server_description.text()
            == server_config.server_config.description
        )
        assert auth_window._server_page._server_widget == server_widget
        assert auth_window._server_page._last_layout_pos == expected_pos

    def test_switch_to_same_server_widget_does_not_update(
        self, auth_window: Window
    ):
        """
        Tests that switching to the same server widget
        does not trigger updates.
        """
        # Arrange
        server_widget = auth_window._choose_server._buttons[0]
        auth_window._server_page.switch_to_server_page(
            CONFIG_NAME_1, server_widget
        )
        auth_window._server_page._config.get_modpack = MagicMock()
        # Act

        auth_window._server_page.switch_to_server_page(
            CONFIG_NAME_1, server_widget
        )

        # Assert
        assert (
            auth_window._ui_instance.stackedWidget.currentWidget()
            == auth_window._ui_instance.server_settings_page
        )
        auth_window._server_page._config.get_modpack.assert_not_called()

    def test_back_arrow_functionality(self, auth_window: Window, qtbot: QtBot):
        """
        Tests the functionality of the back arrow in the server settings.
        """
        # Arrange
        server_widget = auth_window._choose_server._buttons[1]
        expected_pos = auth_window._ui_instance.horizontalLayout_2.indexOf(
            server_widget
        )
        auth_window._server_page.switch_to_server_page(
            CONFIG_NAME_2, server_widget
        )

        # Act
        qtbot.mouseClick(
            auth_window._ui_instance.pushButton_back_from_server_settings,
            Qt.LeftButton,
        )

        # Assert
        assert auth_window._server_page._server_widget is None
        assert (
            auth_window._ui_instance.stackedWidget.currentWidget()
            == auth_window._ui_instance.choose_server_page
        )
        assert (
            auth_window._ui_instance.horizontalLayout_2.indexOf(server_widget)
            == expected_pos
        )
