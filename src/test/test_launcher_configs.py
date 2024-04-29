"""Tests for src/launcher_config.py"""
# pylint:disable = E0401
# pylint: disable=W0212
import json
import os
import shelve
from unittest.mock import MagicMock

import boto3
import boto3.exceptions
import minecraft_launcher_lib as mine_lib
import pytest
from src.launcher.boto3_cred import BOTO3_ACCESS_KEY, BOTO3_SECRET_KEY
from src.launcher.launcher_configs import (
    ConfigGetter,
    ConfigLoader,
    LauncherConfig,
    ServerConfig,
)
from src.launcher.utillity.custom_exceptions import (
    ConfigDownloadError,
    ConfigProcessingError,
    RequestDownloadError,
)
from src.launcher.utillity.file_downloader import FileDownloader
from src.test.conftest import (
    CONFIG_NAME_1,
    CONFIG_NAME_2,
    DISPLAY_NAME_1,
    DISPLAY_NAME_2,
)


@pytest.fixture(autouse=True)
def mock_window(
    mocker,
    tmpdir,
):
    """
    Create an window instance without notification message boxes.
    Set minecraft root dir to the temp dir.
    """
    with mocker.patch.object(
        mine_lib.utils, "get_minecraft_directory", return_value=str(tmpdir)
    ):
        yield


class TestConfigLoader:
    """Unit tests for ConfigLoader."""

    def test__install_boto3_instance_when_client_not_installed(self, mocker):
        """
        Test _install_boto3_instance method when boto3 client
        is not installed.
        """
        # Create an instance of ConfigLoader
        config_loader = ConfigLoader(MagicMock(spec=LauncherConfig))
        config_loader._boto3_client = None
        mock_boto3_instance = "mock_boto3_instance"
        mock_client = MagicMock(return_value=mock_boto3_instance)
        # Mock boto3.client to ensure it is called only if _boto3_client
        # is None
        with mocker.patch.object(boto3, "client", mock_client):
            # Call the _install_boto3_instance method
            config_loader._install_boto3_instance()

        # Ensure that boto3.client was called only once
        mock_client.assert_called_once_with(
            "s3",
            endpoint_url="https://storage.yandexcloud.net",
            aws_access_key_id=BOTO3_ACCESS_KEY,
            aws_secret_access_key=BOTO3_SECRET_KEY,
        )
        assert config_loader._boto3_client == mock_boto3_instance

    def test__install_boto3_instance_when_client_already_installed(
        self, mocker
    ):
        """
        Test _install_boto3_instance method when boto3 client
        is already installed.
        """
        config_loader = ConfigLoader(MagicMock(spec=LauncherConfig))
        config_loader._boto3_client = MagicMock()
        mock_boto3_instance = "mock_boto3_instance"
        mock_client = MagicMock(return_value=mock_boto3_instance)
        # Mock boto3.client to ensure it is called only
        # if _boto3_client is None
        with mocker.patch.object(boto3, "client", mock_client):
            # Call the _install_boto3_instance method
            config_loader._install_boto3_instance()

        # Ensure that boto3.client was not called
        mock_client.assert_not_called()

    def test__install_boto3_instance_handles_exception(self, mocker):
        """Test _install_boto3_instance method handles exception."""
        # Create an instance of ConfigLoader
        config_loader = ConfigLoader(MagicMock(spec=LauncherConfig))
        config_loader._boto3_client = None
        mock_client = MagicMock(side_effect=boto3.exceptions.Boto3Error)
        # Mock boto3.client to raise a Boto3Error exception
        with mocker.patch.object(boto3, "client", mock_client):
            # Call the _install_boto3_instance method
            config_loader._install_boto3_instance()

        assert config_loader._boto3_client is None

    def test_get_from_url_success(
        self,
        mocker,
        mock_config_data,
    ):
        """Test get_from_url method with correct json data."""
        mock_download_file = MagicMock()
        mock_config = LauncherConfig()

        config_loader = ConfigLoader(mock_config)
        mock_download_file.return_value = json.dumps(mock_config_data)
        with mocker.patch.object(
            FileDownloader,
            "download_file",
            mock_download_file,
        ):
            config = config_loader.get_from_url()
        assert config == mock_config_data
        mock_download_file.assert_called_once_with(mock_config.MAP_JSON_URL)

    def test_get_from_url_request_error(self, mocker):
        """Test get_from_url method when download request fails."""
        mock_config = LauncherConfig()
        config_loader = ConfigLoader(mock_config)
        with pytest.raises(ConfigDownloadError):
            mocker.patch.object(
                FileDownloader,
                "download_file",
                side_effect=RequestDownloadError,
            )
            config_loader.get_from_url()

    def test_get_from_yos_success(
        self,
        mocker,
        mock_config_data,
    ):
        """Test get_from_yos method with correct json data."""
        mock_boto3 = MagicMock()
        mock_response = MagicMock()
        mock_response["body"] = MagicMock()
        mock_response["body"].read.return_value = json.dumps(mock_config_data)
        mock_get_object = MagicMock(return_value=mock_response)

        mock_config = LauncherConfig()
        config_loader = ConfigLoader(mock_config)
        config_loader._boto3_client = mock_boto3

        with mocker.patch.object(mock_boto3, "get_object", mock_get_object):
            config = config_loader.get_from_yos()

        assert config == mock_config_data
        mock_get_object.assert_called_once_with(
            Bucket=mock_config.BUCKET_NAME,
            Key=mock_config.MAP_JSON_YOS_OBJ_KEY,
        )

    def test_get_from_yos_request_error(self, mocker):
        """Test get_from_yos method when get_object fails."""
        mock_config = LauncherConfig()
        config_loader = ConfigLoader(mock_config)
        config_loader._boto3_client = MagicMock()
        with pytest.raises(ConfigDownloadError):
            mocker.patch.object(
                config_loader._boto3_client,
                "get_object",
                side_effect=boto3.exceptions.Boto3Error,
            )
            config_loader.get_from_yos()

    def test__create_model_from_bytes_valid_json_data(self):
        """Test _create_model_from_bytes method with valid JSON data."""
        valid_json_data = b'{"key": "value"}'
        expected_result = {"key": "value"}

        result = ConfigLoader._create_model_from_bytes(valid_json_data)

        assert result == expected_result

    def test__create_model_from_bytes_invalid_json_data(self):
        """Test _create_model_from_bytes method when json data is invalid."""
        with pytest.raises(ConfigProcessingError):
            ConfigLoader._create_model_from_bytes("invalid_data")

    def test_boto3_client_property(self, mocker):
        """Test boto3_client property."""
        # Create an instance of ConfigLoader
        config_loader = ConfigLoader(LauncherConfig())

        # Mock _install_boto3_instance method
        mock_install_boto3_instance = mocker.patch.object(
            config_loader, "_install_boto3_instance"
        )

        # Call the boto3_client property
        boto3_client = config_loader.boto3_client

        # Ensure that _install_boto3_instance method was called
        mock_install_boto3_instance.assert_called_once()

        # Ensure that the returned value is _boto3_client
        assert boto3_client == config_loader._boto3_client


