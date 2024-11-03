"""Tests for launcher installer."""

# pylint: disable=E0401
from src.launcher.launcher_configs import LauncherConfig


def test_constant_variables():
    """
    These constants are needed by the installer.
    Avoid changing them incorrectly.
    """
    config = LauncherConfig()

    assert config.BASE_API_URL == "https://auth.aulecraft.ru/"
    assert (
        config.API_URL_S3_INSTALLER_CRED
        == "https://auth.aulecraft.ru/get_installer_s3_cred"
    )
