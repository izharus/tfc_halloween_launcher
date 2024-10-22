"""
launcher_config.py - Minecraft Launcher Configuration Module

This module defines classes and methods for configuring the Minecraft
launcher and managing server configurations.

"""

import json
import os
from pathlib import Path
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
        DATA_DIR (Path): The directory for storing launcher data.
        SERVERS_DIR (Path): The directory where server configurations
            are stored.
        JAVA_INSTALL_URL (str): The URL for Java installation.
        MINECRAFT_LAUNCHER_IP_ADDR (str): The API URL for accessing UUID
            and access token.
        API_URL_PUSH_SKIN (str): The API URL for pushing user skin.
        API_URL_PUSH_CAPE (str): The API URL for pushing user cape.
        minecraft_skin_directory = (Path): Dir for choosing user skins.
        minecraft_cape_directory = (Path): Dir for choosing user capes.
        IS_AUTHENTICATED_KEY (str): A key for SettingsManager, 1 if user
            was authenticated, 0 otherwise

    """

    DEVELOPER_EMAIL = "ruslan.izhakovskij@gmail.com"
    LAUNCHER_NAME = "AuleCraft"
    JAVA_INSTALL_URL = "https://www.java.com/download/ie_manual.jsp"

    MINECRAFT_LAUNCHER_IP_ADDR = "http://77.239.232.50:23846/launcher"
    API_URL_PUSH_SKIN = "http://77.239.232.50:23846/push_skin"
    API_URL_PUSH_CAPE = "http://77.239.232.50:23846/push_cape"
    MAP_JSON_YOS_OBJ_KEY = "modpacks/map.json"
    BUCKET_NAME = BOTO3_BUCKET_NAME

    IS_AUTHENTICATED_KEY = "is_authenticated"  # A key for SettingsManager
    LAUNCHER_ROOT_DIR = (
        Path(
            unidecode(
                os.path.dirname(mine_lib.utils.get_minecraft_directory())
            )
        )
        / LAUNCHER_NAME
    )
    LOGGING_DIR = LAUNCHER_ROOT_DIR / "logs"
    MINECRAFT_SKIN_DIR = LAUNCHER_ROOT_DIR / "skins"
    MINECRAFT_CAPE_DIR = LAUNCHER_ROOT_DIR / "capes"

    # Directory with "assets", "runtime", "libraries", "versions"

    _GENERAL_DIR: Final = "general_libs"
    _GENERAL_DIR_NAMES: Final = [
        "assets",
        "libraries",
        "runtime",
        "versions",
    ]
    _DOWNLOADS_DIR = Path("downloads")
    _servers_data_dir: Path
    _downloads_dir: Path
    _general_lib_dir: Path

    def __init__(self):
        """
        Initialize directories and load launcher data from file if available.
        """
        self._create_launcher_dirs()
        self.set_download_dir(self.LAUNCHER_ROOT_DIR)

    def set_download_dir(self, download_path: Path) -> None:
        """Set directory for downloads."""
        self._downloads_dir = download_path / self._DOWNLOADS_DIR
        self._servers_data_dir = self._downloads_dir / "servers"
        self._general_lib_dir = self._downloads_dir / "general"

        self._downloads_dir.mkdir(parents=True, exist_ok=True)
        self._servers_data_dir.mkdir(parents=True, exist_ok=True)
        self._general_lib_dir.mkdir(parents=True, exist_ok=True)

        self._create_general_dirs()

    def _create_launcher_dirs(self):
        self.LAUNCHER_ROOT_DIR.mkdir(parents=True, exist_ok=True)
        self.LOGGING_DIR.mkdir(parents=True, exist_ok=True)
        self.MINECRAFT_SKIN_DIR.mkdir(parents=True, exist_ok=True)
        self.MINECRAFT_CAPE_DIR.mkdir(parents=True, exist_ok=True)

    def _create_general_dirs(self) -> None:
        for dirname in self._GENERAL_DIR_NAMES:
            (self._general_lib_dir / dirname).mkdir(
                parents=True,
                exist_ok=True,
            )

    def get_servers_data_dir(self, server_name: str) -> Path:
        """
        Get the directory path for the specified server's data.

        Args:
            server_name (str): The name of the server.

        Returns:
            Path: The path to the server's data directory.
        """
        return self._servers_data_dir / server_name

    def init_server_directory(self, server_data_path: Path) -> None:
        """
        Initializes the server directory by creating symbolic
        links to general directories.

        This method ensures that the specified server data path exists
        and creates symbolic links for each directory listed in
        `_GENERAL_DIR_NAMES` from the general library directory.

        Args:
            server_data_path (Path): The path to the server data directory
                where symbolic links will be created.
        """
        server_data_path.mkdir(parents=True, exist_ok=True)
        for general_dir_name in self._GENERAL_DIR_NAMES:
            src_general_path = self._general_lib_dir / general_dir_name
            dst_general_path = server_data_path / general_dir_name
            if dst_general_path.exists() and dst_general_path.is_symlink():
                dst_general_path.unlink()
            dst_general_path.symlink_to(
                src_general_path, target_is_directory=True
            )


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
        self.minecraft_directory: Final = (
            self._launcher_config.get_servers_data_dir(self.internal_name)
        )
        self._settings = settings

        self._is_minecraft_installed_key: Final = "/".join(
            [self.internal_name, "is_installed"]
        )

    @property
    def is_minecraft_installed(
        self,
    ) -> bool:
        """True if current minecraft server is installed, False otherwise."""
        if not self.minecraft_directory.exists():
            self.is_minecraft_installed = False
        self._launcher_config.init_server_directory(self.minecraft_directory)
        return bool(
            self._settings.get_user_value(self._is_minecraft_installed_key)
        )

    @is_minecraft_installed.setter
    def is_minecraft_installed(self, other: bool) -> None:
        """Change _is_minecraft_installed state for current server."""
        self._settings.set_user_value(
            self._is_minecraft_installed_key, int(other)
        )
