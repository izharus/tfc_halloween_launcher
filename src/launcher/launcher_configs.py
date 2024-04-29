"""
launcher_config.py - Minecraft Launcher Configuration Module

This module defines classes and methods for configuring the Minecraft
launcher and managing server configurations.

"""
import json
import os
import shelve
import traceback
from typing import Any, Dict, List, Optional

import boto3
import boto3.exceptions
import minecraft_launcher_lib as mine_lib
from loguru import logger as log
from src.launcher.boto3_cred import BOTO3_ACCESS_KEY, BOTO3_SECRET_KEY

from .boto3_cred import BOTO3_BUCKET_NAME
from .utility.custom_exceptions import (
    ConfigDownloadError,
    ConfigProcessingError,
    RequestDownloadError,
)
from .utility.file_downloader import FileDownloader
from .utility.pydantic_models import MapJson, Modpack


class LauncherConfig:
    """
    Configuration settings for the Minecraft launcher.

    Attributes:
        LAUNCHER_NAME (str): The name of the Minecraft launcher.
        DATA_DIR (str): The directory for storing launcher data.
        SERVERS_DIR (str): The directory where server configurations
            are stored.
        JAVA_INSTALL_URL (str): The URL for Java installation.
        MINECRAFT_LAUNCHER_IP_ADDR (str): The API URL for accessing UUID
            and access token.
        API_URL_PUSH_SKIN (str): The API URL for pushing user skin.
        API_URL_PUSH_CAPE (str): The API URL for pushing user cape.
        minecraft_skin_directory = (str): Dir for choosing user skins.
        minecraft_cape_directory = (str): Dir for choosing user capes.
    """

    LAUNCHER_NAME = "tfc_halloween"
    DATA_DIR = "halloween_data"
    SERVERS_DIR = "servers"
    JAVA_INSTALL_URL = "https://java-for-minecraft.com/ru/"
    MINECRAFT_LAUNCHER_IP_ADDR = "http://77.239.232.50:23846/launcher"
    API_URL_PUSH_SKIN = "http://77.239.232.50:23846/push_skin"
    API_URL_PUSH_CAPE = "http://77.239.232.50:23846/push_cape"
    MAP_JSON_URL = "https://raw.githubusercontent.com/izharus/hallowen_modpacks/main/map.json"  # pylint: disable=C0301
    MAP_JSON_YOS_OBJ_KEY = "modpacks/map.json"
    BUCKET_NAME = BOTO3_BUCKET_NAME

    def __init__(self):
        """
        Initialize directories and load launcher data from file if available.
        """
        self._minecraft_root_directory = (
            mine_lib.utils.get_minecraft_directory() + f"_{self.LAUNCHER_NAME}"
        )
        os.makedirs(self._minecraft_root_directory, exist_ok=True)
        self._ui_data_path = os.path.join(
            self._minecraft_root_directory,
            self.DATA_DIR,
            "ui_inputs_data",
            "input_data",
        )
        os.makedirs(os.path.dirname(self._ui_data_path), exist_ok=True)
        self._launcher_data_path = os.path.join(
            self._minecraft_root_directory, self.DATA_DIR, "launcher_data.bin"
        )

        self._logging_dir = os.path.join(
            self._minecraft_root_directory, self.DATA_DIR, "logs"
        )
        os.makedirs(self._logging_dir, exist_ok=True)
        self._launcher_data = self._get_launcher_data()
        self.minecraft_skin_directory = os.path.join(
            self.minecraft_root_directory,
            "skins",
        )
        self.minecraft_cape_directory = os.path.join(
            self.minecraft_root_directory,
            "capes",
        )

    @property
    def minecraft_root_directory(self) -> str:
        """
        Get the Minecraft root directory.
        """

        return self._minecraft_root_directory

    @property
    def ui_data_path(self) -> str:
        """
        Get the UI data path.
        """

        return self._ui_data_path

    @property
    def launcher_data_path(self) -> str:
        """Get the path to the launcher data file."""

        return self._launcher_data_path

    @property
    def logging_dir(self) -> str:
        """
        Get the logging directory.
        """

        return self._logging_dir

    @property
    def launcher_data(self) -> Dict:
        """Get the launcher data."""
        return self._launcher_data

    def set_launcher_data_value(
        self,
        data_key: str,
        data_value: Any,
    ) -> None:
        """
        Set a value in the launcher data.

        Args:
            data_key: The key of the data to set.
            data_value: The value to set.
        """
        self._launcher_data[data_key] = data_value
        self._update_launcher_data()

    def get_launcher_data_value(
        self,
        data_key: str,
    ) -> Any:
        """
        Get a value from the launcher data.

        Args:
            data_key: The key of the data to get.
        """
        value = self._launcher_data.get(data_key, None)
        if not value:
            log.debug(f"Failed to get '{data_key}' from launcher_data.")
        return value

    def _get_launcher_data(self) -> Dict:
        """
        Get launcher data from the file.

        Returns:
            dict: The launcher data.
        """
        try:
            with shelve.open(self._launcher_data_path) as launcher_data:
                return dict(launcher_data)
        except Exception as error:
            log.error(f"Failed to get launcher_data: {error}")
            log.debug(traceback.format_exc)
            return {}

    def _update_launcher_data(self) -> None:
        """
        Update launcher data in the file.
        """
        try:
            with shelve.open(self._launcher_data_path) as launcher_data:
                launcher_data.update(self._launcher_data)
        except Exception as error:
            log.error(f"Failed to update launcher_data: {error}")
            log.debug(traceback.format_exc)


