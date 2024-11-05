"""Tests for main qt Window class."""

from unittest.mock import MagicMock

# pylint: disable=W0613,W0212, E0401
from src.launcher.main_window import Window


def test_page_switching_after_success_authentication(
    main_window: Window, mocker, qtbot
):
    """Test if page switches to success after authentication."""
    main_window._config_installer_thread._config_manager = MagicMock()

    main_window._login_widget._auth_data = MagicMock()
    main_window._login_widget._auth_data.username = "mock_username"

    main_window._config_installer_complete()

    assert main_window._ui_instance.label_player_name.text() == "mock_username"
    assert (
        main_window._ui_instance.stackedWidget.currentWidget()
        == main_window._ui_instance.choose_server_page
    )
