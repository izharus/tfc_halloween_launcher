"""Tests fpr src.test.test_launcher_installer.py"""

# pylint: disable=W0212,E0401

import json
import subprocess
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from src.launcher.launcher_configs import ServerConfig
from src.launcher.launcher_installer import (
    ConfigInstallerThread,
    InstallThread,
    MinecraftExecutorThread,
)
from src.launcher.utility.custom_exceptions import FileDownloadError
from src.launcher.utility.pydantic_models import AuthData


@pytest.fixture
def executor_thread() -> MinecraftExecutorThread:
    """Mock MinecraftExecutorThread."""
    return MinecraftExecutorThread(
        auth_data=AuthData(
            status="mock_status",
            username="mock_nickname",
            uuid="mock_uuid",
            accessToken="mock_access_token",
        ),
        server_config=MagicMock(),
        settings=MagicMock(),
    )


class TestConfigInstallerThread:
    """Tests for ConfigInstallerThread."""

    def test_initial_config_manager_state(self):
        """Check if _config_manager is empty initially."""
        installer = ConfigInstallerThread(MagicMock(), MagicMock())
        assert installer.config_manager is None

    def test_successful_installation(self, qtbot, mock_config_data):
        """Test run method when ServerConfigManager installs correct."""

        mock_file_downloader = MagicMock()
        mock_file_downloader.download_bytes = MagicMock(
            return_value=json.dumps(mock_config_data)
        )
        installer = ConfigInstallerThread(
            mock_file_downloader, "mock_object_key"
        )

        with qtbot.wait_signals(
            [installer.finished, installer.success, installer.write_info]
        ):
            with qtbot.assertNotEmitted(installer.write_error):
                installer.run()

    def test_installation_with_invalid_config(self, qtbot):
        """
        Test run method when ServerConfigManager raises ConfigProcessingError.
        """

        mock_file_downloader = MagicMock()
        mock_file_downloader.download_bytes = MagicMock(
            return_value="invalid_value"
        )
        installer = ConfigInstallerThread(
            mock_file_downloader, "mock_object_key"
        )

        with qtbot.wait_signals([installer.finished, installer.write_info]):
            with qtbot.assertNotEmitted(installer.success):
                installer.run()

    def test_installation_with_download_error(self, qtbot):
        """
        Test run method when ServerConfigManager raises FileDownloadError .
        """

        mock_file_downloader = MagicMock()
        mock_file_downloader.download_bytes = MagicMock(
            side_effect=FileDownloadError
        )
        installer = ConfigInstallerThread(
            mock_file_downloader, "mock_object_key"
        )

        with qtbot.wait_signals([installer.finished, installer.write_info]):
            with qtbot.assertNotEmitted(installer.success):
                installer.run()


class TestMinecraftExecutorThread:
    """Tests for MinecraftExecutorThread."""

    def test_create_launcher_options_allocate_ram_not_specified(
        self,
        executor_thread: MinecraftExecutorThread,
    ):
        """Test that 'jvmArguments' is not present if RAM is not specified."""
        options = executor_thread.create_launcher_options()

        assert "jvmArguments" not in options

    def test_create_launcher_options_with_allocate_ram_zero(
        self,
        executor_thread: MinecraftExecutorThread,
    ):
        """Test that 'jvmArguments' is not added if RAM is 0."""
        ram = 0
        options = executor_thread.create_launcher_options(allocate_ram=ram)

        assert "jvmArguments" not in options

    def test_create_launcher_options_with_allocate_ram(
        self,
        executor_thread: MinecraftExecutorThread,
    ):
        """Test that correct 'jvmArguments' are added when RAM is specified."""
        ram = 34_314
        options = executor_thread.create_launcher_options(allocate_ram=ram)

        assert f"-Xmx{ram}m" in options["jvmArguments"]

    def test_ram_allocating_by_slider(
        self,
        executor_thread: MinecraftExecutorThread,
        mocker: MockerFixture,
    ):
        """Test the RAM allocation process via the slider in the UI."""
        allocated_ram = 8192
        mock_create_options = MagicMock()
        mock_popen = MagicMock()
        # Mock create_launcher_options
        mocker.patch.object(
            executor_thread,
            "create_launcher_options",
            mock_create_options,
        )

        # Mock slider value
        mocker.patch.object(
            executor_thread._settings,
            "get_ui_value",
            return_value=allocated_ram,
        )

        mocker.patch.object(
            subprocess,
            "Popen",
            mock_popen,
        )

        executor_thread.run()

        mock_create_options.assert_called_once_with(allocated_ram)

    def test_create_default_options_called_in_run_due_exception(
        self,
        executor_thread: MinecraftExecutorThread,
        mocker: MockerFixture,
    ):
        """
        Test that create_default_options and update_default_options
        are called when run is executed.
        """

        mocker.patch.object(
            subprocess,
            "Popen",
            side_effect=RuntimeError,
        )
        executor_thread._config.create_default_options = MagicMock()
        executor_thread._config.update_default_options = MagicMock()

        executor_thread.run()

        executor_thread._config.create_default_options.assert_called_once()
        executor_thread._config.update_default_options.assert_called_once()


class TestInstallThread:
    """Tests for InstallThread."""

    @pytest.mark.parametrize("initial_state", (False, True))
    def test_check_is_installed_flag_setting(
        self,
        initial_state: bool,
        mocker: MockerFixture,
        server_config: ServerConfig,
    ):
        """
        Tests that the `is_minecraft_installed` flag in `server_config`
        is set to `True` after running the `InstallThread`.
        """
        thread = InstallThread(
            server_config,
            lambda: True,
            server_config,
        )
        mocker.patch.object(thread, "main_worker")

        server_config.is_minecraft_installed = initial_state

        thread.run()

        assert server_config.is_minecraft_installed is True

    @pytest.mark.parametrize("initial_state", (False, True))
    def test_check_is_installed_flag_after_failure_installation(
        self,
        mocker: MockerFixture,
        server_config: ServerConfig,
        initial_state: bool,
    ):
        """
        Tests that the `is_minecraft_installed` flag in `server_config`
        remains `False` if the `InstallThread` encounters a failure during
        installation.
        """
        thread = InstallThread(
            server_config,
            lambda: True,
            server_config,
        )
        mocker.patch.object(thread, "main_worker", side_effect=RuntimeError)

        server_config.is_minecraft_installed = initial_state

        thread.run()

        assert server_config.is_minecraft_installed is False