class ConfigLoader:
    """
    A class for loading modpacks configuration data.

    Args:
        launcher_config (LauncherConfig): An instance of LauncherConfig
            containing configuration parameters.
    """

    def __init__(self, launcher_config: LauncherConfig) -> None:
        """
        Initializes the ConfigLoader instance.

        Args:
            launcher_config (LauncherConfig): An instance of LauncherConfig
                containing modpacks configuration parameters.
        """
        self._boto3_client: Optional[boto3.client] = None
        self._install_boto3_instance()
        self._launcher_config = launcher_config

    def _install_boto3_instance(self):
        """
        Install boto3 client instance if not already installed.
        """
        if not self._boto3_client:
            try:
                self._boto3_client = boto3.client(
                    "s3",
                    endpoint_url="https://storage.yandexcloud.net",
                    aws_access_key_id=BOTO3_ACCESS_KEY,
                    aws_secret_access_key=BOTO3_SECRET_KEY,
                )
            except boto3.exceptions.Boto3Error as error:
                log.error(f"Failed to create an s3 instance: {error}")

    @property
    def boto3_client(self) -> Optional[boto3.client]:
        """
        Returns the boto3 client instance.

        Returns:
            Optional[boto3.client]: The boto3 client instance.
        """
        self._install_boto3_instance()
        return self._boto3_client

    @staticmethod
    def _create_model_from_bytes(
        bytes_file_data: bytes,
    ) -> Dict:
        """
        Creates a MapJson model instance from bytes file data.

        Args:
            bytes_file_data (bytes): The bytes file data containing JSON data.

        Returns:
            Dict: A Dict with the modpack config.

        Raises:
            ConfigProcessingError: If there is an error processing
                the configuration data.
        """
        try:
            config = json.loads(bytes_file_data)
        except Exception as error:
            log.error(f"Failed to load json from config file: {error}")
            raise ConfigProcessingError from error
        return config

    def get_from_url(
        self,
    ) -> Dict:
        """
        Retrieves configuration data from a URL.

        Returns:
            Dict: A Dict with the modpack config.

        Raises:
            ConfigProcessingError: If there is an error
                processing the configuration data.
        """
        try:
            bytes_file_data = FileDownloader.download_file_from_url(
                self._launcher_config.MAP_JSON_URL
            )
        except RequestDownloadError as error:
            log.error("Failed to load a config file.")
            raise ConfigDownloadError from error
        return self._create_model_from_bytes(bytes_file_data)

    def get_from_yos(
        self,
    ) -> Dict:
        """
        Retrieves configuration data from YOS (Yandex Object Storage).

        Returns:
            Dict: A Dict with the modpack config.

        Raises:
            ConfigProcessingError: If there is an error processing
                the configuration data.
        """
        self._install_boto3_instance()
        if not self._boto3_client:
            log.error("Failed, boto3_client is None.")
            raise ConfigDownloadError()
        try:
            bytes_file_data = FileDownloader.download_file_from_yos(
                self._boto3_client,
                self._launcher_config.BUCKET_NAME,
                self._launcher_config.MAP_JSON_YOS_OBJ_KEY,
            )
        except RequestDownloadError as error:
            log.error(f"Failed to load a config file. {error}")
            raise ConfigDownloadError from error
        return self._create_model_from_bytes(bytes_file_data)


