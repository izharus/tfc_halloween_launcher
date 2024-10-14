"""Tests fpr src.test.test_launcher_installer.py"""

import json
from unittest.mock import MagicMock

from src.launcher.launcher_installer import ConfigInstallerThread
from src.launcher.utility.custom_exceptions import FiletDownloadError


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
