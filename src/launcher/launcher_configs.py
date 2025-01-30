"""
launcher_config.py - Minecraft Launcher Configuration Module

This module defines classes and methods for configuring the Minecraft
launcher and managing server configurations.

"""

# pylint: disable=C0103

import json
import os
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Final, List, Optional, Tuple

import minecraft_launcher_lib as mine_lib
from loguru import logger as log
from pydantic import ValidationError
from unidecode import unidecode

from .boto3_cred import BOTO3_BUCKET_NAME
from .utility.custom_exceptions import (
    ConfigDownloadError,
    ConfigProcessingError,
    FileDownloadError,
    ModpackNotfound,
)
from .utility.file_downloader import FileDownloaderProtocol
from .utility.pydantic_models import FileInfo, MapJson, Modpack

if TYPE_CHECKING:
    from .design.thread_data_utils import SettingsManager

DEFAULT_USER_SETTINGS = "lang:ru_ru"


class URL(str):
    """
    A class representing a URL that allows for easy construction
    and manipulation of URL paths using the division operator.
    """

    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url.rstrip("/")

    def __truediv__(self, other: str):
        return URL(f"{self.base_url}/{other.lstrip('/')}")

    def __str__(self):
        return self.base_url


class BinariesObjectKey(Enum):
    """Object keys for launcher binaries."""

    WIN10X64: str = "binary/AuleCraftWin10_64bit.exe"
    WIN7X64: str = "binary/AuleCraftWin7_64bit.exe"
    WIN7X86: str = "binary/AuleCraftWin7_32bit.exe"


