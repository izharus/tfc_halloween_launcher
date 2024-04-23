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
from log_wizard import log as get_logger

from .utillity.custom_exceptions import (
    ConfigProcessingError,
    RequestDownloadError,
)
from .utillity.file_downloader import FileDownloader


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
    """

    LAUNCHER_NAME = "tfc_halloween"
    DATA_DIR = "halloween_data"
    SERVERS_DIR = "servers"
    JAVA_INSTALL_URL = "https://java-for-minecraft.com/ru/"
    MINECRAFT_LAUNCHER_IP_ADDR = "http://77.239.232.50:23846/launcher"
    API_URL_PUSH_SKIN = "http://77.239.232.50:23846/push_skin"
    API_URL_PUSH_CAPE = "http://77.239.232.50:23846/push_cape"
    MAP_JSON_URL = "https://raw.githubusercontent.com/izharus/hallowen_modpacks/dev/map.json" # pylint: disable=C0301
    MAP_JSON_YOS_KEY = "modpacks/map.json"

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


# DefaultConfig(log_dir=LauncherConfig.logging_dir)
log = get_logger()


class ConfigLoader:
    """A class for loading and handling configuration data."""

    def __init__(
        self, config_data: Dict, launcher_config: LauncherConfig
    ) -> None:
        """
        Initialize ConfigLoader with provided configuration data.

        Parameters:
            config_data (Dict): A dictionary containing configuration data.
            launcher_config (LauncherConfig): An instance of LauncherConfig
                containing launcher settings.
        """
        self._config_data = config_data
        self._launcher_config = launcher_config

    def __eq__(self, other):
        if isinstance(other, ConfigLoader):
            return set(self.config_list) == set(other.config_list)
        return False

    @staticmethod
    def _pars_bytes_config(
        bytes_file_data: bytes,
    ) -> Dict:
        try:
            config = json.loads(bytes_file_data)
        except Exception as error:
            log.error(f"Failed to load json from config file: {error}")
            log.debug(traceback.format_exc())
            raise ConfigProcessingError from error
        if not isinstance(config, dict):
            log.error("Incorrect config format.")
            raise ConfigProcessingError
        return config

    @classmethod
    def download_from_url(
        cls, launcher_config: LauncherConfig
    ) -> "ConfigLoader":
        """
        Download configuration data from a specified URL.

        Parameters:
            launcher_config (LauncherConfig): An instance of LauncherConfig
                containing launcher settings.

        Returns:
            ConfigLoader: A ConfigLoader instance.

        Raises:
            RequestDownloadError: If the download request for the config
                fails.
            ConfigProcessingError: If an error occurs while processing
                the configuration data.
        """
        try:
            bytes_file_data = FileDownloader.download_file(
                launcher_config.MAP_JSON_URL
            )
        except RequestDownloadError:
            log.error("Failed to load a config file.")
            raise
        return cls(
            cls._pars_bytes_config(bytes_file_data),
            launcher_config,
        )
        try:
            config = json.loads(bytes_file_data)
        except Exception as error:
            log.error(f"Failed to load json from config file: {error}")
            log.debug(traceback.format_exc())
            raise ConfigProcessingError from error
        if not isinstance(config, dict):
            log.error("Incorrect config format.")
            raise ConfigProcessingError
        return cls(config, launcher_config)

    @property
    def config_list(self) -> List[str]:
        """
        Get a list of all supported configurations.

        Returns:
            List[str]: A list of strings representing supported
                configuration names.
        """
        return list(key for key in self._config_data)

    def get_config(self, config_name: str) -> "MinecraftLauncherConfig":
        """
        Get the configuration data for a specified configuration name.

        Parameters:
            config_name (str): The name of the configuration to retrieve.

        Returns:
            MinecraftLauncherConfig: An instance of MinecraftLauncherConfig
                containing the configuration data.

        Raises:
            ConfigProcessingError: If the specified configuration name is
                not found in the loaded data.
        """
        if config_name not in self._config_data:
            raise ConfigProcessingError(
                f"config name: '{config_name}' was not found"
            )
        return MinecraftLauncherConfig(
            self._config_data[config_name], self._launcher_config
        )


class MinecraftLauncherConfig:
    """
    Configuration settings for the Minecraft launcher, including
    specific Minecraft server configurations.

    Note:
        Call get_stored_data() to load stored data from the file.
    Attributes:


        minecraft_directory (str): The directory where Minecraft is installed.
        minecraft_skin_directory (str): The directory with skins.
        minecraft_cape_directory (str): The directory with capes.
        minecraft_java_version (str): The Java version to use.
        repo_url (str): The URL for the GitHub repository where
            mods are stored.


    """

    minecraft_skin_directory: str
    minecraft_cape_directory: str

    def __init__(
        self,
        map_json_data,
        launcher_config: LauncherConfig,
    ):
        self._launcher_config = launcher_config
        self.map_json_data = map_json_data
        self._minecraft_directory = os.path.join(
            self._launcher_config.minecraft_root_directory,
            self._launcher_config.SERVERS_DIR,
            self.config_name,
        )
        self.minecraft_skin_directory = os.path.join(
            self._launcher_config.minecraft_root_directory,
            "skins",
        )
        self.minecraft_cape_directory = os.path.join(
            self._launcher_config.minecraft_root_directory,
            "capes",
        )

    def __eq__(self, other):
        if isinstance(other, MinecraftLauncherConfig):
            return self.map_json_data == other.map_json_data
        return False

    def _get_config_value(self, key: str, default: Any = "") -> Any:
        """
        Helper method to get a value from the 'config' sub-dictionary
        in 'map_json_data'.
        """
        if self.map_json_data and "config" in self.map_json_data:
            return self.map_json_data["config"].get(key, default)
        log.error("Failed to parse param from config: {key}")
        return default

    @property
    def config_name(self) -> str:
        """The name of the launcher configuration."""
        return self._get_config_value("config_name")

    @property
    def minecraft_version(self) -> str:
        """minecraft_version (str): The version of Minecraft to be used."""
        return self._get_config_value("minecraft_version")

    @property
    def forge_version(self) -> str:
        """forge_version (str): The version of Forge to be used."""
        return self._get_config_value("forge_version")

    @property
    def minecraft_profile(self):
        """The Minecraft profile to be used."""
        return self._get_config_value("minecraft_profile")

    @property
    def minecraft_server_ip(self) -> str:
        """The IP address of the Minecraft server."""
        return self._get_config_value("minecraft_server_ip")

    @property
    def minecraft_server_port(self) -> str:
        """The port of the Minecraft server."""
        return self._get_config_value("minecraft_server_port")

    @property
    def minecraft_directory(self) -> str:
        """The minecraft directory for current config."""
        return self._minecraft_directory

    def is_minecraft_installed(
        self,
    ) -> bool:
        """
        Check in minecraft has already installed for current config profile.
        """
        return bool(
            self._launcher_config.get_launcher_data_value(
                f"{self.config_name}_is_installed"
            )
        )

    def set_minecraft_installed(self, is_installed: bool = True) -> None:
        """
        Set minecraft installed flag for this current profile.
        """
        key = f"{self.config_name}_is_installed"
        self._launcher_config.set_launcher_data_value(key, is_installed)
