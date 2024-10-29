"""Pytest conftest."""

# pylint: disable=W0212,W0613
import json
from unittest.mock import MagicMock

import pytest
from loguru import logger as log
from qtpy.QtCore import QSettings
from src.launcher.launcher_configs import ServerConfig, ServerConfigManager
from src.launcher.main_window import Window
from src.launcher.utility.file_downloader import FileDownloaderProtocol
from src.launcher.utility.pydantic_models import (
    ServerConfig as PydanticServerConfig,
)

log.remove()


CONFIG_NAME_1 = "TestModpack1"
CONFIG_NAME_2 = "TestModpack2"
DISPLAY_NAME_1 = "display_name_1"
DISPLAY_NAME_2 = "display_name_2"
MODPACK_DISPLAY_NAME = "modpack_display_name"


@pytest.fixture
def mock_file_info():
    """Mock FileInfo."""
    return {
        "file_name": "test_file1.txt",
        "api_url": "http://example.com/test_file1.txt",
        "yan_obj_storage": "test_object_key1",
        "hash": "abcdef123456",
        "dist_file_path": "/path/to/test_file1.txt",
    }


@pytest.fixture
def mock_config_data(mock_file_info):
    """Mock a config data."""
    return {
        "modpacks": {
            CONFIG_NAME_1: {
                "server_config": {
                    "display_name": DISPLAY_NAME_1,
                    "minecraft_version": "1.16.5",
                    "forge_version": "1.16.5-36.2.0",
                    "minecraft_profile": "TestProfile1",
                    "minecraft_server_ip": "127.0.0.1",
                    "minecraft_server_port": "25565",
                    "description": "config_1_desc",
                    "server_icon": mock_file_info,
                },
                "main_data": [
                    {
                        "file_name": "test_file1.txt",
                        "api_url": "http://example.com/test_file1.txt",
                        "yan_obj_storage": "test_object_key1",
                        "hash": "abcdef123456",
                        "dist_file_path": "/path/to/test_file1.txt",
                    }
                ],
                "client_additional_data": {},
            },
            CONFIG_NAME_2: {
                "server_config": {
                    "display_name": DISPLAY_NAME_2,
                    "minecraft_version": "1.16.5",
                    "forge_version": "1.16.5-36.2.0",
                    "minecraft_profile": "TestProfile2",
                    "minecraft_server_ip": "127.0.0.1",
                    "minecraft_server_port": "25565",
                    "description": "config_2_desc",
                    "server_icon": mock_file_info,
                },
                "main_data": [
                    {
                        "file_name": "test_file2.txt",
                        "api_url": "http://example.com/test_file2.txt",
                        "yan_obj_storage": "test_object_key2",
                        "hash": "abcdef123456",
                        "dist_file_path": "/path/to/test_file2.txt",
                    }
                ],
                "client_additional_data": {},
            },
        }
    }


@pytest.fixture
def mock_modpack_data(mock_file_info):
    """Mock a modpack data."""
    return {
        "server_config": {
            "display_name": MODPACK_DISPLAY_NAME,
            "minecraft_version": "1.17.1",
            "forge_version": "1.17.1-37.0.0",
            "minecraft_profile": "TestProfile3",
            "minecraft_server_ip": "192.168.0.1",
            "minecraft_server_port": "25566",
            "description": "config_1_desc",
            "server_icon": mock_file_info,
        },
        "main_data": [
            {
                "file_name": "test_file3.txt",
                "api_url": "http://example.com/test_file3.txt",
                "yan_obj_storage": "test_object_key3",
                "hash": "abcdef654321",
                "dist_file_path": "/path/to/test_file3.txt",
            }
        ],
        "client_additional_data": {},
    }


@pytest.fixture
def pydantic_server_config(mock_modpack_data) -> PydanticServerConfig:
    """Mock a pydantic ServerConfig data."""
    return PydanticServerConfig(**mock_modpack_data["server_config"])


@pytest.fixture
def mock_auth_data():
    """Mock auth data."""
    return {
        "status": "status",
        "username": "username",
        "uuid": "uuid",
        "accessToken": "accessToken",
    }


@pytest.fixture
def mock_settings() -> QSettings:
    """Mock QSettings instance"""

    # pylint: disable=C0415

    company_name = "IzharusTest"
    app_name = "TestApp"

    settings = QSettings(company_name, app_name)
    settings.clear()

    return settings


@pytest.fixture
def main_window(mock_settings, qtbot) -> Window:
    """Mock main window."""
    window = Window(settings=mock_settings)
    return window


@pytest.fixture
def server_config(main_window) -> ServerConfig:
    """Mock a ServeCOnfig."""
    return ServerConfig(
        internal_name="mock_name",
        modpack=MagicMock(),
        launcher_config=MagicMock(),
        settings=main_window._settings,
    )


@pytest.fixture
def auth_window(mock_settings, mock_config_data) -> Window:
    """Mock main window."""
    window = Window(settings=mock_settings)

    downloader = MagicMock(spec_set=FileDownloaderProtocol)
    downloader.download_bytes.return_value = json.dumps(
        mock_config_data
    ).encode("utf-8")
    window._config_installer_thread._config_manager = ServerConfigManager(
        file_downloader=downloader,
        map_object_key="mock_key",
    )
    window._config_installer_complete()
    return window
