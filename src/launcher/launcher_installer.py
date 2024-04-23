"""
launcher_installer.py - Minecraft Launcher Installer Module

This module provides classes and functions for configuring and installing
a Minecraft launcher, including Minecraft, Forge, mods, shaders, and
executing the Minecraft game.

Classes:
    - MinecraftLauncherConfig: Configuration settings for a Minecraft launcher.
    - ModDownloader: A threaded downloader for Minecraft mods from a remote
        repository.
    - InstallThread: A threaded installer for Minecraft, Forge, and mods.
    - InstallShadersThread: A threaded installer for shaders and shaderpacks.
    - MinecraftExecutorThread: A threaded executor for launching th
        Minecraft game.


Each class and function within this module serves a specific purpose in
the Minecraft launcher installation process. They handle various aspects
of the installation, configuration, and execution of Minecraft and associated
components.

The module provides essential tools and functionality for setting up and
launching a customized Minecraft environment.
"""

# pylint: disable=unnecessary-lambda
import os
import subprocess
import traceback
from typing import Callable, Dict, List, Optional

import minecraft_launcher_lib as mine_lib
from log_wizard import log as get_logger
from minecraft_launcher_lib.types import MinecraftOptions
from PyQt6.QtCore import QThread, pyqtSignal

from .launcher_configs import MinecraftLauncherConfig
from .utillity.custom_exceptions import (
    CalculateHashFailed,
    FilesSaveError,
    MinecraftLauncherConfigNotSet,
    RequestDownloadError,
)
from .utillity.file_downloader import FileDownloader

log = get_logger()


class ModsInstaller(QThread, FileDownloader):
    """Class for save downloading and deleting unknown files"""

    def __init__(
        self,
        files_info_list: List[Dict],
        minecraft_directory: str,
        mods_directory: str = "mods",
    ):
        QThread.__init__(self)
        self.files_info_list = files_info_list
        self.minecraft_directory = minecraft_directory
        self.mods_directory = os.path.join(minecraft_directory, mods_directory)

    def delete_unknown_mods(self):
        """
        Deletes all files in directory 'mods' which do not exists in
        self.files_info_list.

        Returns:
            bool: True if all files were deleted, False otherwise.
        """
        validate_file_names = list(
            file_info["file_name"]
            for file_info in self.files_info_list
            if file_info["file_name"].split(".")[-1] == "jar"
        )

        for _root, _directories, files in os.walk(self.mods_directory):
            for file in files:
                if file not in validate_file_names:
                    undifinied_file_path = os.path.join(
                        self.mods_directory, file
                    )
                    log.info(f"Deleting unknown file: {undifinied_file_path}")
                    try:
                        os.remove(undifinied_file_path)
                    except Exception as error:
                        log.error(
                            "Error filed deleting the file:"
                            f"{undifinied_file_path}, {error}"
                        )
                        return False
        return True

    def check_and_download(
        self,
        callback: Optional[Dict[str, Callable]] = None,
    ) -> bool:
        """
        Checks hash for all file in self.files_info_list and downloads
        them again if hash incorrect or if files do not exist.
        Args:
            callback (dict): A dictionary of callback functions for
            updating the UI.
        Returns:
            bool: True if all files were deleted, False otherwise.
        """
        if callback:
            callback["setMax"](len(self.files_info_list))
            progress_bar_index = 0
        for file_info in self.files_info_list:
            file_name = file_info["file_name"]
            dist_file_path = file_info["dist_file_path"]
            file_path = os.path.join(self.minecraft_directory, dist_file_path)
            if callback:
                callback["setProgress"](progress_bar_index)
                callback["setStatus"](f"Checking file hash: {file_name}...")
                progress_bar_index += 1
            if os.path.exists(file_path):
                try:
                    file_hash = self.calculate_hash(file_path)
                except CalculateHashFailed:
                    log.error(f"Failed to calculate hash for: {file_name}.")
                    return False
                if file_hash == file_info["hash"]:
                    log.info(f"File hash correct: {file_name}")
                    continue
                log.info(f"File hash incorrect: {file_name}")
            if callback:
                callback["setStatus"](f"Downloading file: {file_name}...")
            try:
                self.save_file(
                    file_path, self.download_file(file_info["api_url"])
                )
            except (FilesSaveError, RequestDownloadError):
                log.error(f"Failed to download file: {file_name}.")
                return False
        return True


