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
import re
import subprocess
import traceback
from dataclasses import dataclass

import minecraft_launcher_lib as mine_lib
import requests
from minecraft_launcher_lib.types import MinecraftOptions
from PyQt6.QtCore import QThread, pyqtSignal


@dataclass
class MinecraftLauncherConfig:
    """
    Configuration settings for a Minecraft launcher.

    This class defines various configuration settings for a Minecraft launcher,
    including the Minecraft version, Forge version (if applicable), Minecraft
    profile, and the directory where Minecraft files are stored, with an added
    "_tfc_halloween" suffix. It also provides settings for the repository URL,
    Minecraft server IP, and Minecraft server port.

    Attributes:
        minecraft_version (str): The Minecraft version to use (e.g., "1.18.2").
        forge_version (str): The Forge version to use (e.g., "1.18.2-40.2.9").
        minecraft_profile (str): The Minecraft profile with Forge version
            (if applicable).
        minecraft_directory (str): The directory where Minecraft files are
            stored, including "_tfc_halloween".
        repo_url (str): The URL for the GitHub repository.
        minecraft_server_ip (str): The IP address of the Minecraft server.
        minecraft_server_port (str): The port number of the Minecraft server.
    """

    minecraft_version = "1.18.2"
    forge_version = "1.18.2-40.2.9"
    minecraft_profile = forge_version.replace("-", "-forge-")
    minecraft_directory = mine_lib.utils.get_minecraft_directory()
    minecraft_directory += "_tfc_halloween"
    repo_url = "https://api.github.com/repos/izharus/tfc_hallowen_modpack"
    minecraft_server_ip = "77.239.232.50"
    minecraft_server_port = "25565"
    # pylint: disable = C0301
    java_install_url = "https://www.oracle.com/java/technologies/javase/jdk17-archive-downloads.html"


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
            logging.debug(traceback.format_exc())
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
        options["server"] = self.minecraft_server_ip
        options["port"] = self.minecraft_server_port
        return options

    def run(self):
        """
        Execute the Minecraft game with the specified nickname.

        This method configures and executes the Minecraft game with the
        provided nickname. It sets the necessary options, including the
        nickname, and runs the Minecraft game.

        """

        # options["gameDirectory"] = self.minecraft_directory
        minecraft_command = mine_lib.command.get_minecraft_command(
            self.minecraft_profile,
            self.minecraft_directory,
            self.create_launcher_options(),
        )
        with subprocess.Popen(
            minecraft_command,
            cwd=self.minecraft_directory,
        ) as minecraft_process:
            minecraft_process.wait()  # Wait for the subprocess to complete


def is_java_17_or_better_installed():
    """
    Check if Java 17 or a newer version is installed on the system.

    This function runs the 'java -version' command, extracts the Java version
    from the first line of the output, and checks if it is version 17 or
    a newer version.

    Returns:
        bool: True if Java 17 or a newer version is installed, False otherwise.
    """
    try:
        # Run the 'java -version' command to check the Java version
        output = subprocess.check_output(
            ["java", "-version"],
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        first_line = output.split("\n", maxsplit=1)[0]
        version_match = re.search(r"(\d+\.\d+\.\d+)", first_line)
        if version_match:
            java_version = int(
                version_match.group(1).split(".", maxsplit=1)[0]
            )
            if java_version >= 17:
                return True

        return False
    except (subprocess.CalledProcessError, ValueError):
        return False


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
