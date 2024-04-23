"""Tests for main qt Window class."""
from unittest.mock import MagicMock

import minecraft_launcher_lib as mine_lib
import pytest
from PyQt6 import QtCore
from src.launcher.design.styles import MainButtonData
from src.launcher.design.utillity import MessageBoxManager
from src.launcher.launcher_configs import (
    OFFLINE_MAP_JSON,
    ConfigLoader,
    LauncherConfig,
)
from src.launcher.main_window import Window
from src.launcher.utillity.custom_exceptions import (
    ConfigProcessingError,
    RequestDownloadError,
)

# pylint: disable=W0613,W0212


SERVER_NAME_1 = "server name 1"
SERVER_NAME_2 = "server name 2"


@pytest.fixture
def mock_config_data():
    """Mock a config data."""
    return {
        SERVER_NAME_1: {"config": {"config_name": "config_name_1"}},
        SERVER_NAME_2: {"config": {"config_name": "config_name_2"}},
    }


@pytest.fixture
def mock_download_from_url(mocker, mock_config_data):
    """Mock ConfigLoader.download_from_url method."""
    with mocker.patch.object(
        ConfigLoader,
        "download_from_url",
        return_value=ConfigLoader(mock_config_data, LauncherConfig()),
    ):
        yield


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
    with mocker.patch.object(
        MessageBoxManager,
        "create_msg_box",
        MagicMock(),
    ), mocker.patch.object(
        MessageBoxManager, "warn", side_effect=MagicMock()
    ), mocker.patch.object(
        MessageBoxManager,
        "info",
        side_effect=MagicMock(),
    ), mocker.patch.object(
        mine_lib.utils, "get_minecraft_directory", return_value=str(tmpdir)
    ):
        window = Window()
        qtbot.addWidget(window)
        yield window


def test_get_config_loader_success(
    mock_download_from_url, mock_config_data, mock_window
):
    """TODO: Docstring"""
    window = mock_window

    assert window.config_loader._config_data == mock_config_data


def test_get_config_loader_download_failed(
    mock_window,
    mocker,
):
    """Test that the config loader handles download failure gracefully."""
    window = mock_window
    with mocker.patch.object(
        ConfigLoader,
        "download_from_url",
        side_effect=RequestDownloadError,
    ):
        window.config_loader = window.get_config_loader()

    assert window.config_loader._config_data == OFFLINE_MAP_JSON


def test_get_config_loader_config_error(
    mock_window,
    mocker,
):
    """
    Test that the config loader handles exception
    ConfigProcessingError gracefully.
    """
    window = mock_window
    with mocker.patch.object(
        ConfigLoader,
        "download_from_url",
        side_effect=ConfigProcessingError,
    ):
        window.config_loader = window.get_config_loader()
    assert window.config_loader._config_data == OFFLINE_MAP_JSON
    window.msg_box.warn.assert_called_once()


def test_update_server_type_combobox_with_config(
    mock_config_data, mock_window
):
    """
    Test _update_server_type_combobox with valid config data.
    """
    window = mock_window

    config_loader = ConfigLoader(mock_config_data, LauncherConfig())
    window._update_server_type_combobox(config_loader)

    config_names = config_loader.config_list

    combo_box_items = [
        window._ui_instance.comboBox_server_type.itemText(i)
        for i in range(window._ui_instance.comboBox_server_type.count())
    ]

    assert set(config_names) == set(combo_box_items)


def test_update_server_type_combobox_with_empty_config(mock_window):
    """
    Test _update_server_type_combobox with empty config data.
    """

    window = mock_window

    window._update_server_type_combobox(ConfigLoader({}, LauncherConfig))

    assert window._ui_instance.comboBox_server_type.count() == 0


def test_update_server_type_combobox_with_different_config(
    mock_config_data, mock_window
):
    """
    Test _update_server_type_combobox with different config data.
    """

    window = mock_window
    config_loader = ConfigLoader(mock_config_data, LauncherConfig())
    window._update_server_type_combobox(config_loader)

    initial_combo_box_items = [
        window._ui_instance.comboBox_server_type.itemText(i)
        for i in range(window._ui_instance.comboBox_server_type.count())
    ]

    new_config_data = {"config3": {"config": {"config_name": "Config 3"}}}
    new_config_loader = ConfigLoader(new_config_data, LauncherConfig())
    window._update_server_type_combobox(new_config_loader)

    new_combo_box_items = [
        window._ui_instance.comboBox_server_type.itemText(i)
        for i in range(window._ui_instance.comboBox_server_type.count())
    ]

    assert set(new_combo_box_items) != set(initial_combo_box_items)


def test_update_config_with_valid_config(
    mock_download_from_url,
    mock_window,
    mock_config_data,
):
    """
    Test update_config method with valid configuration data.
    """
    window = mock_window

    window._ui_instance.comboBox_server_type.setCurrentText(SERVER_NAME_2)
    status = window.update_config()

    assert status
    assert window.config.map_json_data == mock_config_data[SERVER_NAME_2]


def test_update_config_success(
    mock_download_from_url,
    mock_window,
):
    """
    Test update_config method with successful configuration update.
    """
    window = mock_window

    status = window.update_config()

    assert status is True
    window.msg_box.create_msg_box.assert_not_called()


def test_update_config_outdate_config(
    mock_download_from_url, mock_window, mocker
):
    """
    Test update_config method when the configuration is outdated.
    """
    window = mock_window
    new_config_data = {"config3": {"config": {"config_name": "Config 3"}}}
    with mocker.patch.object(
        ConfigLoader,
        "download_from_url",
        return_value=ConfigLoader(new_config_data, LauncherConfig()),
    ):
        status = window.update_config()

    assert status is False
    window.msg_box.warn.assert_called_once()


def test_simulate_config_update(
    mock_download_from_url,
    mock_window,
    mock_config_data,
    mocker,
    qtbot,
):
    """
    Test situation when configs list changes while app is working.
    """
    server_name_3 = "server name 3"
    mock_updated_config_data = mock_config_data | {
        server_name_3: {"config": {"config_name": "config_name_3"}}
    }
    window = mock_window
    with mocker.patch.object(
        ConfigLoader,
        "download_from_url",
        return_value=ConfigLoader(mock_updated_config_data, LauncherConfig()),
    ):
        qtbot.mouseClick(
            window._ui_instance.pushButton_install_and_launch,
            QtCore.Qt.MouseButton.LeftButton,
        )

    assert set(window.config_loader.config_list) == set(
        mock_updated_config_data.keys()
    ), "A new field should be added to the config."
    assert (
        window._ui_instance.comboBox_server_type.currentText() == SERVER_NAME_1
    ), "Current config should not be changed"
    # Warning about changed config should be called once
    window.msg_box.warn.assert_called_once()


def test_simulate_config_changes(
    mock_download_from_url,
    mock_window,
    mock_config_data,
    qtbot,
):
    """
    Simulate changing config in combobox.
    """
    window = mock_window
    assert window.config.map_json_data == mock_config_data[SERVER_NAME_1]
    qtbot.keyClicks(window._ui_instance.comboBox_server_type, SERVER_NAME_2)
    assert window.config.map_json_data == mock_config_data[SERVER_NAME_2]
