"""Tests for src/launcher_config.py"""
# pylint:disable = E0401
# pylint: disable=W0212
import json
import os
from unittest.mock import MagicMock

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


class TestConfigLoader:
    """Unit tests for ConfigLoader."""

    @pytest.fixture
    def mock_config_data(self):
        """Mock a config data."""
        return {
            "config1": {"param1": "value1"},
            "config2": {"param2": "value2"},
        }

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


def test_get_config_do_not_returns_existing_config():
    """Check in get_config() returns correct config."""
    config_name = "TFC Halloween"
    config: MinecraftLauncherConfig = get_config(config_name)
    assert callable(config)
    assert config().config_name == "terrafirmacraft"
    assert isinstance(config(), MinecraftLauncherConfig)


def test_get_config_do_not_returns_default_config():
    """
    Check if get_config() returns default config
    if config_name incorrect.
    """
    config_name = "nonexistent_config"
    result = get_config(config_name)

    assert callable(result)
    assert isinstance(result(), MinecraftLauncherConfig)
    assert result is list(SUPPORTED_CONFIGS.values())[0]


def test_java_install_url_is_incorrect():
    """Java install url is universal and should not be changed."""
    java_install_url = "https://java-for-minecraft.com/ru/"
    assert LauncherConfig.java_install_url == java_install_url

    for config in SUPPORTED_CONFIGS.values():
        assert config().java_install_url == java_install_url


def test_is_minecraft_installed(tmp_path, mocker):
    """
    Test the is_minecraft_installed method of MinecraftLauncherConfig.
    """
    # pylint: disable = C0301
    mocker.patch(
        "src.launcher.launcher_configs.MinecraftLauncherConfig.parse_map_json_data",
        return_value="Test map_json file data.",
    )
    config = get_config("TFC Halloween TEST")()
    config.launcher_data = os.path.join(tmp_path, "launcher_data.bin")

    assert not config.is_minecraft_installed()

    # Set the flag to True and check again
    config.set_minecraft_installed()
    assert config.is_minecraft_installed()


def test_get_stored_data(tmp_path, mocker):
    """
    Test the get_stored_data method of MinecraftLauncherConfig.
    """
    # pylint: disable = C0301
    mocker.patch(
        "src.launcher.launcher_configs.MinecraftLauncherConfig.parse_map_json_data",
        return_value="Test map_json file data.",
    )
    config = get_config("TFC Halloween TEST")()
    config.launcher_data = os.path.join(tmp_path, "launcher_data.bin")
    # Create a sample stored data
    config.launcher_stored_data = {"stored_data_key": "stored_data_value"}

    # Update stored data in the file
    config._update_stored_data()

    # Reset stored data in the object
    config.launcher_stored_data = {}

    # Get stored data from the file
    config.get_stored_data()

    # Check if the stored data matches the original data
    assert config.launcher_stored_data == {
        "stored_data_key": "stored_data_value"
    }


def test_parse_map_json_data(tmp_path, mocker):
    """
    Test the parse_map_json_data method of MinecraftLauncherConfig.
    """
    # pylint: disable = C0301
    config = get_config("TFC Halloween TEST")()
    config.launcher_data = os.path.join(tmp_path, "launcher_data.bin")
    # Use Mocker to mock the FileDownloader class
    mocker.patch(
        "src.launcher.launcher_configs.FileDownloader.download_file",
        return_value='{"terrafirmacraft_test": {"key": "value"}}',
    )

    config.map_json_url = "http://example.com/map.json"
    config.parse_map_json_data()

    assert config.map_json_data == {"key": "value"}
