"""
launcher_installer.py - Minecraft Launcher Installer Module

This module provides classes and functions for configuring and installing
a Minecraft launcher, including Minecraft, Forge, mods, shaders, and
executing the Minecraft game.

Classes:
    - ServerConfig: Configuration settings for a Minecraft launcher.
    - ModDownloader: A threaded downloader for Minecraft mods from a remote
        repository.
    - InstallThread: A threaded installer for Minecraft, Forge, and mods.
    - InstallShadersThread: A threaded installer for shaders and shader packs.
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

import boto3
import boto3.exceptions
import minecraft_launcher_lib as mine_lib
from loguru import logger as log
from minecraft_launcher_lib.types import MinecraftOptions
from qtpy.QtCore import QThread, Signal

from .launcher_configs import ServerConfig
from .utility.custom_exceptions import (
    CalculateHashFailed,
    FilesSaveError,
    MinecraftLauncherConfigNotSet,
    RequestDownloadError,
)
from .utility.file_downloader import FileDownloader
from .utility.pydantic_models import FileInfo


class ModsInstaller(QThread, FileDownloader):
    """Class for save downloading and deleting unknown files"""

    def __init__(
        self,
        files_info_list: List[FileInfo],
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
            file_info.file_name
            for file_info in self.files_info_list
            if file_info.file_name.split(".")[-1] == "jar"
        )

        for _root, _directories, files in os.walk(self.mods_directory):
            for file in files:
                if file not in validate_file_names:
                    undefined_file_path = os.path.join(
                        self.mods_directory, file
                    )
                    log.info(f"Deleting unknown file: {undefined_file_path}")
                    try:
                        os.remove(undefined_file_path)
                    except Exception as error:
                        log.error(
                            "Error filed deleting the file:"
                            f"{undefined_file_path}, {error}"
                        )
                        return False
        return True

    def check_and_download(
        self,
        callback: Optional[Dict[str, Callable]] = None,
        boto3_client: Optional[boto3.client] = None,
        bucket_name: Optional[str] = None,
    ) -> bool:
        """
        Checks hash for all file in self.files_info_list and downloads
        them again if hash incorrect or if files do not exist.
        Args:
            callback (dict): A dictionary of callback functions for
            updating the UI.
            boto3_client: (Optional[boto3.client]): A boto3 client instance.
            bucket_name: (Optional[str]): A bucket name for downloading from
                object storage.
        Returns:
            bool: True if all files were deleted, False otherwise.
        """
        if callback:
            callback["setMax"](len(self.files_info_list))
            progress_bar_index = 0
        for file_info in self.files_info_list:
            file_name = file_info.file_name
            dist_file_path = file_info.dist_file_path
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
                if file_hash == file_info.hash:
                    # log.info(f"File hash correct: {file_name}")
                    continue
                log.info(f"File hash incorrect: {file_name}")
            if callback:
                callback["setStatus"](f"Downloading file: {file_name}...")
            try:
                self.save_file(
                    file_path, self.download_file_from_url(file_info.api_url)
                )
                log.info(f"File was downloaded from url: {file_name}")
                continue
            except (FilesSaveError, RequestDownloadError):
                log.error(
                    f"Failed to download file from github url: {file_name}."
                )
                if boto3_client and bucket_name:
                    try:
                        self.save_file(
                            file_path,
                            self.download_file_from_yos(
                                boto3_client,
                                bucket_name,
                                file_info.yan_obj_storage,
                            ),
                        )
                        log.info(
                            "File was downloaded from object storage: "
                            f"{file_name}"
                        )
                        continue
                    except boto3.exceptions.Boto3Error as error:
                        log.error(
                            "Failed to download file from object storage: "
                            f"{error}"
                        )
                return False

        return True


class InstallThread(QThread):
    """
    Thread for installing Minecraft, Forge, and mods.

    This class extends QThread and ServerConfig to create a
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

    progress_max = Signal("int")
    progress = Signal("int")
    text = Signal("QString")

    def __init__(self, config: Optional[ServerConfig] = None) -> None:
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

    def set_config(self, config: ServerConfig):
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

        if not self.config.is_minecraft_installed:
            mine_lib.forge.install_forge_version(
                self.config.server_config.forge_version,
                self.config.minecraft_directory,
                callback=self._callback_dict,
            )
        map_dirs = self.config.main_data
        if self.is_install_shaders:
            if "client_data_shaders" in self.config.client_additional_data:
                map_dirs += self.config.client_additional_data[
                    "client_data_shaders"
                ]
            else:
                log.error(
                    "Shaders couldn't be installed for "
                    f"{self.config.internal_name}"
                )
                self.runtime_error = True
                return

        downloader = ModsInstaller(map_dirs, self.config.minecraft_directory)
        status = downloader.check_and_download(
            callback=self._callback_dict,
            boto3_client=self.config.boto3_client,
            # pylint: disable=W0212
            bucket_name=self.config._launcher_config.BUCKET_NAME,
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

    """

    def __init__(
        self,
        nickname: str,
        uuid: str,
        access_token: str,
        config: ServerConfig,
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
        options["server"] = self.config.server_config.minecraft_server_ip
        options["port"] = self.config.server_config.minecraft_server_port
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
                self.config.server_config.minecraft_profile,
                self.config.minecraft_directory,
                self.create_launcher_options(),
            )
            # Hide the console window
            creation_flags = (
                subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            )

            with subprocess.Popen(
                minecraft_command,
                cwd=self.config.minecraft_directory,
                creationflags=creation_flags,
                # Redirect stdout to PIPE to capture output
                # stdout=subprocess.PIPE,
                # Redirect stderr to PIPE to capture error output
                stderr=subprocess.PIPE,
                universal_newlines=True,  # Use text mode for stdout/stderr
            ) as minecraft_process:
                # first var is stdout
                _, stderr = minecraft_process.communicate()
                if stderr:
                    log.error(f"Minecraft stderr: {stderr}")
                else:
                    log.debug("Minecraft stderr is empty")
        except Exception as error:
            self.runtime_error = error
            log.debug(
                "Unexpected error wile executing minecraft:\n"
                f"{traceback.format_exc()}"
            )