class ConfigGetter:
    """
    A class for managing server configurations.

    Attributes:
        _launcher_config (LauncherConfig): The launcher configuration.
        _modpacks_configs (Dict): A dictionary of modpack configurations.
        _active_config_display_name (str): The name of the active modpack
            configuration.
    """

    def __init__(
        self,
        config_data: Dict,
        launcher_config: LauncherConfig,
        boto3_client: Optional[boto3.client] = None,
    ):
        """
        Initializes the ConfigGetter instance.

        Args:
            config_data (Dict): Configuration data for the server.
            launcher_config (LauncherConfig): The launcher configuration.
            boto3_client: (Optional[boto3.client]): A boto3 client instance.

        Raises:
            ValidationError: If the config_data fails Pydantic validation.
        """
        self._launcher_config = launcher_config
        map_json = MapJson(**config_data)
        self._modpacks_configs = config_data["modpacks"]

        self._display_names_list = list(
            config.server_config.display_name
            for config in map_json.modpacks.values()
        )
        self._active_config_display_name: str = self._display_names_list[0]
        self._configs_map = dict(
            zip(self._display_names_list, map_json.modpacks.keys())
        )
        self._boto3_client = boto3_client

    @property
    def active(self) -> "ServerConfig":
        """
        Returns the active server configuration.

        Returns:
            ServerConfig: The active server configuration.
        """
        return ServerConfig(
            self._configs_map[self._active_config_display_name],
            self._modpacks_configs[
                self._configs_map[self._active_config_display_name]
            ],
            self._launcher_config,
            boto3_client=self._boto3_client,
        )

    @property
    def config_list(self) -> List[str]:
        """
        Returns the list of available server configurations.

        Returns:
            List[str]: The list of available server configurations.
        """
        return list(self._display_names_list)

    def set_active(self, display_name: str) -> bool:
        """
        Sets the active server configuration.

        Args:
            display_name (str): The name of the configuration to set as active.

        Returns:
            bool: True if the configuration was successfully set
                as active, False otherwise.
        """
        if display_name in self._configs_map:
            self._active_config_display_name = display_name
            return True
        return False


class ServerConfig(Modpack):
    """
    Represents a Minecraft server configuration.

    Inherits from Modpack.

    Attributes:
        _launcher_config (LauncherConfig): The launcher configuration.
        _minecraft_directory (str): The directory where Minecraft server
            data is stored.
        internal_name (str): Internal name for current config.
    """

    internal_name: str

    def __init__(
        self,
        internal_name: str,
        modpack_data: Dict,
        launcher_config: LauncherConfig,
        boto3_client: Optional[boto3.client] = None,
    ):
        """
        Initializes the ServerConfig instance.

        Args:
            internal_name (str): Internal name for current config.
            modpack_data (Dict): Configuration data for the modpack.
            launcher_config (LauncherConfig): The launcher configuration.
        """
        super().__init__(**modpack_data, internal_name=internal_name)
        self._launcher_config = launcher_config
        self._minecraft_directory = self._generate_minecraft_directory()
        self._boto3_client = boto3_client

    @property
    def boto3_client(self) -> Optional[boto3.client]:
        """Return a boto3_client instance if it exists."""
        return self._boto3_client

    def _generate_minecraft_directory(self) -> str:
        """
        Generates the Minecraft directory based on the active configuration.

        Returns:
            str: The Minecraft directory.
        """
        return os.path.join(
            self._launcher_config.minecraft_root_directory,
            self._launcher_config.SERVERS_DIR,
            self.internal_name,
        )

    @property
    def minecraft_directory(self) -> str:
        """
        Returns the Minecraft directory for the current configuration.

        Returns:
            str: The Minecraft directory.
        """
        return self._minecraft_directory

    @property
    def is_minecraft_installed(
        self,
    ) -> bool:
        """
        Checks if Minecraft is already installed for the current configuration.

        Returns:
            bool: True if Minecraft is installed, False otherwise.
        """
        return bool(
            self._launcher_config.get_launcher_data_value(
                f"{self.internal_name}_is_installed"
            )
        )

    @is_minecraft_installed.setter
    def is_minecraft_installed(self, other: bool) -> None:
        """
        Sets the flag indicating whether Minecraft is installed
        for the current configuration.

        Args:
            other (bool, optional): The value to set for the flag.
        """
        key = f"{self.internal_name}_is_installed"
        self._launcher_config.set_launcher_data_value(key, other)
