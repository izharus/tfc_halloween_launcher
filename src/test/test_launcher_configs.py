"""Tests for src/launcher_config.py"""

# pylint:disable = E0401
# pylint: disable=W0212
import json
from pathlib import Path
from unittest.mock import MagicMock

import minecraft_launcher_lib as mine_lib
import pytest
from pytest_mock import MockerFixture
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


class TestLauncherConfig:
    """Tests for LauncherConfig."""

    def test__create_general_dirs(
        self,
        mocker: MockerFixture,
        tmp_path: Path,
    ):
        """
        Tests if is_minecraft_installed returns correct value when
        the game directory is non-exists.
        """
        with mocker.patch.object(
            mine_lib.utils,
            "get_minecraft_directory",
            return_value=str(tmp_path),
        ):
            launcher_config = LauncherConfig()
        for dirname in launcher_config._GENERAL_DIR_NAMES:
            assert Path(
                launcher_config.general_lib_directory, dirname
            ).exists()


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
    """Test for ServerCOnfig."""

    @pytest.mark.parametrize("install_status", (True, False))
    def test_is_minecraft_installed_if_directory_exists(
        self,
        mocker: MockerFixture,
        tmp_path: Path,
        install_status: bool,
    ):
        """
        Tests if is_minecraft_installed returns correct value when
        the game directory is already exists.
        """
        server_config = ServerConfig(
            internal_name="mock_name",
            modpack=MagicMock(),
            launcher_config=MagicMock(),
            settings=MagicMock(),
        )

        server_config.minecraft_directory = tmp_path  # type: ignore
        mocker.patch.object(
            server_config._settings,
            "get_user_value",
            return_value=install_status,
        )

        assert server_config.is_minecraft_installed == install_status

    def test_is_minecraft_installed_if_directory_non_exists(
        self,
        mocker: MockerFixture,
    ):
        """
        Tests if is_minecraft_installed returns correct value when
        the game directory is non-exists.
        """
        server_config = ServerConfig(
            internal_name="mock_name",
            modpack=MagicMock(),
            launcher_config=MagicMock(),
            settings=MagicMock(),
        )

        server_config.minecraft_directory = "non-exists"  # type: ignore
        mocker.patch.object(
            server_config._settings, "get_user_value", return_value=True
        )

        assert not server_config.is_minecraft_installed
