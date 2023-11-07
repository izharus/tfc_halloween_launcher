"""
launcher_config.py - Minecraft Launcher Configuration Module

This module defines classes and methods for configuring the Minecraft
launcher and managing server configurations.

"""
import logging
import os
from dataclasses import dataclass

import minecraft_launcher_lib as mine_lib

from .utillity.custom_exceptions import UndefinedMinecraftLauncherConfig


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
    """

    launcher_name: str = "tfc_halloween"
    minecraft_root_directory: str = mine_lib.utils.get_minecraft_directory()
    minecraft_root_directory += f"_{launcher_name}"
    logging_dir: str = os.path.join(minecraft_root_directory, "logs")
    servers_directory: str = "servers"


# pylint: disable= R0902
@dataclass
class MinecraftLauncherConfig(LauncherConfig):
    """
    Configuration settings for the Minecraft launcher, including
    specific Minecraft server configurations.

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
        java_install_url (str): The URL for Java installation.

    """

    config_name: str
    minecraft_version: str
    forge_version: str
    minecraft_directory: str
    minecraft_profile: str
    minecraft_server_ip: str
    minecraft_server_port: str
    minecraft_java_version: int
    repo_url: str
    java_install_url: str


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
        repo_url="https://api.github.com/repos/izharus/tfc_hallowen_modpack",
        # pylint: disable = C0301
        java_install_url="https://www.oracle.com/java/technologies/javase/jdk17-archive-downloads.html",
    )
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
        repo_url="https://api.github.com/repos/izharus/tfc_hallowen_modpack",
        # pylint: disable = C0301
        java_install_url="https://www.oracle.com/java/technologies/javase/jdk17-archive-downloads.html",
    )
    return terra_firma_craft_config


def get_config(config_name: str):
    """
    Get the launcher configuration based on the specified name.

    Args:
        config_name (str): The name of the configuration to retrieve.

    Returns:
        MinecraftLauncherConfig: The specified launcher configuration.

    Raises:
        UndefinedMinecraftLauncherConfig: If the specified
            configuration is undefined.

    """
    try:
        return SUPPORTED_CONFIGS[config_name]
    except IndexError as error:
        logging.critical("get_config(): couldn't get launcher config")
        raise UndefinedMinecraftLauncherConfig() from error


SUPPORTED_CONFIGS = {
    "terrafirmacraft": get_terra_firma_craft_config(),
    "terrafirmacraft_test": get_terra_firma_craft_test_config(),
}