class InstallThread(QThread):
    """
    Thread for installing Minecraft, Forge, and mods.

    This class extends QThread and MinecraftLauncherConfig to create a
    dedicated thread for the installation process. It manages the
    installation of Minecraft, Forge, and mods, and provides progress
    updates to the UI.

    Signals:
        progress_max (int): Signal to set the maximum progress value.
        progress (int): Signal to update the progress value.
        text (str): Signal to update the status text.

    Attributes:
        _callback_dict (dict): A dictionary of callback functions for
            updating the UI.
        is_working (bool): Flag indicating if the installation process
            is in progress.
        _is_installation_failed (bool): Flag indicating if the last
            installation failed.
    Methods:
        run(): The main method for running the installation process in the
            thread.
    """

    progress_max = pyqtSignal("int")
    progress = pyqtSignal("int")
    text = pyqtSignal("QString")

    def __init__(
        self, config: Optional[MinecraftLauncherConfig] = None
    ) -> None:
        QThread.__init__(self)
        self.config = config
        self._callback_dict = {
            "setStatus": lambda text: self.text.emit(text),
            "setMax": lambda max_progress: self.progress_max.emit(
                max_progress
            ),
            "setProgress": lambda progress: self.progress.emit(progress),
        }
        self.is_working = False
        self.runtime_error: Optional[Exception] = None
        self.is_install_shaders = False

    def change_install_shaders_status(self, is_install_shaders: bool):
        """Indicates if shaders should be installed."""
        self.is_install_shaders = is_install_shaders

    def set_config(self, config: MinecraftLauncherConfig):
        """
        Set or update the configuration for the installation thread.
        """
        self.config = config

    def run(self) -> None:
        """Call main_worker an handle any exceptions."""
        self.runtime_error = None
        try:
            self.main_worker()
        except Exception as error:
            log.error(
                "Unexpected error in InstallThread thread:\n"
                f"{traceback.format_exc()}"
            )
            self.runtime_error = error

    def main_worker(self):
        """
        Run the installation process in a separate thread.

        This method performs the installation process in a dedicated thread.
        It installs Minecraft, Forge, and mods, and provides progress updates
        to the UI.

        Raises:
            MinecraftLauncherConfigNotSet: if self.config no configured.
        Returns:
            None
        """
        if not self.config:
            raise MinecraftLauncherConfigNotSet()

        if not self.config.is_minecraft_installed():
            mine_lib.forge.install_forge_version(
                self.config.forge_version,
                self.config.minecraft_directory,
                callback=self._callback_dict,
            )
        map_dirs = self.config.map_json_data["main_data"]
        map_dirs += self.config.map_json_data["client_data"]
        if self.is_install_shaders:
            if "client_data_shaders" in self.config.map_json_data:
                map_dirs += self.config.map_json_data["client_data_shaders"]
            else:
                log.error(
                    "Shaders couldn't be installed for "
                    f"{self.config.config_name}"
                )
                self.runtime_error = True
                return

        files_data = list(
            file_data
            for file_data in map_dirs
            if file_data["install_on_client"]
        )
        downloader = ModsInstaller(files_data, self.config.minecraft_directory)
        status = downloader.check_and_download(
            callback=self._callback_dict,
        )
        if not status:
            self.runtime_error = True
        status = downloader.delete_unknown_mods()
        if not status:
            self.runtime_error = True
        self._callback_dict["setStatus"]("Launching minecraft...")


class MinecraftExecutorThread(QThread):
    """
    Thread for executing the Minecraft game.

    This class extends QThread. It handles the
    configuration and execution of Minecraft with a specified nickname.

    Attributes:
        nickname (str): The nickname to be used in the Minecraft game.
        uuid (str): The UUID of the user.
        access_token (str): User access token.

    Methods:
        is_nicnname_incorrect(nickname: str) -> bool: Check if the provided
            nickname is too short and show a message box if it doesn't meet
            the minimum length requirement.
        execute_minecraft(): Execute the Minecraft game with the specified
            nickname.

    """

    def __init__(
        self,
        nickname: str,
        uuid: str,
        access_token: str,
        config: MinecraftLauncherConfig,
    ):
        QThread.__init__(self)
        self.nickname = nickname
        self.uuid = uuid
        self.config = config
        self.access_token = access_token
        self.runtime_error: Optional[Exception] = None

    def create_launcher_options(self) -> MinecraftOptions:
        """
        Create launcher options for connecting to a Minecraft server.

        This method generates and returns a dictionary of options for
        configuring the connection to a Minecraft server. It sets the
        username, server IP, and port based on the attributes of the current
        instance.

        Returns:
            MinecraftOptions: A dictionary containing options for Minecraft
                server connection, including the username, server IP, and port.

        Note:
            The `MinecraftOptions` dictionary should be used to configure the
            connection to a Minecraft server.
        """
        options = mine_lib.utils.generate_test_options()
        options["username"] = self.nickname
        options["uuid"] = self.uuid
        options["token"] = self.access_token
        # options["server"] = self.minecraft_server_ip
        # options["port"] = self.minecraft_server_port
        return options

    def run(self):
        """
        Execute the Minecraft game with the specified nickname.

        This method configures and executes the Minecraft game with the
        provided nickname. It sets the necessary options, including the
        nickname, and runs the Minecraft game.

        """
        self.runtime_error = None
        try:
            # options["gameDirectory"] = self.minecraft_directory
            minecraft_command = mine_lib.command.get_minecraft_command(
                self.config.minecraft_profile,
                self.config.minecraft_directory,
                self.create_launcher_options(),
            )
            with subprocess.Popen(
                minecraft_command,
                cwd=self.config.minecraft_directory,
            ) as minecraft_process:
                minecraft_process.wait()  # Wait for the subprocess to complete
        except Exception as error:
            self.runtime_error = error
            log.debug(
                "Unexpected error wile executing minecraft:\n"
                f"{traceback.format_exc()}"
            )
