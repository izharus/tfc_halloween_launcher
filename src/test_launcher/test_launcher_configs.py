"""Tests for src/launcher_config.py"""
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


def test_get_config_do_not_returns_default_config(caplog):
    """
    Check if get_config() returns default config
    if config_name incorrect.
    """
    config_name = "nonexistent_config"
    result = get_config(config_name)

    assert callable(result)
    assert isinstance(result(), MinecraftLauncherConfig)

    assert "Unknown config name" in caplog.text
    log_message = (
        "Setting default config: " f"{list(SUPPORTED_CONFIGS.values())[0]}"
    )
    assert log_message in caplog.text


def test_java_install_url_is_incorrect():
    """Java install url is universal and should not be changed."""
    java_install_url = "https://java-for-minecraft.com/ru/"
    assert LauncherConfig.java_install_url == java_install_url

    for config in SUPPORTED_CONFIGS.values():
        assert config().java_install_url == java_install_url


# Add more test cases as needed
