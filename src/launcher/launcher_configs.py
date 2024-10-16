"""
launcher_config.py - Minecraft Launcher Configuration Module

This module defines classes and methods for configuring the Minecraft
launcher and managing server configurations.

"""

import json
import os
from typing import Final, Optional

import minecraft_launcher_lib as mine_lib
from loguru import logger as log
from pydantic import ValidationError
from unidecode import unidecode

from .boto3_cred import BOTO3_BUCKET_NAME
from .design.thread_data_utils import SettingsManager
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
        DEVELOPER_EMAIL (str): Complain about bugs here.
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
        IS_AUTHENTICATED_KEY (str): A key for SettingsManager, 1 if user
            was authenticated, 0 otherwise

    """

    DEVELOPER_EMAIL = "ruslan.izhakovskij@gmail.com"
    LAUNCHER_NAME = "tfc_halloween"
    DATA_DIR = "halloween_data"
    SERVERS_DIR = "servers"
    JAVA_INSTALL_URL = "https://www.java.com/download/ie_manual.jsp"
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

        self._logging_dir = os.path.join(
            self._minecraft_root_directory, self.DATA_DIR, "logs"
        )
        os.makedirs(self._logging_dir, exist_ok=True)
        self._minecraft_skin_directory = os.path.join(
            self.minecraft_root_directory,
            "skins",
        )
        self._minecraft_cape_directory = os.path.join(
            self.minecraft_root_directory,
            "capes",
        )

    @property
    def minecraft_root_directory(self) -> str:
        """Get the Minecraft root directory."""
        return self._minecraft_root_directory

    @property
    def logging_dir(self) -> str:
        """Get the logging directory."""
        return self._logging_dir

    @property
    def minecraft_skin_directory(self) -> str:
        """Get the directory with user skins."""
        return self._minecraft_skin_directory

    @property
    def minecraft_cape_directory(self) -> str:
        """Get the directory with user capes."""
        return self._minecraft_cape_directory


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


class ServerConfig:
    """
    Represents a Minecraft server configuration.
    """

    # pylint: disable=R0902
    def __init__(
        self,
        internal_name: str,
        modpack: Modpack,
        launcher_config: LauncherConfig,
        settings: SettingsManager,
    ):
        """
        Initializes the ServerConfig instance.

        Args:
            internal_name (str): Internal name for current config.
            modpack (Modpack): An instance of Modpack class with modpack data.
            modpack_data (Dict): Configuration data for the modpack.
            launcher_config (LauncherConfig): The launcher configuration.
        """
        self.main_data: Final = modpack.main_data
        self.client_additional_data: Final = modpack.client_additional_data
        self.server_config: Final = modpack.server_config
        self.internal_name: Final = internal_name
        self._launcher_config = launcher_config
        self.minecraft_directory: Final = self._generate_minecraft_directory()
        self._settings = settings

        self._is_minecraft_installed_key: Final = "/".join(
            [self.internal_name, "is_installed"]
        )

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
    def is_minecraft_installed(
        self,
    ) -> bool:
        """True if current minecraft server is installed, False otherwise."""
        return bool(
            self._settings.get_user_value(self._is_minecraft_installed_key)
        )

    @is_minecraft_installed.setter
    def is_minecraft_installed(self, other: bool) -> None:
        """Change _is_minecraft_installed state for current server."""
        self._settings.set_user_value(
            self._is_minecraft_installed_key, int(other)
        )
