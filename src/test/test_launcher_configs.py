"""Tests for src/launcher_config.py"""
# pylint:disable = E0401
# pylint: disable=W0212
import os

from src.launcher.launcher_configs import (
    SUPPORTED_CONFIGS,
    LauncherConfig,
    MinecraftLauncherConfig,
    get_config,
)


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