class TestConfigGetter:
    """Unit tests for ConfigGetter"""

    def test_config_list(self, mock_config_data):
        """
        Test config_list method to ensure it returns a list of supported
        configuration names.
        """
        server_config = ConfigGetter(mock_config_data, LauncherConfig())
        assert server_config.config_list == [DISPLAY_NAME_1, DISPLAY_NAME_2]

    def test_set_active_existing_config(self, mock_config_data):
        """
        Test set_active method for an existing config name.
        """
        mock_launcher_config = LauncherConfig()
        server_config = ConfigGetter(
            mock_config_data,
            mock_launcher_config,
        )
        assert server_config._active_config_display_name == DISPLAY_NAME_1
        assert server_config.active == ServerConfig(
            CONFIG_NAME_1,
            mock_config_data["modpacks"][CONFIG_NAME_1],
            mock_launcher_config,
        )

        assert server_config.set_active(DISPLAY_NAME_2) is True
        assert server_config.active == ServerConfig(
            CONFIG_NAME_2,
            mock_config_data["modpacks"][CONFIG_NAME_2],
            mock_launcher_config,
        )

    def test_set_active_non_existing_config(self, mock_config_data):
        """
        Test set_active method for a non-existing config name.
        """
        mock_launcher_config = LauncherConfig()
        server_config = ConfigGetter(
            mock_config_data,
            mock_launcher_config,
        )
        assert server_config.set_active("NonExistingConfig") is False


class TestServerConfig:
    """Unit tests for ServerConfig."""

    def test_is_minecraft_installed_set_true(self, tmp_path, mock_config_data):
        """Test setting Minecraft installed flag to True."""
        server_config = ConfigGetter(
            mock_config_data,
            LauncherConfig(),
        ).active
        server_config._launcher_config._launcher_data_path = os.path.join(
            tmp_path, "launcher_data.bin"
        )

        server_config.is_minecraft_installed = True
        field = f"{server_config.internal_name}_is_installed"
        assert server_config._launcher_config.launcher_data[field] is True

    def test_sis_minecraft_installed_set_true_and_false(
        self, tmp_path, mock_config_data
    ):
        """Test setting Minecraft installed flag to True and False."""
        server_config = ConfigGetter(
            mock_config_data,
            LauncherConfig(),
        ).active
        server_config._launcher_config._launcher_data_path = os.path.join(
            tmp_path, "launcher_data.bin"
        )

        server_config.is_minecraft_installed = True
        server_config.is_minecraft_installed = False
        field = f"{server_config.internal_name}_is_installed"
        assert server_config._launcher_config.launcher_data[field] is False

    def test_is_minecraft_installed(self, tmp_path, mock_config_data):
        """
        Test the is_minecraft_installed method of MinecraftLauncherConfig.
        """
        server_config = ConfigGetter(
            mock_config_data,
            LauncherConfig(),
        ).active
        server_config._launcher_config._launcher_data_path = os.path.join(
            tmp_path, "launcher_data.bin"
        )
        assert not server_config.is_minecraft_installed

        # Set the flag to True and check again
        server_config.is_minecraft_installed = True
        assert server_config.is_minecraft_installed

    def test__update_launcher_data(self, tmp_path, mock_config_data):
        """
        Test the _update_launcher_data method of MinecraftLauncherConfig.
        """
        server_config = ConfigGetter(
            mock_config_data,
            LauncherConfig(),
        ).active
        server_config._launcher_config._launcher_data_path = os.path.join(
            tmp_path, "launcher_data.bin"
        )
        data_to_save = {"stored_data_key": "stored_data_value"}
        server_config._launcher_config._launcher_data_path = os.path.join(
            tmp_path, "launcher_data.bin"
        )
        # Create a sample stored data
        server_config._launcher_config._launcher_data = data_to_save

        # Update stored data in the file
        server_config._launcher_config._update_launcher_data()

        with shelve.open(
            server_config._launcher_config._launcher_data_path
        ) as data:
            save_data = dict(data)

        # Check if the stored data matches the original data
        assert save_data == data_to_save
