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
    - MinecraftExecuterThread: A threaded executor for launching th
        Minecraft game.

Functions:
    - init_logging_basic_config(log_dir: str) -> None: Initialize basic
        logging configuration.

Each class and function within this module serves a specific purpose in
the Minecraft launcher installation process. They handle various aspects
of the installation, configuration, and execution of Minecraft and associated
components.

The module provides essential tools and functionality for setting up and
launching a customized Minecraft environment.
"""

# pylint: disable=unnecessary-lambda
import datetime
import logging
import os
import subprocess
from dataclasses import dataclass

import minecraft_launcher_lib as mine_lib
import requests
from PyQt6 import QtWidgets
from PyQt6.QtCore import QThread, pyqtSignal


@dataclass
class MinecraftLauncherConfig:
    """
    Configuration settings for a Minecraft launcher.

    This class defines various configuration settings such as the Minecraft
    version, Forge version, Minecraft profile, and the directory where
    Minecraft files are stored. It also appends "_imperial" to the Minecraft
    directory name.

    Attributes:
        minecraft_version (str): The Minecraft version to use (e.g., "1.18.2").
        forge_version (str): The Forge version to use (e.g., "1.18.2-40.2.9").
        minecraft_profile (str): The Minecraft profile with Forge version
            (if applicable).
        minecraft_directory (str): The directory where Minecraft files are
            stored, including "_imperial".
    """

    minecraft_version = "1.18.2"
    forge_version = "1.18.2-40.2.9"
    minecraft_profile = forge_version.replace("-", "-forge-")
    minecraft_directory = mine_lib.utils.get_minecraft_directory()
    minecraft_directory += "_imperial"
    repo_url = "https://api.github.com/repos/izharus/tfc_hallowen_modpack"


class ModDownloader(QThread, MinecraftLauncherConfig):
    """
    A class for downloading and installing Minecraft mods from a remote
    repository.

    This class inherits from QThread and MinecraftLauncherConfig to manage
    downloading and installing Minecraft mods. It provides a method,
    download_files, to fetch and install mod files from a remote repository.

    Args:
        repo_url (str): The base URL of the mod repository.

    Attributes:
        Inherits attributes from the MinecraftLauncherConfig class.

    Methods:
        download_files(callback, content_path, sub_directory="") -> bool:
            Downloads and installs mod files from the repository.

    """

    def __init__(self, repo_url):
        QThread.__init__(self)
        self.repo_url = repo_url

    def download_files(self, callback, content_path, sub_directory="") -> bool:
        """
        Download and install mod files from the repository.

        Args:
            callback (dict): A dictionary containing callback functions for
                updating the UI.
            content_path (str): The path to the mod content on the repository.
            sub_directory (str): An optional sub-directory within the
                Minecraft directory.

        Returns:
            bool: True if all mods were downloaded successfully,
                False on any error.

        This method downloads mod files from the specified content path on the
        remote repository and installs them in the specified sub-directory
        within the Minecraft directory. It provides progress updates through
        the provided callback functions.

        """
        directory = os.path.join(self.minecraft_directory, sub_directory)
        api_url = f"{self.repo_url}/{content_path}"
        try:
            logging.debug("download_files() started")
            # Create the target directory if it doesn't exist
            os.makedirs(directory, exist_ok=True)

            # Fetch the list of mod files from the GitHub repository
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            mod_files = response.json()

            # Initialize the progress bar
            total_mods = len(mod_files)
            progress = 0
            callback["setMax"](total_mods)
            callback["setProgress"](progress)

            # Download each mod file
            for mod_file in mod_files:
                file_name = mod_file["name"]
                callback["setStatus"](f"installing mode '{file_name}'...")
                download_url = mod_file["download_url"]
                file_path = os.path.join(directory, file_name)

                # Check if the file already exists
                if os.path.exists(file_path):
                    logging.info(f"Skipped: {file_name} (already downloaded)")
                else:
                    # Download the mod file
                    response = requests.get(download_url, timeout=10)
                    response.raise_for_status()

                    # Save the mod file to the specified directory
                    with open(file_path, "wb") as mod_file:
                        mod_file.write(response.content)
                    logging.info(f"Downloaded: {file_name}")

                # Update the progress
                progress += 1
                callback["setProgress"](progress)

            logging.info("All mods downloaded successfully.")
            return True
        except Exception as error:
            logging.critical(f"An error occurred: {str(error)}")
            return False

    def download_files_multiple_dirs(
        self,
        callback,
        map_dirs,
    ) -> bool:
        """
        Download and install mod files from multiple directories on the
        repository.

        Args:
            callback (dict): A dictionary containing callback functions for
                updating the UI.
            map_dirs (list of dict): A list of dictionaries where each
                dictionary contains information about the content path and
                destination sub-directory for downloading mod files.

        Returns:
            bool: True if all mods were downloaded successfully from all
                specified directories, False on any error.
        """
        for data in map_dirs:
            content_path = data["content_path"]
            sub_directory = data["dist_sub_path"]
            status = self.download_files(
                callback,
                content_path,
                sub_directory,
            )
            if not status:
                return False
        return True


class InstallThread(QThread, MinecraftLauncherConfig):
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
        is_last_install_failed(): Check if the last installation process
            failed.
        run(): The main method for running the installation process in the
            thread.
    """

    progress_max = pyqtSignal("int")
    progress = pyqtSignal("int")
    text = pyqtSignal("QString")

    def __init__(self) -> None:
        QThread.__init__(self)
        MinecraftLauncherConfig.__init__(self)
        self._callback_dict = {
            "setStatus": lambda text: self.text.emit(text),
            "setMax": lambda max_progress: self.progress_max.emit(
                max_progress
            ),
            "setProgress": lambda progress: self.progress.emit(progress),
        }
        self.is_working = False
        self._is_installation_failed: bool

    def is_last_install_failed(self):
        """
        Check if the last installation process failed.

        Returns:
            bool: True if the last installation process failed,
                False otherwise.
        """
        return self._is_installation_failed

    def run(self) -> None:
        """
        Run the installation process in a separate thread.

        This method performs the installation process in a dedicated thread.
        It installs Minecraft, Forge, and mods, and provides progress updates
        to the UI.

        Returns:
            None
        """
        self.is_working = True
        self._is_installation_failed = False
        mine_lib.forge.install_forge_version(
            self.forge_version,
            self.minecraft_directory,
            callback=self._callback_dict,
        )
        map_dirs = [
            {
                "content_path": "contents/main_data/mods",
                "dist_sub_path": "mods",
            },
            {
                "content_path": "contents/client_data/main_data/mods",
                "dist_sub_path": "mods",
            },
            {
                "content_path": "contents/client_data/main_data",
                "dist_sub_path": "",
            },
        ]

        downloader = ModDownloader(self.repo_url)

        if not downloader.download_files_multiple_dirs(
            self._callback_dict,
            map_dirs,
        ):
            self._is_installation_failed = True
            self.is_working = False
            return
        self._callback_dict["setStatus"]("Launching minecraft...")
        self.is_working = False


