"""Tests for src/launcher_config.py"""
# pylint:disable = E0401
# pylint: disable=W0212
import json
import os
from unittest.mock import MagicMock

import pytest
from src.launcher.launcher_configs import ConfigLoader, MinecraftLauncherConfig
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


class TestConfigLoader:
    """Unit tests for ConfigLoader."""

    def test_download_from_url_success(
        self,
        mocker,
        mock_config_data,
    ):
        """Test download_from_url method with correct json data."""
        mock_download_file = MagicMock()
        mock_download_file.return_value = json.dumps(mock_config_data)
        with mocker.patch.object(
            FileDownloader,
            "download_file",
            mock_download_file,
        ):
            loader = ConfigLoader.download_from_url("test_url")
        assert loader.config_list == list(mock_config_data.keys())

    def test_download_from_url_request_error(self, mocker):
        """Test download_from_url method when download request fails."""
        with pytest.raises(RequestDownloadError):
            mocker.patch.object(
                FileDownloader,
                "download_file",
                side_effect=RequestDownloadError,
            )
            ConfigLoader.download_from_url("test_url")

    def test_download_from_url_config_invalid_json_data(self, mocker):
        """Test download_from_url method when json data is invalid."""
        with pytest.raises(ConfigProcessingError):
            mocker.patch.object(
                FileDownloader,
                "download_file",
                return_value="invalid_json_data",
            )
            ConfigLoader.download_from_url("test_url")

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
            ConfigLoader.download_from_url("test_url")

    def test_config_list(self, mock_config_data):
        """
        Test config_list method to ensure it returns a list of supported
        configuration names.
        """
        loader = ConfigLoader(mock_config_data)
        assert loader.config_list == ["config1", "config2"]

    def test_get_config(self, mock_config_data):
        """
        Test get_config method to ensure it returns the configuration
        data for a specified configuration name.
        """
        loader = ConfigLoader(mock_config_data)
        config_name = "config1"
        config = loader.get_config(config_name)
        assert config == MinecraftLauncherConfig(mock_config_data[config_name])

    def test_get_config_missing_name(self, mock_config_data):
        """
        Test get_config method when the specified configuration name
        is not found in the loaded data.
        """
        loader = ConfigLoader(mock_config_data)
        missing_config_name = "missing_config"
        with pytest.raises(ConfigProcessingError):
            loader.get_config(missing_config_name)


class TestMinecraftLauncherConfig:
    """Unit tests for MinecraftLauncherConfig."""

    def test_set_minecraft_installed_set_true(
            self, tmp_path, mock_config_data):
        """Test setting Minecraft installed flag to True."""
        loader = ConfigLoader(mock_config_data)
        config = loader.get_config(
            loader.config_list[0],
        )
        config.launcher_data = os.path.join(tmp_path, "launcher_data.bin")

        config.set_minecraft_installed()
        field = f"{config.config_name}_is_installed"
        assert config.launcher_stored_data[field] is True

    def test_set_minecraft_installed_set_true_and_false(
            self, tmp_path, mock_config_data):
        """Test setting Minecraft installed flag to True and False."""
        loader = ConfigLoader(mock_config_data)
        config = loader.get_config(
            loader.config_list[0],
        )
        config.launcher_data = os.path.join(tmp_path, "launcher_data.bin")

        config.set_minecraft_installed()
        config.set_minecraft_installed(False)
        field = f"{config.config_name}_is_installed"
        assert config.launcher_stored_data[field] is False
    def test_is_minecraft_installed(self, tmp_path, mock_config_data):
        """
        Test the is_minecraft_installed method of MinecraftLauncherConfig.
        """
        loader = ConfigLoader(mock_config_data)
        config = loader.get_config(
            loader.config_list[0],
        )
        config.launcher_data = os.path.join(tmp_path, "launcher_data.bin")

        assert not config.is_minecraft_installed()

        # Set the flag to True and check again
        config.set_minecraft_installed()
        assert config.is_minecraft_installed()

    def test__get_stored_data(self, tmp_path, mock_config_data):
        """
        Test the _get_stored_data method of MinecraftLauncherConfig.
        """
        loader = ConfigLoader(mock_config_data)
        config = loader.get_config(
            loader.config_list[0],
        )
        config.launcher_data = os.path.join(tmp_path, "launcher_data.bin")
        # Create a sample stored data
        config.launcher_stored_data = {"stored_data_key": "stored_data_value"}

        # Update stored data in the file
        config._update_stored_data()

        # Reset stored data in the object
        config.launcher_stored_data = {}

        # Get stored data from the file
        config._get_stored_data()

        # Check if the stored data matches the original data
        assert config.launcher_stored_data == {
            "stored_data_key": "stored_data_value"
        }
