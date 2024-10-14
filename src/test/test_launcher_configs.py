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
    LauncherConfig,
    ServerConfig,
    ServerConfigManager,
)
from src.launcher.utility.custom_exceptions import (
    ConfigDownloadError,
    ConfigProcessingError,
    FiletDownloadError,
)
from src.launcher.utility.pydantic_models import MapJson


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


class TestServerConfigManager:
    """Tests for ServerConfigManager."""

    def test_update_config_success(
        self,
        mocker,
        mock_config_data,
    ):
        """Test update_config method with correct json data."""
        object_key = "mock_object_key"
        mock_file_downloader = MagicMock()
        mock_download_bytes = MagicMock(
            return_value=json.dumps(mock_config_data)
        )
        with mocker.patch.object(
            mock_file_downloader, "download_bytes", mock_download_bytes
        ):
            config_manager = ServerConfigManager(
                mock_file_downloader,
                object_key,
            )
        assert config_manager.map_json == MapJson(**mock_config_data)
        mock_download_bytes.assert_called_once_with(
            object_key,
        )

    def test_update_config_download_error(
        self,
        mocker,
    ):
        """Test update_config method when download failed."""
        object_key = "mock_object_key"
        mock_file_downloader = MagicMock()
        with mocker.patch.object(
            mock_file_downloader,
            "download_bytes",
            side_effect=FiletDownloadError,
        ):
            with pytest.raises(ConfigDownloadError):
                ServerConfigManager(
                    mock_file_downloader,
                    object_key,
                )

    def test_update_config_with_invalid_json_data(
        self,
        mocker,
    ):
        """Test update_config method with valid JSON data."""
        object_key = "mock_object_key"
        mock_file_downloader = MagicMock()
        with mocker.patch.object(
            mock_file_downloader,
            "download_bytes",
            return_value=b'{"some_key": 1}',
        ):
            with pytest.raises(ConfigProcessingError):
                ServerConfigManager(
                    mock_file_downloader,
                    object_key,
                )

    def test_update_config_with_invalid_json_data_type(
        self,
        mocker,
    ):
        """Test update_config method with valid JSON data."""
        object_key = "mock_object_key"
        mock_file_downloader = MagicMock()
        with mocker.patch.object(
            mock_file_downloader,
            "download_bytes",
            return_value="1",
        ):
            with pytest.raises(ConfigProcessingError):
                ServerConfigManager(
                    mock_file_downloader,
                    object_key,
                )

    def test_update_config_with_incorrect_json(
        self,
        mocker,
    ):
        """Test update_config method with valid JSON data."""
        object_key = "mock_object_key"
        mock_file_downloader = MagicMock()
        with mocker.patch.object(
            mock_file_downloader,
            "download_bytes",
            return_value="{{{{1",
        ):
            with pytest.raises(ConfigProcessingError):
                ServerConfigManager(
                    mock_file_downloader,
                    object_key,
                )


class TestServerConfig:
    """Unit tests for ServerConfig."""

    def test_is_minecraft_installed_set_true(
        self, tmp_path, mock_modpack_data
    ):
        """Test setting Minecraft installed flag to True."""
        server_config = ServerConfig(
            "name",
            mock_modpack_data,
            LauncherConfig(),
        )
        server_config._launcher_config._launcher_data_path = os.path.join(
            tmp_path, "launcher_data.bin"
        )

        server_config.is_minecraft_installed = True
        field = f"{server_config.internal_name}_is_installed"
        assert server_config._launcher_config.launcher_data[field] is True

    def test_sis_minecraft_installed_set_true_and_false(
        self, tmp_path, mock_modpack_data
    ):
        """Test setting Minecraft installed flag to True and False."""
        server_config = ServerConfig(
            "name",
            mock_modpack_data,
            LauncherConfig(),
        )
        server_config._launcher_config._launcher_data_path = os.path.join(
            tmp_path, "launcher_data.bin"
        )

        server_config.is_minecraft_installed = True
        server_config.is_minecraft_installed = False
        field = f"{server_config.internal_name}_is_installed"
        assert server_config._launcher_config.launcher_data[field] is False

    def test_is_minecraft_installed(self, tmp_path, mock_modpack_data):
        """
        Test the is_minecraft_installed method of MinecraftLauncherConfig.
        """
        server_config = ServerConfig(
            "name",
            mock_modpack_data,
            LauncherConfig(),
        )
        server_config._launcher_config._launcher_data_path = os.path.join(
            tmp_path, "launcher_data.bin"
        )
        assert not server_config.is_minecraft_installed

        # Set the flag to True and check again
        server_config.is_minecraft_installed = True
        assert server_config.is_minecraft_installed

    def test__update_launcher_data(self, tmp_path, mock_modpack_data):
        """
        Test the _update_launcher_data method of MinecraftLauncherConfig.
        """
        server_config = ServerConfig(
            "name",
            mock_modpack_data,
            LauncherConfig(),
        )
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
