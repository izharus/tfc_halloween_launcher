"""Tests fpr src.test.test_launcher_installer.py"""

# pylint: disable=W0212

import json
import subprocess
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from src.launcher.launcher_installer import (
    ConfigInstallerThread,
    MinecraftExecutorThread,
)
from src.launcher.utility.custom_exceptions import FiletDownloadError


@pytest.fixture
def executor_thread() -> MinecraftExecutorThread:
    """Mock MinecraftExecutorThread."""
    return MinecraftExecutorThread(
        nickname="mock_nickname",
        uuid="mock_uuid",
        access_token="mock_access_token",
        config=MagicMock(),
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
        Test run method when ServerConfigManager raises FiletDownloadError.
        """

        mock_file_downloader = MagicMock()
        mock_file_downloader.download_bytes = MagicMock(
            side_effect=FiletDownloadError
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

        with mocker.patch.object(
            subprocess,
            "Popen",
            mock_popen,
        ):
            executor_thread.run()

        mock_create_options.assert_called_once_with(allocated_ram)