class LauncherConfig:
    """
    Configuration settings for the Minecraft launcher.

    Attributes:
        BASE_API_URL (str): Domain of auth service.
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

    BASE_API_URL = URL("https://auth.aulecraft.ru/")
    BASE_WEBSITE_URL = URL("https://aulecraft.ru/")

    DEVELOPER_EMAIL = "ruslan.izhakovskij@gmail.com"
    LAUNCHER_NAME = "AuleCraft"
    JAVA_INSTALL_URL = "https://www.java.com/ru/download/"

    MINECRAFT_LAUNCHER_IP_ADDR = BASE_API_URL / "launcher"
    API_URL_PUSH_SKIN = BASE_API_URL / "push_skin"
    API_URL_PUSH_CAPE = BASE_API_URL / "push_cape"
    API_URL_S3_INSTALLER_CRED = BASE_API_URL / "get_installer_s3_cred"
    REGISTER_URL = BASE_WEBSITE_URL / "register"
    RECOVERY_PWD_URL = BASE_API_URL / "reset-password-request"

    MAP_JSON_YOS_OBJ_KEY = "modpacks/map.json"
    BUCKET_NAME = BOTO3_BUCKET_NAME
    LAUNCHER_BINARIES = BinariesObjectKey

    IS_AUTHENTICATED_KEY = "is_authenticated"  # A key for SettingsManager
    LAUNCHER_ROOT_DIR = (
        Path(
            unidecode(
                os.path.dirname(mine_lib.utils.get_minecraft_directory())
            )
        )
        / f".{LAUNCHER_NAME}"
    )
    LOGGING_DIR = LAUNCHER_ROOT_DIR / "logs"
    LAUNCHER_DATA_DIR = LAUNCHER_ROOT_DIR / "data"
    MINECRAFT_SKIN_DIR = LAUNCHER_DATA_DIR / "skins"
    MINECRAFT_CAPE_DIR = LAUNCHER_DATA_DIR / "capes"
    LAUNCHER_SERVER_ICONS_DIR = LAUNCHER_DATA_DIR / "icons"

    # Path to the file with default user game settings
    DEFAULT_OPTIONS_PATH = LAUNCHER_DATA_DIR / "default_options.txt"

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
        self._create_default_options()
        self.set_download_dir(self.LAUNCHER_ROOT_DIR)

    @classmethod
    def get_icon_path(cls, filehash: str) -> Path:
        """
        Generate the icon path.

        Args:
            filehash (str): Hash of the icon file.

        Returns:
            Optional[Path]: Path where icon should be saved.
        """
        return cls.LAUNCHER_SERVER_ICONS_DIR / filehash

    @classmethod
    def get_icon_file(cls, filehash: str) -> Optional[Path]:
        """
        Get icon file path by its filehash.

        Args:
            filehash (str): Hash of the icon file.

        Returns:
            Optional[Path]: Path to the icon or None if icon not exists.
        """
        path = cls.get_icon_path(filehash)
        if path.exists():
            return path
        return None

    def set_download_dir(self, download_path: Path) -> None:
        """Set directory for downloads."""
        self._downloads_dir = download_path / self._DOWNLOADS_DIR
        self._servers_data_dir = self._downloads_dir / "servers"
        self._general_lib_dir = self._downloads_dir / "general"

        self._downloads_dir.mkdir(parents=True, exist_ok=True)
        self._servers_data_dir.mkdir(parents=True, exist_ok=True)
        self._general_lib_dir.mkdir(parents=True, exist_ok=True)

        self._create_general_dirs()

    @property
    def general_lib_dir(self) -> Path:
        """Return current path to the general libs."""
        return self._general_lib_dir

    def _create_launcher_dirs(self):
        self.LAUNCHER_ROOT_DIR.mkdir(parents=True, exist_ok=True)
        self.LOGGING_DIR.mkdir(parents=True, exist_ok=True)
        self.MINECRAFT_SKIN_DIR.mkdir(parents=True, exist_ok=True)
        self.MINECRAFT_CAPE_DIR.mkdir(parents=True, exist_ok=True)
        self.LAUNCHER_SERVER_ICONS_DIR.mkdir(parents=True, exist_ok=True)

    def _create_general_dirs(self) -> None:
        for dirname in self._GENERAL_DIR_NAMES:
            (self._general_lib_dir / dirname).mkdir(
                parents=True,
                exist_ok=True,
            )

    def _create_default_options(self) -> None:
        """Create default game options if they do not exist."""

        # Check if default options already exist
        if self.DEFAULT_OPTIONS_PATH.exists():
            log.debug("Default game settings already exist.")
            return

        options_path = (
            Path(mine_lib.utils.get_minecraft_directory()) / "options.txt"
        )
        log.debug(
            "Default game settings not found, "
            "attempting to create default options."
        )

        # Ensure the directory for default options exists
        try:
            self.DEFAULT_OPTIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            log.error(
                "Failed to create the default options directory "
                f"'{self.DEFAULT_OPTIONS_PATH.parent}': {error}"
            )
            return

        # Attempt to read user game settings from options file
        try:
            if options_path.exists():
                log.debug(f"Parsing user game settings from: {options_path}")
                content = options_path.read_text(encoding="utf-8")
                self.DEFAULT_OPTIONS_PATH.write_text(content)
                return
        except OSError as error:
            log.error(
                "Failed to read default game settings from "
                f"'{options_path}': {error}"
            )

        # If all else fails, write default user settings
        try:
            self.DEFAULT_OPTIONS_PATH.write_text(DEFAULT_USER_SETTINGS)
        except OSError as error:
            log.error(
                "Failed to create default user game settings at "
                f"'{self.DEFAULT_OPTIONS_PATH}': {error}"
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
        self._create_general_dirs()
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
        except FileDownloadError as download_error:
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

    def get_modpack(self, modpack_name: str) -> "Modpack":
        """
        Retrieves a specific modpack configuration by its name.

        Returns:
            Modpack: The modpack configuration if found,
                otherwise `None`.

        Raises:
            ModpackNotfound: If modpack was not found with the provided
                modpack name.
        """
        try:
            return self._map_json.modpacks[modpack_name]
        except KeyError as error:
            log.error(f"Modpack was not found: {modpack_name}")
            raise ModpackNotfound from error


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
        settings: "SettingsManager",
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
        self.mutable_data: Final = modpack.mutable_data
        self.modpack_options: Final = modpack.modpack_options
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
        self._launcher_config.init_server_directory(self.minecraft_directory)

        if (
            not self.minecraft_directory.exists()
            or not self._is_minecraft_profile_installed()
        ):
            self.is_minecraft_installed = False
            return False

        return bool(
            self._settings.get_user_value(self._is_minecraft_installed_key)
        )

    @is_minecraft_installed.setter
    def is_minecraft_installed(self, other: bool) -> None:
        """Change _is_minecraft_installed state for current server."""
        self._settings.set_user_value(
            self._is_minecraft_installed_key, int(other)
        )

    @property
    def minecraft_options_path(self) -> Path:
        """Return the minecraft options Path."""
        return self.minecraft_directory / "options.txt"

    def create_default_options(self) -> None:
        """Create an options for the current server."""
        if not self.minecraft_options_path.exists():
            try:
                self.minecraft_options_path.write_text(
                    self._launcher_config.DEFAULT_OPTIONS_PATH.read_text()
                )
            except OSError as error:
                log.error(
                    "Failed to create a default options "
                    f"in the server '{self.internal_name}': {error}."
                )

    def update_default_options(self) -> None:
        """Update the Minecraft options when the game is closed."""
        log.debug("Updating default minecraft options.")
        try:
            new_options = self.minecraft_options_path.read_text()
            if new_options:
                self._launcher_config.DEFAULT_OPTIONS_PATH.write_text(
                    new_options,
                )
        except OSError:
            log.error("Failed to update default minecraft options.")

    def _is_minecraft_profile_installed(self):
        profile_path = (
            self._launcher_config.general_lib_dir
            / "versions"
            / self.server_config.minecraft_profile
        )
        if profile_path.exists():
            return True
        return False

    def get_options(
        self, is_installed: bool
    ) -> Tuple[List[FileInfo], List[FileInfo]]:
        """
        Retrieves a list of file options based on their installation status.

        Args:
            is_installed (bool): A flag indicating whether to retrieve options
                that are installed (`True`) or not installed (`False`).

        Returns:
            Tuple[List[FileInfo], List[FileInfo]]: A tuple containing
                two lists:
                - `main_data`: The main data files of the selected options.
                - `mutable_data`: The mutable data files of the selected
                    options.
        """
        main_data: List[FileInfo] = []
        mutable_data: List[FileInfo] = []
        for option in self.modpack_options.values():
            if (
                self._settings.get_user_value(option.manifest.option_key)
                == is_installed
            ):
                main_data.extend(option.main_data)
                mutable_data.extend(option.mutable_data)
        return main_data, mutable_data
