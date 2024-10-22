"""Tests for src/launcher_config.py"""

# pylint: disable=W0212,W0613,E0401
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
            assert Path(launcher_config._general_lib_dir, dirname).exists()

    def test_get_servers_data_dir(
        self,
    ):
        """Check if get_servers_data_di generates correct path."""
        launcher_config = LauncherConfig()
        server_name = Path("server_name")
        launcher_config._servers_data_dir = Path("data_dir")

        assert (
            launcher_config.get_servers_data_dir(server_name)
            == launcher_config._servers_data_dir / server_name
        )

    def test_init_server_directory_create_main_dir(
        self,
        tmp_path: Path,
    ):
        """
        Check if init_server_directory creates a main server data directory.
        """
        server_data_dir = tmp_path / "server_dir"  # type: ignore

        LauncherConfig().init_server_directory(server_data_dir)

        assert server_data_dir.exists()

    def test_init_server_directory_check_symbolic_links_create(
        self, tmp_path: Path
    ):
        """Check if init_server_directory creates symbolic links."""

        launcher_config = LauncherConfig()

        launcher_config.init_server_directory(tmp_path)

        for dirname in launcher_config._GENERAL_DIR_NAMES:

            symlink = tmp_path / dirname
            expected_target = launcher_config._general_lib_dir / dirname
            assert symlink.is_symlink()
            assert symlink.resolve() == expected_target

    def test_init_server_directory_check_symbolic_links_create_after_moving(
        self, tmp_path: Path
    ):
        """
        Check if init_server_directory recreates correct symbolic links
        if _general_lib_dir was changed.
        """

        launcher_config = LauncherConfig()

        launcher_config.init_server_directory(tmp_path)

        launcher_config.set_download_dir(tmp_path / "new_downloads")

        launcher_config.init_server_directory(tmp_path)
        for dirname in launcher_config._GENERAL_DIR_NAMES:

            symlink = tmp_path / dirname
            expected_target = launcher_config._general_lib_dir / dirname
            assert symlink.is_symlink()
            assert symlink.resolve() == expected_target


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

    @pytest.mark.parametrize("install_status", (True, False))
    def test_is_minecraft_installed_setter(
        self,
        install_status: bool,
        server_config: ServerConfig,
        tmp_path: Path,
        qtbot,
    ):
        """
        Tests is_minecraft_installed setter.
        """
        server_config.minecraft_directory = tmp_path
        server_config.is_minecraft_installed = install_status

        assert server_config.is_minecraft_installed == install_status

    def test_is_minecraft_installed_if_directory_non_exists(
        self,
        server_config: ServerConfig,
        qtbot,
    ):
        """
        Tests if is_minecraft_installed returns correct value when
        the game directory is non-exists. If minecraft_directory
        is changed or deleted, the installation status should also be updated.
        """
        server_config.is_minecraft_installed = True

        server_config.minecraft_directory = Path("non-exists")  # type: ignore
        assert not server_config.is_minecraft_installed

    def test_is_minecraft_installed_calls_init_server_directory_exists_dir(
        self,
        server_config: ServerConfig,
        mocker: MockerFixture,
        tmp_path: Path,
        qtbot,
    ):
        """
        Check if is_minecraft_installed calls init_server_directory
        if minecraft_directory exists.
        """
        mock_init = MagicMock()
        with mocker.patch.object(
            server_config._launcher_config,
            "init_server_directory",
            mock_init,
        ):
            server_config.minecraft_directory = tmp_path
            status = server_config.is_minecraft_installed

        assert not status
        mock_init.assert_called_once_with(server_config.minecraft_directory)

    def test_is_minecraft_installed_calls_init_server_directory_non_exists_dir(
        self,
        server_config: ServerConfig,
        mocker: MockerFixture,
        qtbot,
    ):
        """
        Check if is_minecraft_installed calls init_server_directory
        if minecraft_directory is not exist.
        """
        mock_init = MagicMock()
        with mocker.patch.object(
            server_config._launcher_config,
            "init_server_directory",
            mock_init,
        ):
            server_config.minecraft_directory = Path("non-exists")
            status = server_config.is_minecraft_installed

        assert not status
        mock_init.assert_called_once_with(server_config.minecraft_directory)
