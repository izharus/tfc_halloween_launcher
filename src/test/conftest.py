"""Pytest conftest."""

import pytest

CONFIG_NAME_1 = "TestModpack1"
CONFIG_NAME_2 = "TestModpack2"
DISPLAY_NAME_1 = "display_name_1"
DISPLAY_NAME_2 = "display_name_2"
MODPACK_DISPLAY_NAME = "modpack_display_name"


@pytest.fixture
def mock_config_data():
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
def mock_modpack_data():
    """Mock a modpack data."""
    return {
        "server_config": {
            "display_name": MODPACK_DISPLAY_NAME,
            "minecraft_version": "1.17.1",
            "forge_version": "1.17.1-37.0.0",
            "minecraft_profile": "TestProfile3",
            "minecraft_server_ip": "192.168.0.1",
            "minecraft_server_port": "25566",
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
def mock_auth_data():
    """Mock auth data."""
    return {
        "status": "status",
        "username": "username",
        "uuid": "uuid",
        "accessToken": "accessToken",
    }
