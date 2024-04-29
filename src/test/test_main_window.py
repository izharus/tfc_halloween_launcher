"""Tests for main qt Window class."""
from unittest.mock import MagicMock

# pylint: disable=W0613,W0212, E0401
import minecraft_launcher_lib as mine_lib
import pytest
from src.launcher.design.styles import MainButtonData
from src.launcher.design.utility import MessageBoxManager
from src.launcher.launcher_configs import ConfigLoader
from src.launcher.main_window import Window
from src.launcher.utility.pydantic_models import ServerConfig
from src.test.conftest import (
    CONFIG_NAME_1,
    CONFIG_NAME_2,
    DISPLAY_NAME_1,
    DISPLAY_NAME_2,
    MODPACK_DISPLAY_NAME,
)


@pytest.fixture
def mock_download_from_url(mocker, mock_config_data):
    """Mock ConfigLoader.download_from_url method."""
    with mocker.patch.object(
        ConfigLoader,
        "get_from_url",
        return_value=mock_config_data,
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
    """Test that the configuration loader is successfully initialized."""
    window = mock_window
    assert window.config_loader.get_from_url() == mock_config_data


def test_update_server_type_combobox_with_updated_config_data(
    mock_download_from_url,
    mock_window,
    mock_config_data,
    mock_modpack_data,
    mocker,
):
    """
    Test _update_server_type_combobox with new config data.
    """
    window = mock_window

    config_name_3 = "config3"
    mock_config_data["modpacks"][config_name_3] = mock_modpack_data
    with mocker.patch.object(
        ConfigLoader,
        "get_from_url",
        return_value=mock_config_data,
    ):
        window.update_config()
        # Call the method to be tested
        window._update_server_type_combobox()

        # Check if the combo box items match the expected config names
        combo_box_items = [
            window._ui_instance.comboBox_server_type.itemText(i)
            for i in range(window._ui_instance.comboBox_server_type.count())
        ]
        assert set(combo_box_items) == {
            DISPLAY_NAME_1,
            DISPLAY_NAME_2,
            MODPACK_DISPLAY_NAME,
        }
        # First config should be installed, if all old configs were deleted
        cur_name = window._ui_instance.comboBox_server_type.currentText()
        assert cur_name == DISPLAY_NAME_1


def test_update_server_type_combobox_with_new_config_data(
    mock_download_from_url,
    mock_window,
    mock_modpack_data,
    mocker,
):
    """
    Test _update_server_type_combobox with updated config data.
    """
    window = mock_window

    config_name_3 = "config3"
    mock_config_data = {"modpacks": {config_name_3: mock_modpack_data}}
    with mocker.patch.object(
        ConfigLoader,
        "get_from_url",
        return_value=mock_config_data,
    ):
        window.update_config()
        # Call the method to be tested
        window._update_server_type_combobox()

        # Check if the combo box items match the expected config names
        combo_box_items = [
            window._ui_instance.comboBox_server_type.itemText(i)
            for i in range(window._ui_instance.comboBox_server_type.count())
        ]
        assert set(combo_box_items) == {MODPACK_DISPLAY_NAME}
        # First config should be installed, if all old configs were deleted
        cur_name = window._ui_instance.comboBox_server_type.currentText()
        assert cur_name == MODPACK_DISPLAY_NAME


def test_update_config_with_valid_config(
    mock_download_from_url,
    mock_window,
    mock_config_data,
):
    """
    Test update_config method with valid configuration data.
    """
    window = mock_window

    window._ui_instance.comboBox_server_type.setCurrentText(DISPLAY_NAME_2)
    # status = window.update_config()

    # assert status
    expected = ServerConfig(
        **mock_config_data["modpacks"][CONFIG_NAME_2]["server_config"]
    )
    current = window.config_getter.active.server_config
    assert expected == current


def test_multiple_updating_different_main_button_text(
    mock_download_from_url, mock_window
):
    """
    Test the behavior of updating the main button text when
    switching server types.
    """
    window: Window = mock_window
    window.show()
    window.config_getter.set_active(DISPLAY_NAME_1)
    window.config_getter.active.is_minecraft_installed = False
    window.config_getter.set_active(DISPLAY_NAME_2)
    window.config_getter.active.is_minecraft_installed = True

    assert (
        window._ui_instance.pushButton_install_and_launch.text()
        == MainButtonData.install_text
    )
    window._ui_instance.comboBox_server_type.setCurrentText(DISPLAY_NAME_2)

    assert (
        window._ui_instance.pushButton_install_and_launch.text()
        == MainButtonData.launch_text
    )
    window._ui_instance.comboBox_server_type.setCurrentText(DISPLAY_NAME_2)
    window._ui_instance.comboBox_server_type.setCurrentText(DISPLAY_NAME_2)
    window._ui_instance.comboBox_server_type.setCurrentText(DISPLAY_NAME_1)
    assert (
        window._ui_instance.pushButton_install_and_launch.text()
        == MainButtonData.install_text
    )
    window._ui_instance.comboBox_server_type.setCurrentText(DISPLAY_NAME_2)
    window._ui_instance.comboBox_server_type.setCurrentText(DISPLAY_NAME_2)
    assert (
        window._ui_instance.pushButton_install_and_launch.text()
        == MainButtonData.launch_text
    )


def test_updating_main_button_text_after_success_installation(
    mock_download_from_url, mock_window
):
    """
    Test the behavior of updating the main button text after
    a successful installation.
    """
    window = mock_window
    window.config_getter.set_active(CONFIG_NAME_1)
    window.config_getter.active.is_minecraft_installed = False

    window._install_thread_finished()

    assert window.config_getter.active.is_minecraft_installed is True
    assert (
        window._ui_instance.pushButton_install_and_launch.text()
        == MainButtonData.launch_text
    )


def test_updating_main_button_text_after_failed_installation(
    mock_download_from_url, mock_window
):
    """
    Test the behavior of updating the main button text after
    a failed installation.
    """
    window = mock_window
    window.config_getter.set_active(CONFIG_NAME_1)
    window.config_getter.active.is_minecraft_installed = False
    window._install_thread.runtime_error = True

    window._install_thread_finished()

    assert window.config_getter.active.is_minecraft_installed is False
    assert (
        window._ui_instance.pushButton_install_and_launch.text()
        == MainButtonData.install_text
    )
