"""Tests for src/launcher_config.py"""

# pylint:disable = E0401
# pylint: disable=W0212
import json
from unittest.mock import MagicMock

import minecraft_launcher_lib as mine_lib
import pytest
from src.launcher.launcher_configs import ServerConfigManager
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
