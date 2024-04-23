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
    ConfigLoader,
    LauncherConfig,
    MinecraftLauncherConfig,
)
from src.launcher.utillity.custom_exceptions import (
    ConfigProcessingError,
    RequestDownloadError,
)
from src.launcher.utillity.file_downloader import FileDownloader


@pytest.fixture
def mock_config_data():
    """Mock a config data."""
    return {
        "config1": {"param1": "value1"},
        "config2": {"param2": "value2"},
    }


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

    def test_download_from_url_success(
        self,
        mocker,
        mock_config_data,
    ):
        """Test download_from_url method with correct json data."""
        mock_download_file = MagicMock()
        mock_config = LauncherConfig()

        mock_download_file.return_value = json.dumps(mock_config_data)
        with mocker.patch.object(
            FileDownloader,
            "download_file",
            mock_download_file,
        ):
            loader = ConfigLoader.download_from_url(
                mock_config,
            )
        assert loader.config_list == list(mock_config_data.keys())
        mock_download_file.assert_called_once_with(mock_config.MAP_JSON_URL)

    def test_download_from_url_request_error(self, mocker):
        """Test download_from_url method when download request fails."""
        with pytest.raises(RequestDownloadError):
            mocker.patch.object(
                FileDownloader,
                "download_file",
                side_effect=RequestDownloadError,
            )
            ConfigLoader.download_from_url(LauncherConfig())

    def test_download_from_url_config_invalid_json_data(self, mocker):
        """Test download_from_url method when json data is invalid."""
        with pytest.raises(ConfigProcessingError):
            mocker.patch.object(
                FileDownloader,
                "download_file",
                return_value="invalid_json_data",
            )
            ConfigLoader.download_from_url(LauncherConfig())

    def test_download_from_url_incorrect_json_type(self, mocker):
        """
        Test download_from_url method when json config type is invalid.
        Expected dict data, but received a list.
        """
        with pytest.raises(ConfigProcessingError):
            mocker.patch.object(
                FileDownloader,
                "download_file",
                return_value='["invalid_format", "config_data"]',
            )
            ConfigLoader.download_from_url(LauncherConfig())

    def test_config_list(self, mock_config_data):
        """
        Test config_list method to ensure it returns a list of supported
        configuration names.
        """
        loader = ConfigLoader(mock_config_data, LauncherConfig())
        assert loader.config_list == ["config1", "config2"]

    def test_get_config(self, mock_config_data):
        """
        Test get_config method to ensure it returns the configuration
        data for a specified configuration name.
        """
        loader = ConfigLoader(mock_config_data, LauncherConfig())
        config_name = "config1"
        config = loader.get_config(config_name)
        assert config == MinecraftLauncherConfig(
            mock_config_data[config_name], LauncherConfig()
        )

    def test_get_config_missing_name(self, mock_config_data):
        """
        Test get_config method when the specified configuration name
        is not found in the loaded data.
        """
        loader = ConfigLoader(mock_config_data, LauncherConfig())
        missing_config_name = "missing_config"
        with pytest.raises(ConfigProcessingError):
            loader.get_config(missing_config_name)


class TestMinecraftLauncherConfig:
    """Unit tests for MinecraftLauncherConfig."""

    def test_set_minecraft_installed_set_true(
        self, tmp_path, mock_config_data
    ):
        """Test setting Minecraft installed flag to True."""
        loader = ConfigLoader(mock_config_data, LauncherConfig())
        config = loader.get_config(
            loader.config_list[0],
        )
        config._launcher_config._launcher_data_path = os.path.join(
            tmp_path, "launcher_data.bin"
        )

        config.set_minecraft_installed()
        field = f"{config.config_name}_is_installed"
        assert config._launcher_config.launcher_data[field] is True

    def test_set_minecraft_installed_set_true_and_false(
        self, tmp_path, mock_config_data
    ):
        """Test setting Minecraft installed flag to True and False."""
        loader = ConfigLoader(mock_config_data, LauncherConfig())
        config = loader.get_config(
            loader.config_list[0],
        )
        config._launcher_config._launcher_data_path = os.path.join(
            tmp_path, "launcher_data.bin"
        )

        config.set_minecraft_installed()
        config.set_minecraft_installed(False)
        field = f"{config.config_name}_is_installed"
        assert config._launcher_config._launcher_data[field] is False

    def test_is_minecraft_installed(self, tmp_path, mock_config_data):
        """
        Test the is_minecraft_installed method of MinecraftLauncherConfig.
        """
        loader = ConfigLoader(mock_config_data, LauncherConfig())
        config = loader.get_config(
            loader.config_list[0],
        )
        config._launcher_config._launcher_data_path = os.path.join(
            tmp_path, "launcher_data.bin"
        )

        assert not config.is_minecraft_installed()

        # Set the flag to True and check again
        config.set_minecraft_installed()
        assert config.is_minecraft_installed()

    def test__update_launcher_data(self, tmp_path, mock_config_data):
        """
        Test the _update_launcher_data method of MinecraftLauncherConfig.
        """
        loader = ConfigLoader(mock_config_data, LauncherConfig())
        config = loader.get_config(
            loader.config_list[0],
        )
        data_to_save = {"stored_data_key": "stored_data_value"}
        config._launcher_config._launcher_data_path = os.path.join(
            tmp_path, "launcher_data.bin"
        )
        # Create a sample stored data
        config._launcher_config._launcher_data = data_to_save

        # Update stored data in the file
        config._launcher_config._update_launcher_data()

        with shelve.open(config._launcher_config._launcher_data_path) as data:
            save_data = dict(data)

        # Check if the stored data matches the original data
        assert save_data == data_to_save
