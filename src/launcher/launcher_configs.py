"""
launcher_config.py - Minecraft Launcher Configuration Module

This module defines classes and methods for configuring the Minecraft
launcher and managing server configurations.

"""
import json
import os
import shelve
import traceback
from dataclasses import dataclass
from typing import Callable, Dict, Optional

import minecraft_launcher_lib as mine_lib
from log_wizard import DefaultConfig
from log_wizard import log as get_logger

from .utillity.file_downloader import FileDownloader


# pylint: disable = R0903
class LauncherConfig:
    """
    Configuration settings for the Minecraft launcher.

    Attributes:
        launcher_name (str): The name of the Minecraft launcher.
        minecraft_root_directory (str): The root directory for
            Minecraft installations.
        logging_dir (str): The directory where log files are stored.
        servers_directory (str): The directory where server
            configurations are stored.
        data_dir (str): The directory for only launcher files, like logs or
            input_data in intpus.
        launcher_data (str): Path to file with launcher data. There could
            stores information about installed servers, for an example.
        ui_data_path (str): Here launcher stores data from frontend inputs.
        java_install_url (str): The URL for Java installation.
        launcher_stored_data (Dict): A dict with saved configuration
            variables from file.
        minecraft_launcher_ip_addr (str): api url from web_server for uuid and
            access_token
    """

    launcher_name: str = "tfc_halloween"
    minecraft_root_directory: str = mine_lib.utils.get_minecraft_directory()
    minecraft_root_directory += f"_{launcher_name}"

    data_dir: str = "halloween_data"
    ui_data_path: str = os.path.join(
        minecraft_root_directory,
        data_dir,
        "ui_inputs_data\\input_data",
    )
    launcher_data: str = os.path.join(
        minecraft_root_directory, data_dir, "launcher_data.bin"
    )
    logging_dir: str = os.path.join(minecraft_root_directory, data_dir, "logs")
    servers_directory: str = "servers"
    java_install_url: str = "https://java-for-minecraft.com/ru/"
    minecraft_launcher_ip_addr: str = "http://77.239.232.50:23846/launcher"
    launcher_stored_data: Dict = {}


DefaultConfig(log_dir=LauncherConfig.logging_dir)
log = get_logger()


# pylint: disable= R0902
@dataclass
class MinecraftLauncherConfig(LauncherConfig):
    """
    Configuration settings for the Minecraft launcher, including
    specific Minecraft server configurations.

    Note:
        Call get_stored_data() to load stored data from the file.
    Attributes:
        config_name (str): The name of the launcher configuration.
        minecraft_version (str): The version of Minecraft to be used.
        forge_version (str): The version of Forge to be used.
        minecraft_directory (str): The directory where Minecraft is installed.
        minecraft_profile (str): The Minecraft profile to be used.
        minecraft_server_ip (str): The IP address of the Minecraft server.
        minecraft_server_port (str): The port of the Minecraft server.
        minecraft_java_version (str): The Java version to use.
        repo_url (str): The URL for the GitHub repository where
            mods are stored.
        map_json_url (str): Url for downloading map file. It stores
            config for installing all modpacks.
        map_json_data Optional[Dict]: main info about all modpacks files.
            Should be installed before all functions calls.

    """

    config_name: str
    minecraft_version: str
    forge_version: str
    minecraft_directory: str
    minecraft_profile: str
    minecraft_server_ip: str
    minecraft_server_port: str
    minecraft_java_version: int
    map_json_url: str
    map_json_data: Optional[Dict] = None

    def parse_map_json_data(self):
        """Download map.json file from backend repo."""
        self.map_json_data = json.loads(
            FileDownloader.download_file(self.map_json_url)
        )[self.config_name]

    def is_minecraft_installed(
        self,
    ) -> bool:
        """
        Check in mineraft has already installed for current config profile.
        """
        return self.launcher_stored_data.get(
            f"{self.config_name}_is_installed", False
        )

    def set_minecraft_installed(self) -> None:
        """
        Set minecraft installed flag for this current profile.
        """
        field = f"{self.config_name}_is_installed"
        self.launcher_stored_data[field] = True
        self._update_stored_data()

    def get_stored_data(self) -> None:
        """
        Get stored data from the file.
        """
        try:
            with shelve.open(self.launcher_data) as launcher_data:
                self.launcher_stored_data = launcher_data["stored_data"]
        except Exception as error:
            log.error(f"Failed to get stored_data: {error}")
            log.debug(traceback.format_exc)

    def _update_stored_data(self) -> None:
        """
        Update stored data in the file.
        """
        try:
            with shelve.open(self.launcher_data) as launcher_data:
                launcher_data["stored_data"] = self.launcher_stored_data
        except Exception as error:
            log.error(f"Failed to update stored_data: {error}")
            log.debug(traceback.format_exc)


def get_terra_firma_craft_config() -> MinecraftLauncherConfig:
    """
    Get the configuration for the Terra Firma Craft Minecraft server.

    Returns:
        MinecraftLauncherConfig: The configuration for the Terra
            Firma Craft server.

    """
    config_name = "terrafirmacraft"
    minecraft_directory = MinecraftLauncherConfig.minecraft_root_directory
    terra_firma_craft_config = MinecraftLauncherConfig(
        config_name=config_name,
        minecraft_version="1.18.2",
        forge_version="1.18.2-40.2.9",
        minecraft_directory=minecraft_directory,
        minecraft_profile="1.18.2-forge-40.2.9",
        minecraft_server_ip="77.239.232.50",
        minecraft_server_port="25565",
        minecraft_java_version=17,
        # pylint: disable = C0301
        map_json_url="https://raw.githubusercontent.com/izharus/hallowen_modpacks/main/map.json",
    )
    terra_firma_craft_config.parse_map_json_data()
    return terra_firma_craft_config


def get_terra_firma_craft_test_config() -> MinecraftLauncherConfig:
    """
    Get the configuration for the Terra Firma Craft Test Minecraft server.

    Returns:
        MinecraftLauncherConfig: The configuration for the Terra
            Firma Craft Test server.

    """
    config_name = "terrafirmacraft_test"
    minecraft_directory = os.path.join(
        MinecraftLauncherConfig.minecraft_root_directory,
        MinecraftLauncherConfig.servers_directory,
        config_name,
    )
    terra_firma_craft_config = MinecraftLauncherConfig(
        config_name="terrafirmacraft_test",
        minecraft_version="1.18.2",
        forge_version="1.18.2-40.2.9",
        minecraft_directory=minecraft_directory,
        minecraft_profile="1.18.2-forge-40.2.9",
        minecraft_server_ip="77.239.232.50",
        minecraft_server_port="25570",
        minecraft_java_version=17,
        # pylint: disable = C0301
        map_json_url="https://raw.githubusercontent.com/izharus/hallowen_modpacks/main/map.json",
    )
    terra_firma_craft_config.parse_map_json_data()
    return terra_firma_craft_config


def get_config(config_name: str) -> Callable[[], MinecraftLauncherConfig]:
    """
    Get the launcher configuration based on the specified name.

    Args:
        config_name (str): The name of the configuration to retrieve.

    Returns:
        MinecraftLauncherConfig: The specified launcher configuration function.


    """
    try:
        return SUPPORTED_CONFIGS[config_name]
    except KeyError:
        default_config = list(SUPPORTED_CONFIGS.values())[0]
        log.error(f"Unknown config name: {config_name}")
        log.error(f"Setting default config: {default_config}")
        return default_config


SUPPORTED_CONFIGS = {
    "TFC Halloween": get_terra_firma_craft_config,
    "TFC Halloween TEST": get_terra_firma_craft_test_config,
}
