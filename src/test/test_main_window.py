"""Tests for main qt Window class."""

from unittest.mock import MagicMock

# pylint: disable=W0613,W0212, E0401
import minecraft_launcher_lib as mine_lib
import pytest
from src.launcher.main_window import Window


@pytest.fixture
def mock_window(
    mocker,
    qtbot,
    tmpdir,
):
    """
    Create an window instance without notification message boxes.
    Set minecraft root dir to the temp dir.
    """
    # fmt: off
    with mocker.patch.object(
        mine_lib.utils, "get_minecraft_directory", return_value=str(tmpdir)
    ):
        window = Window()
        qtbot.addWidget(window)
        yield window
    # fmt: on


def test_page_switching_after_success_authentication(
    mock_window, mocker, qtbot
):
    """Test if page switches to success after authentication."""
    window = mock_window
    window._config_installer_thread._config_manager = MagicMock()
    window._config_installer_complete()

    assert (
        window._ui_instance.stackedWidget.currentWidget()
        == window._ui_instance.choose_server_page
    )