class InstallShadersThread(InstallThread):
    """
    Thread for installing shaders and shaderpacks.

    This class extends the InstallThread to create a dedicated thread for
    installing shaders  and shaderpacks. It manages the installation of
    shaders and shaderpacks and provides progress updates to the UI.

    Methods:
        run(): The main method for running the installation process for shaders
            and shaderpacks.
    """

    def run(self) -> None:
        self.is_working = True
        self._is_installation_failed = False

        # pylint: disable = C0301
        map_dirs = [
            {
                "content_path": "contents/client_data/additional_data/shaders_data/shaderpacks",
                "dist_sub_path": "shaderpacks",
            },
            {
                "content_path": "contents/client_data/additional_data/shaders_data/mods",
                "dist_sub_path": "mods",
            },
        ]

        downloader = ModDownloader(self.repo_url)

        if not downloader.download_files_multiple_dirs(
            self._callback_dict,
            map_dirs,
        ):
            self._is_installation_failed = True
            self.is_working = False
            return
        self._callback_dict["setStatus"]("Shaders installed...")
        self.is_working = False


class MinecraftExecuterThread(QThread, MinecraftLauncherConfig):
    """
    Thread for executing the Minecraft game.

    This class extends QThread and MinecraftLauncherConfig to create a
    dedicated thread for executing the Minecraft game. It handles the
    configuration and execution of Minecraft with a specified nickname.

    Attributes:
        nickname (str): The nickname to be used in the Minecraft game.

    Methods:
        is_nicnname_incorrect(nickname: str) -> bool: Check if the provided
            nickname is too short and show a message box if it doesn't meet
            the minimum length requirement.
        execute_minecraft(): Execute the Minecraft game with the specified
            nickname.

    """

    def __init__(self, nickname: str):
        QThread.__init__(self)
        MinecraftLauncherConfig.__init__(self)
        self.nickname = nickname

    # Define a function to show a message box
    def is_nicnname_incorrect(self, nickname: str) -> bool:
        """
        Check if the provided nickname is too short and display a warning
        message if it doesn't meet the minimum length requirement.

        Args:
            nickname (str): The nickname to be checked.

        Returns:
            bool: True if the nickname is too short, False otherwise.

        This method checks the length of the provided nickname and, if it is
        shorter than or equal to three characters, displays a warning message
        using a message box. The warning informs the user that the nickname is
        too short and suggests entering a nickname with more than five
        characters. It returns True if the nickname is too short and False
        otherwise.

        """
        if len(nickname) <= 3:
            self.input_data.change_input_edit_status(bool_stop_edit=False)
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
            msg.setText("Nickname is too short!")
            msg.setInformativeText(
                "Please enter a nickname with more than 5 characters."
            )
            msg.setWindowTitle("Nickname Length Warning")
            msg.exec()
            return True
        return False

    def execute_minecraft(self):
        """
        Execute the Minecraft game with the specified nickname.

        This method configures and executes the Minecraft game with the
        provided nickname. It sets the necessary options, including the
        nickname, and runs the Minecraft game.

        """
        if self.is_nicnname_incorrect(self.nickname):
            return
        options = mine_lib.utils.generate_test_options()
        options["username"] = self.nickname
        minecraft_command = mine_lib.command.get_minecraft_command(
            self.minecraft_profile, self.minecraft_directory, options
        )
        subprocess.run(minecraft_command, check=True)


def init_logging_basic_config(log_dir: str) -> None:
    """
    Initialize basic logging configuration.

    This function sets up basic logging configuration for logging messages to
    a log file. It creates a log directory, generates a log file name based on
    the current month and year, and configures the log file path, format, and
    logging level.

    Args:
        log_dir (str): The directory where the log file will be stored.

    Returns:
        None

    Parameters:
        - log_dir (str): The directory path for storing log files.

    The log file will include timestamps, log levels, and log messages in the
    specified format.

    Example:
    ```
    init_logging_basic_config("/path/to/log_directory")
    ```

    """
    os.makedirs(log_dir, exist_ok=True)

    # Get the current month and year
    current_month = datetime.datetime.now().strftime("%m")
    current_year = datetime.datetime.now().strftime("%Y")

    # Create the log file name using the current month and year
    log_file_name = f"{current_month}.{current_year}.log"
    # Create the full path to the log file
    log_file_path = os.path.join(log_dir, log_file_name)
    logging.basicConfig(
        filename=log_file_path,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%d.%m.%Y %H:%M:%S",
        level=logging.DEBUG,
    )
