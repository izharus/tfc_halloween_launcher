"""Tests for src/launcher_config.py"""

# pylint: disable=W0212,W0613,E0401,C0411,C0103
import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import src.minecraft_launcher_lib.minecraft_launcher_lib as mine_lib
from pytest_mock import MockerFixture
from src.launcher.launcher_configs import (
    DEFAULT_USER_SETTINGS,
    LauncherConfig,
    ServerConfig,
    ServerConfigManager,
)
from src.launcher.utility.custom_exceptions import (
    ConfigDownloadError,
    ConfigProcessingError,
    FileDownloadError,
    ModpackNotfound,
)
from src.launcher.utility.pydantic_models import MapJson, Modpack


class TestLauncherConfig:
    """Tests for LauncherConfig."""

    def test__create_launcher_dirs(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ):
        """Test if launcher create initial directories correctly."""
        mocker.patch.object(
            mine_lib.utils,
            "get_minecraft_directory",
            return_value=str(tmp_path),
        )

        launcher_config = LauncherConfig()

        assert launcher_config.LAUNCHER_ROOT_DIR.exists()
        assert launcher_config.LAUNCHER_DATA_DIR.exists()
        assert launcher_config.MINECRAFT_SKIN_DIR.exists()
        assert launcher_config.MINECRAFT_CAPE_DIR.exists()
        assert launcher_config.LAUNCHER_SERVER_ICONS_DIR.exists()

    def test__create_general_dirs(
        self,
        mocker: MockerFixture,
        tmp_path: Path,
    ):
        """
        Tests if is_minecraft_installed returns correct value when
        the game directory is non-exists.
        """
        mocker.patch.object(
            mine_lib.utils,
            "get_minecraft_directory",
            return_value=str(tmp_path),
        )

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

    def test_get_icon_icon_exists(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ):
        """Test get_icon_file returns correct icon path."""
        mocker.patch.object(
            mine_lib.utils,
            "get_minecraft_directory",
            return_value=str(tmp_path),
        )

        launcher_config = LauncherConfig()
        filehash = "hash"
        expected_file_content = b"Test_bin_data."
        tmp_file = launcher_config.LAUNCHER_SERVER_ICONS_DIR / filehash
        tmp_file.write_bytes(expected_file_content)
        launcher_config = LauncherConfig()

        icon_path = launcher_config.get_icon_file(filehash)

        assert (
            icon_path == launcher_config.LAUNCHER_SERVER_ICONS_DIR / filehash
        )
        assert icon_path.read_bytes() == expected_file_content

    def test_get_icon_icon_not_exists(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ):
        """Test get_icon_file returns None if icon not exists."""
        mocker.patch.object(
            mine_lib.utils,
            "get_minecraft_directory",
            return_value=str(tmp_path),
        )

        launcher_config = LauncherConfig()
        filehash = "non_exists"
        launcher_config = LauncherConfig()

        icon_path = launcher_config.get_icon_file(filehash)

        assert icon_path is None

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

    def test_create_default_options_minecraft_dir_exists(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ):
        """
        Test that default options are created correctly when
        the Minecraft directory exists.
        """
        launcher_config = LauncherConfig()
        expected_options = "options_content"

        launcher_config.DEFAULT_OPTIONS_PATH = tmp_path / "d" / "options.txt"

        mock_options = tmp_path / "options.txt"
        mock_options.write_text(expected_options)

        mocker.patch.object(
            mine_lib.utils,
            "get_minecraft_directory",
            return_value=mock_options.parent,
        )
        launcher_config._create_default_options()

        current_options = launcher_config.DEFAULT_OPTIONS_PATH.read_text()
        assert current_options == expected_options

    def test_create_default_options_minecraft_not_exists(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ):
        """
        Test that default options are created when
        the Minecraft directory does not exist.
        """
        launcher_config = LauncherConfig()
        expected_options = DEFAULT_USER_SETTINGS
        launcher_config.DEFAULT_OPTIONS_PATH = tmp_path / "d" / "options.txt"

        mock_options = tmp_path / "options.txt"

        mocker.patch.object(
            mine_lib.utils,
            "get_minecraft_directory",
            return_value=mock_options.parent,
        )
        launcher_config._create_default_options()

        current_options = launcher_config.DEFAULT_OPTIONS_PATH.read_text()
        assert current_options == expected_options

    def test_create_default_options_called_during_initialization(
        self,
        mocker: MockerFixture,
    ):
        """
        Test that `_create_default_options` is called during
        the initialization of `LauncherConfig`.
        """

        mock_create_default_options = MagicMock()
        mocker.patch.object(
            LauncherConfig,
            "_create_default_options",
            mock_create_default_options,
        )
        LauncherConfig()

        mock_create_default_options.assert_called_once()


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
        mocker.patch.object(
            mock_file_downloader,
            "download_bytes",
            mock_download_bytes,
        )

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
        mocker.patch.object(
            mock_file_downloader,
            "download_bytes",
            side_effect=FileDownloadError,
        )

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
        mocker.patch.object(
            mock_file_downloader,
            "download_bytes",
            return_value=b'{"some_key": 1}',
        )

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
        mocker.patch.object(
            mock_file_downloader,
            "download_bytes",
            return_value="1",
        )

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
        mocker.patch.object(
            mock_file_downloader,
            "download_bytes",
            return_value="{{{{1",
        )

        with pytest.raises(ConfigProcessingError):
            ServerConfigManager(
                mock_file_downloader,
                object_key,
            )

    def test_get_modpack_success(
        self,
        mocker,
        mock_config_data,
    ):
        """Test get_modpack returns modpack object."""
        object_key = "mock_object_key"
        mock_file_downloader = MagicMock()
        mock_download_bytes = MagicMock(
            return_value=json.dumps(mock_config_data),
        )
        mocker.patch.object(
            mock_file_downloader,
            "download_bytes",
            mock_download_bytes,
        )
        config_manager = ServerConfigManager(
            mock_file_downloader,
            object_key,
        )

        modpack = config_manager.get_modpack("TestModpack1")

        assert isinstance(modpack, Modpack)
        assert modpack.server_config.display_name == "display_name_1"

    def test_get_modpack_not_found(
        self,
        mocker,
        mock_config_data,
    ):
        """
        Test get_modpack raises an exception if the modpack not found.
        """
        object_key = "mock_object_key"
        mock_file_downloader = MagicMock()
        mock_download_bytes = MagicMock(
            return_value=json.dumps(mock_config_data),
        )
        mocker.patch.object(
            mock_file_downloader,
            "download_bytes",
            mock_download_bytes,
        )
        config_manager = ServerConfigManager(
            mock_file_downloader,
            object_key,
        )

        with pytest.raises(ModpackNotfound):
            config_manager.get_modpack("non-exists")


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
    def test_is_minecraft_installed_if_minecraft_profile_exists(
        self,
        mocker: MockerFixture,
        tmp_path: Path,
        install_status: bool,
    ):
        """
        Tests if is_minecraft_installed if minecraft profile is exists.
        """
        profile_id = "forge_5000"
        profile_path = tmp_path / "versions" / profile_id
        profile_path.mkdir(parents=True)
        server_config = ServerConfig(
            internal_name="mock_name",
            modpack=MagicMock(),
            launcher_config=MagicMock(),
            settings=MagicMock(),
        )
        server_config.minecraft_profile = profile_id
        server_config._launcher_config.general_lib_dir = tmp_path

        server_config.minecraft_directory = tmp_path  # type: ignore
        mocker.patch.object(
            server_config._settings,
            "get_user_value",
            return_value=install_status,
        )

        assert server_config.is_minecraft_installed is False

    @pytest.mark.parametrize("install_status", (True, False))
    def test_is_minecraft_installed_if_minecraft_profile_not_exists(
        self,
        mocker: MockerFixture,
        tmp_path: Path,
        install_status: bool,
    ):
        """
        Tests if is_minecraft_installed if minecraft profile is not exists.
        """
        profile_id = "forge_5000"
        (tmp_path / "versions").mkdir()

        server_config = ServerConfig(
            internal_name="mock_name",
            modpack=MagicMock(),
            launcher_config=MagicMock(),
            settings=MagicMock(),
        )
        server_config.minecraft_profile = profile_id
        server_config._launcher_config.general_lib_dir = tmp_path

        server_config.minecraft_directory = tmp_path  # type: ignore

        assert server_config.is_minecraft_installed is False

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
        mocker.patch.object(
            server_config._launcher_config,
            "init_server_directory",
            mock_init,
        )

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
        mocker.patch.object(
            server_config._launcher_config,
            "init_server_directory",
            mock_init,
        )

        server_config.minecraft_directory = Path("non-exists")
        status = server_config.is_minecraft_installed

        assert not status
        mock_init.assert_called_once_with(server_config.minecraft_directory)

    def test_create_default_options_for_non_exists_options(
        self,
        tmp_path: Path,
        server_config: ServerConfig,
    ):
        """
        Test that `create_default_options` writes default options to the
        Minecraft options file when it does not already exist.
        """
        default_options = "some_def_options"
        server_config._launcher_config.DEFAULT_OPTIONS_PATH = (
            tmp_path / "default_options.txt"
        )
        server_config._launcher_config.DEFAULT_OPTIONS_PATH.write_text(
            default_options,
        )
        server_config.minecraft_directory = tmp_path

        server_config.create_default_options()
        current_options = server_config.minecraft_options_path.read_text()

        assert current_options == default_options

    def test_create_default_options_for_exists_options(
        self,
        tmp_path: Path,
        server_config: ServerConfig,
    ):
        """
        Test that `create_default_options` does not overwrite existing options
        when the options file is already present.
        """
        default_options = "some_def_options"
        expected_options = "expected_options"
        server_config._launcher_config.DEFAULT_OPTIONS_PATH = (
            tmp_path / "default_options.txt"
        )
        server_config._launcher_config.DEFAULT_OPTIONS_PATH.write_text(
            default_options,
        )
        server_config.minecraft_directory = tmp_path
        server_config.minecraft_options_path.write_text(expected_options)

        server_config.create_default_options()
        current_options = server_config.minecraft_options_path.read_text()

        assert current_options == expected_options

    def test_update_default_options_with_new_options(
        self,
        tmp_path: Path,
        server_config: ServerConfig,
    ):
        """
        Test that `update_default_options` updates the default options
        file with new options if changes are detected.
        """
        default_options = "some_def_options"
        new_options = "expected_options"
        server_config._launcher_config.DEFAULT_OPTIONS_PATH = (
            tmp_path / "default_options.txt"
        )
        server_config._launcher_config.DEFAULT_OPTIONS_PATH.write_text(
            default_options,
        )
        server_config.minecraft_directory = tmp_path
        server_config.minecraft_options_path.write_text(new_options)

        server_config.update_default_options()
        current_options = (
            server_config._launcher_config.DEFAULT_OPTIONS_PATH.read_text()
        )

        assert current_options == new_options

    def test_update_default_options_for_non_exists_new_options(
        self,
        tmp_path: Path,
        server_config: ServerConfig,
    ):
        """
        Test that `update_default_options` does not modify the default
        options file when new options are not available.
        """
        default_options = "some_def_options"
        server_config._launcher_config.DEFAULT_OPTIONS_PATH = (
            tmp_path / "default_options.txt"
        )
        server_config._launcher_config.DEFAULT_OPTIONS_PATH.write_text(
            default_options,
        )
        server_config.minecraft_directory = tmp_path

        server_config.update_default_options()
        current_options = (
            server_config._launcher_config.DEFAULT_OPTIONS_PATH.read_text()
        )

        assert current_options == default_options
