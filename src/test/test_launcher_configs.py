"""Tests for src/launcher_config.py"""

# pylint:disable = E0401
# pylint: disable=W0212
import json
import os
import shelve
from unittest.mock import MagicMock

import minecraft_launcher_lib as mine_lib
import pytest
from src.launcher.launcher_configs import (
    ConfigGetter,
    ConfigLoader,
    LauncherConfig,
    ServerConfig,
)
from src.launcher.utility.custom_exceptions import (
    ConfigDownloadError,
    ConfigProcessingError,
    FiletDownloadError,
)

# from src.launcher.utility.file_downloader import FileDownloader
from src.test.conftest import (
    CONFIG_NAME_1,
    CONFIG_NAME_2,
    DISPLAY_NAME_1,
    DISPLAY_NAME_2,
)


@pytest.fixture(autouse=True)
def mock_window(
    mocker,
    tmpdir,
):
    """
    Create an window instance without notification message boxes.
    Set minecraft root dir to the temp dir.
    """
    with mocker.patch.object(
        mine_lib.utils, "get_minecraft_directory", return_value=str(tmpdir)
    ):
        yield


class TestConfigLoader:
    """Unit tests for ConfigLoader."""

    def test_get_from_yos_success(
        self,
        mocker,
        mock_config_data,
    ):
        """Test get_from_yos method with correct json data."""

        mock_config = LauncherConfig()

        mock_file_downloader = MagicMock()
        config_loader = ConfigLoader(mock_file_downloader, mock_config)

        mock_download_bytes = MagicMock(
            return_value=json.dumps(mock_config_data)
        )

        with mocker.patch.object(
            mock_file_downloader, "download_bytes", mock_download_bytes
        ):
            config = config_loader.get_from_yos()

        assert config == mock_config_data
        mock_download_bytes.assert_called_once_with(
            mock_config.MAP_JSON_YOS_OBJ_KEY,
        )

    def test_get_from_yos_request_error(self, mocker):
        """Test get_from_yos method when get_object fails."""
        mock_config = LauncherConfig()
        mock_file_downloader = MagicMock()
        mock_file_downloader.download_bytes = MagicMock()
        config_loader = ConfigLoader(mock_file_downloader, mock_config)

        with pytest.raises(ConfigDownloadError):
            mocker.patch.object(
                mock_file_downloader,
                "download_bytes",
                side_effect=FiletDownloadError,
            )
            config_loader.get_from_yos()

    def test__create_model_from_bytes_valid_json_data(self):
        """Test _create_model_from_bytes method with valid JSON data."""
        valid_json_data = b'{"key": "value"}'
        expected_result = {"key": "value"}

        result = ConfigLoader._create_model_from_bytes(valid_json_data)

        assert result == expected_result

    def test__create_model_from_bytes_invalid_json_data(self):
        """Test _create_model_from_bytes method when json data is invalid."""
        with pytest.raises(ConfigProcessingError):
            ConfigLoader._create_model_from_bytes("invalid_data")


class TestConfigGetter:
    """Unit tests for ConfigGetter"""

    def test_config_list(self, mock_config_data):
        """
        Test config_list method to ensure it returns a list of supported
        configuration names.
        """
        server_config = ConfigGetter(mock_config_data, LauncherConfig())
        assert server_config.config_list == [DISPLAY_NAME_1, DISPLAY_NAME_2]

    def test_set_active_existing_config(self, mock_config_data):
        """
        Test set_active method for an existing config name.
        """
        mock_launcher_config = LauncherConfig()
        server_config = ConfigGetter(
            mock_config_data,
            mock_launcher_config,
        )
        assert server_config._active_config_display_name == DISPLAY_NAME_1
        assert server_config.active == ServerConfig(
            CONFIG_NAME_1,
            mock_config_data["modpacks"][CONFIG_NAME_1],
            mock_launcher_config,
        )

        assert server_config.set_active(DISPLAY_NAME_2) is True
        assert server_config.active == ServerConfig(
            CONFIG_NAME_2,
            mock_config_data["modpacks"][CONFIG_NAME_2],
            mock_launcher_config,
        )

    def test_set_active_non_existing_config(self, mock_config_data):
        """
        Test set_active method for a non-existing config name.
        """
        mock_launcher_config = LauncherConfig()
        server_config = ConfigGetter(
            mock_config_data,
            mock_launcher_config,
        )
        assert server_config.set_active("NonExistingConfig") is False


class TestServerConfig:
    """Unit tests for ServerConfig."""

    def test_is_minecraft_installed_set_true(self, tmp_path, mock_config_data):
        """Test setting Minecraft installed flag to True."""
        server_config = ConfigGetter(
            mock_config_data,
            LauncherConfig(),
        ).active
        server_config._launcher_config._launcher_data_path = os.path.join(
            tmp_path, "launcher_data.bin"
        )

        server_config.is_minecraft_installed = True
        field = f"{server_config.internal_name}_is_installed"
        assert server_config._launcher_config.launcher_data[field] is True

    def test_sis_minecraft_installed_set_true_and_false(
        self, tmp_path, mock_config_data
    ):
        """Test setting Minecraft installed flag to True and False."""
        server_config = ConfigGetter(
            mock_config_data,
            LauncherConfig(),
        ).active
        server_config._launcher_config._launcher_data_path = os.path.join(
            tmp_path, "launcher_data.bin"
        )

        server_config.is_minecraft_installed = True
        server_config.is_minecraft_installed = False
        field = f"{server_config.internal_name}_is_installed"
        assert server_config._launcher_config.launcher_data[field] is False

    def test_is_minecraft_installed(self, tmp_path, mock_config_data):
        """
        Test the is_minecraft_installed method of MinecraftLauncherConfig.
        """
        server_config = ConfigGetter(
            mock_config_data,
            LauncherConfig(),
        ).active
        server_config._launcher_config._launcher_data_path = os.path.join(
            tmp_path, "launcher_data.bin"
        )
        assert not server_config.is_minecraft_installed

        # Set the flag to True and check again
        server_config.is_minecraft_installed = True
        assert server_config.is_minecraft_installed

    def test__update_launcher_data(self, tmp_path, mock_config_data):
        """
        Test the _update_launcher_data method of MinecraftLauncherConfig.
        """
        server_config = ConfigGetter(
            mock_config_data,
            LauncherConfig(),
        ).active
        server_config._launcher_config._launcher_data_path = os.path.join(
            tmp_path, "launcher_data.bin"
        )
        data_to_save = {"stored_data_key": "stored_data_value"}
        server_config._launcher_config._launcher_data_path = os.path.join(
            tmp_path, "launcher_data.bin"
        )
        # Create a sample stored data
        server_config._launcher_config._launcher_data = data_to_save

        # Update stored data in the file
        server_config._launcher_config._update_launcher_data()

        with shelve.open(
            server_config._launcher_config._launcher_data_path
        ) as data:
            save_data = dict(data)

        # Check if the stored data matches the original data
        assert save_data == data_to_save
