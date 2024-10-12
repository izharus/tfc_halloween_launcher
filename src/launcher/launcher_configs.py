"""
launcher_config.py - Minecraft Launcher Configuration Module

This module defines classes and methods for configuring the Minecraft
launcher and managing server configurations.

"""

import json
import os
import shelve
import traceback
from typing import Any, Dict, Optional

import minecraft_launcher_lib as mine_lib
from loguru import logger as log
from pydantic import ValidationError
from unidecode import unidecode

from .boto3_cred import BOTO3_BUCKET_NAME
from .utility.custom_exceptions import (
    ConfigDownloadError,
    ConfigProcessingError,
    FiletDownloadError,
)
from .utility.file_downloader import FileDownloaderProtocol
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
        _minecraft_root_directory = (
            mine_lib.utils.get_minecraft_directory() + f"_{self.LAUNCHER_NAME}"
        )
        log.info(
            "Original minecraft_root_directory: "
            f"{_minecraft_root_directory}"
        )
        self._minecraft_root_directory = unidecode(_minecraft_root_directory)
        log.info(
            "Current minecraft_root_directory: "
            f"{self._minecraft_root_directory}"
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


class ServerConfigManager:
    """
    Manages server configurations, including downloading, validating,
    and retrieving modpack data.
    """

    def __init__(
        self,
        file_downloader: FileDownloaderProtocol,
        map_object_key: str,
    ):
        """
        Initializes the ConfigGetter instance.

        Args:
            file_downloader (FileDownloaderProtocol): An instance of the class
                for downloading files.
            map_object_key (str): An object key of map.json in object_storage

        Raises:
            ConfigProcessingError: If the config_data fails
                Pydantic validation.
            ConfigDownloadError: If failed to download config.
        """

        self._file_downloader = file_downloader
        self._object_key = map_object_key
        self._map_json: MapJson

        self.update_config()

    def update_config(self):
        """
        Downloads and validates the configuration map JSON.

        Downloads the file specified by the launcher config key, validates it
        using the `MapJson` Pydantic model, and stores the validated data.

        Raises:
            ConfigDownloadError: If the file download fails.
            ConfigProcessingError: If the file contents are invalid JSON or
                                fail validation.
        """
        try:
            bytes_file_data = self._file_downloader.download_bytes(
                self._object_key,
            )
            self._map_json = MapJson.model_validate(
                json.loads(bytes_file_data)
            )
        except FiletDownloadError as download_error:
            log.error(f"Failed to download file for key: {self._object_key}")
            raise ConfigDownloadError from download_error
        except json.JSONDecodeError as json_error:
            log.error(
                "Invalid JSON received for key "
                f"'{self._object_key}': {json_error}"
            )
            raise ConfigProcessingError("Invalid JSON format.") from json_error
        except ValidationError as validation_error:
            log.error(f"Validation failed for map JSON: {validation_error}")
            raise ConfigProcessingError from validation_error

    @property
    def map_json(self) -> "MapJson":
        """
        Returns the `MapJson` object containing
        the configuration of all servers.

        Returns:
            MapJson: An MapJson instance with server configuration data.
        """
        return self._map_json

    def get_config(self, config_name: str) -> Optional["Modpack"]:
        """
        Retrieves a specific modpack configuration by its name.

        Returns:
            Optional[Modpack]: The modpack configuration if found,
                otherwise `None`.
        """
        return self._map_json.modpacks.get(config_name, None)


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
