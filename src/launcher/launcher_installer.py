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
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Thread
from typing import TYPE_CHECKING, Callable, List, Optional

import psutil
from loguru import logger as log
from qtpy.QtCore import QThread, Signal
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from ..minecraft_launcher_lib import minecraft_launcher_lib as mine_lib
from ..minecraft_launcher_lib.minecraft_launcher_lib.types import (
    CallbackDict,
    MinecraftOptions,
)
from .design.thread_data_utils import SettingsManager
from .launcher_configs import ServerConfig, ServerConfigManager
from .utility._helper import SUBPROCESS_CREATION_FLAGS
from .utility.custom_exceptions import (
    CalculateHashFailed,
    ConfigDownloadError,
    ConfigProcessingError,
    FileDownloadError,
    FilesSaveError,
    HashCheckFailed,
    MinecraftLauncherConfigNotSet,
)
from .utility.file_downloader import FileDownloaderProtocol, calculate_hash
from .utility.pydantic_models import AuthData, FileInfo

if TYPE_CHECKING:
    from watchdog.observers.api import BaseObserver
MAX_WORKERS = (os.cpu_count() or 4) * 4


def file_checker(
    config: ServerConfig,
    file_downloader: FileDownloaderProtocol,
):
    """
    This function waits for a short duration to ensure that the WatchDog
    service is fully initialized and then invokes the installation process
    for server files using the provided configuration and file downloader.

    Args:
        config (ServerConfig): The configuration object containing server
            file and directory information.
        file_downloader (FileDownloaderProtocol): An instance responsible for
            downloading required files.
    """

    # Just check the hash, we don't need to download file here
    def simulate_failed_download(*args, **kwargs) -> bytes:
        raise HashCheckFailed

    original_download_bytes = file_downloader.download_bytes

    # pylint: disable=C0301
    try:
        file_downloader.download_bytes = simulate_failed_download  # type: ignore
        # Wait until WatchDog starts
        time.sleep(1)
        InstallThread.install_server_files(
            config,
            file_downloader,
        )
    finally:
        file_downloader.download_bytes = original_download_bytes  # type: ignore


class RecursiveModValidator(FileSystemEventHandler):
    """
    This class extends `FileSystemEventHandler` to provide a unified handler
    for all file system events. It logs recognized events and optionally
    executes a user-defined callback function.
    """

    def __init__(
        self,
        hash_dict: dict[str, FileInfo],
        callback: Optional[Callable] = None,
    ):
        """
        Initializes the RecursiveModValidator with a hash dictionary and
        an optional callback function.

        Args:
            hash_dict (dict): A dictionary containing hashes for validation.
            callback (Optional[Callable], optional): An optional callback
                function to be executed after handling a file system event.
                Defaults to None.
        """
        self._hash_dict = hash_dict
        self.callback = callback

    def on_any_event(self, event: FileSystemEvent) -> None:
        """
        Handles all file system events by logging the event and checking
        file hashes if the event is a file modification.

        Args:
            event (FileSystemEvent): The file system event to be handled.
        """
        # Log the event with a standardized format
        log.info(
            f"Recognized operation '{event.event_type}': {event.src_path}"
        )

        # If the event is a file modification, check the file's hash
        if event.event_type == "modified":
            file_path = event.src_path

            # Retrieve the expected hash from the dictionary
            expected_hash_info = self._hash_dict.get(file_path)
            # Calculate the new hash and compare it with the expected one
            if expected_hash_info:
                try:
                    # Calculate the new hash using the same algorithm as the
                    # expected hash
                    new_hash = calculate_hash(
                        file_path,
                        hash_algorithm=expected_hash_info.hash.algorithm,
                    )

                    # If the new hash does not match the expected hash, log
                    # an error
                    if new_hash != expected_hash_info.hash.value:
                        log.error(f"Incorrect hash: {file_path}")
                    else:
                        # If the hash is correct, return without executing
                        # the callback
                        return
                except CalculateHashFailed as error:
                    # If the hash calculation fails, log an error
                    log.error(
                        f"Failed to calculate hash: {file_path}, {error}"
                    )
            else:
                # If the file is unknown, log an error
                log.error(f"Unknown file: {file_path}")

        # Execute the user-defined callback if one is provided
        if self.callback:
            self.callback()


class SecurityWorker:
    """
    Handles security-related operations for a running Minecraft server.

    This class monitors file changes in the game's directory (specifically
    in the "mods" folder) and terminates the Minecraft process if any issues
    are detected during the monitoring process.
    """

    def __init__(
        self,
        minecraft_process: subprocess.Popen,
        server_config: ServerConfig,
        file_downloader: FileDownloaderProtocol,
    ):
        """
        Initializes the SecurityWorker with the given Minecraft process
        and server configuration.

        Args:
            minecraft_process (subprocess.Popen): The running
                Minecraft process.
            server_config (ServerConfig): Configuration details
                for the Minecraft server.
            file_downloader (FileDownloaderProtocol): An instance
                responsible for downloading required files.
        """
        self._process = minecraft_process
        self._server_config = server_config
        self._file_downloader = file_downloader

    def start(self, is_need_observer: bool = True) -> None:
        """
        Starts the security worker, optionally initializing a file observer.

        This method handles the Minecraft process execution and optionally
        sets up an observer to monitor server-related file changes.

        Args:
            is_need_observer (bool): If True, starts a file observer.
                Defaults to True.
        """
        if is_need_observer:
            self._execute_observer()

        _, stderr = self._process.communicate()

        if stderr:
            log.error(f"Minecraft stderr: {stderr}")
        else:
            log.debug("Minecraft stderr is empty")

    def terminate_minecraft_process(self) -> None:
        """
        Terminates a Minecraft process gracefully, with a fallback
        to force termination.
        """
        if self._process.poll() is None:  # Check if process is still running
            log.debug("Terminating Minecraft process after timeout.")
            self._process.terminate()
            time.sleep(5)  # Give it some time to terminate gracefully
            if self._process.poll() is None:
                log.warning("Minecraft process did not terminate. Killing it.")
                self._process.kill()
        else:
            log.info("Minecraft process is not running.")

    def _create_observer(self) -> "BaseObserver":
        observer = Observer()
        hash_dict = {
            str(
                Path(self._server_config.minecraft_directory)
                / info.dist_file_path
            ): info
            for info in self._server_config.main_data
        }
        event_handler = RecursiveModValidator(
            hash_dict=hash_dict,
            callback=self.terminate_minecraft_process,
        )
        observer.schedule(
            event_handler,
            path=self._server_config.minecraft_directory / "mods",
            recursive=True,
        )
        return observer

    def _execute_observer(self) -> None:
        observer = self._create_observer()
        observer.start()

        checker_thread = Thread(
            target=file_checker,
            args=[self._server_config, self._file_downloader],
        )
        checker_thread.start()
        checker_thread.join()

        try:
            ps_process = psutil.Process(self._process.pid)
            while ps_process.is_running():
                time.sleep(1)
        except psutil.NoSuchProcess:
            log.error("Minecraft process was not found.")
        log.debug("Minecraft process stopped.")
        observer.stop()
        observer.join()


class ConfigInstallerThread(QThread):
    """QThread for installing ServerConfigManager."""

    success = Signal()
    finished = Signal()
    write_error = Signal(str)
    write_info = Signal(str)

    def __init__(
        self,
        file_downloader: FileDownloaderProtocol,
        map_json_object_key: str,
    ):

        super().__init__()
        self._config_manager: Optional[ServerConfigManager] = None
        self._file_downloader = file_downloader
        self._map_json_object_key = map_json_object_key

    def run(self):
        """Attempt to install ServerConfigManager."""
        try:
            log.info("ConfigInstallerThread stared.")
            self.write_info.emit("Загружается список серверов...")
            self._config_manager = ServerConfigManager(
                self._file_downloader,
                self._map_json_object_key,
            )
            log.info("ConfigInstallerThread completed successfully.")
            self.write_info.emit("Список серверов загружен.")
            self.success.emit()
        except ConfigProcessingError as e:
            log.critical(f"Failed to process config failed: {e}")
            self.write_error.emit("Ошибка на моей стороне )=")
        except ConfigDownloadError as e:
            log.critical(f"Failed to download a config file: {e}")
            self.write_error.emit("Обновление не удалось")
        finally:
            self.finished.emit()

    @property
    def config_manager(self) -> Optional[ServerConfigManager]:
        """Return a ServerConfigManager instance or None."""
        return self._config_manager


class ModsInstaller(QThread):
    """Class for save downloading and deleting unknown files"""

    def __init__(
        self,
        minecraft_directory: os.PathLike,
        file_downloader: FileDownloaderProtocol,
        mods_directory: str = "mods",
    ):
        QThread.__init__(self)
        self.minecraft_directory = Path(minecraft_directory)
        self.mods_directory = self.minecraft_directory / mods_directory

        self._file_downloader = file_downloader

    def delete_unknown_mods(
        self,
        files_info_list: List[FileInfo],
    ):
        """
        Deletes all files in directory 'mods' which do not exists in
        self.files_info_list.

        Args:
            files_info_list (List[FileInfo]): A list of `FileInfo` objects
                representing the valid mod files.
        Returns:
            bool: True if all files were deleted, False otherwise.
        """
        validate_file_names = list(
            file_info.file_name
            for file_info in files_info_list
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

    def delete_files(
        self,
        files_info_list: List[FileInfo],
    ):
        """
        Deletes the specified files from the Minecraft directory.

        Args:
            files_info_list (List[FileInfo]): A list of `FileInfo` objects
                representing the files to be deleted.
        """

        for fileinfo in files_info_list:
            filepath = self.minecraft_directory / fileinfo.dist_file_path
            try:
                os.remove(filepath)
                log.info(f"Optional file was deleted: {filepath}")
            except FileNotFoundError:
                continue
            except Exception as error:
                log.error(
                    "Error filed deleting the file:" f"{filepath}, {error}"
                )

    def check_and_download(
        self,
        files_info_list: List[FileInfo],
        is_skip_existing: bool = False,
        callback: Optional[CallbackDict] = None,
    ) -> bool:
        """
        Checks hash for all file in self.files_info_list and downloads
        them again if hash incorrect or if files do not exist.
        Args:
        Args:
            files_info_list (List[FileInfo]): Files to be downloaded.
            is_skip_existing (bool): If True, existing files will be skipped;
                otherwise, the file hash will be checked.
            callback (Optional[CallbackDict]): A dictionary of
                callback functions for updating the UI.
        Returns:
            bool: True if all files were deleted, False otherwise.
        """
        if callback:
            callback["setMax"](len(files_info_list))

        def install_file(file_info: FileInfo) -> None:
            file_name = file_info.file_name
            file_path = self.minecraft_directory / file_info.dist_file_path

            if is_skip_existing:
                if os.path.exists(file_path):
                    return

            if callback:
                callback["setStatus"](f"Downloading file: {file_name}...")

            self._file_downloader.download_file(
                file_info.yan_obj_storage,
                file_path,
                hash_info=file_info.hash,
            )

        count = 0
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [
                executor.submit(install_file, file_info)
                for file_info in files_info_list
            ]

            for future in futures:
                try:
                    future.result()
                except CalculateHashFailed as error:
                    log.error(f"Failed to calculate hash for: {error}.")
                    return False
                except (FileDownloadError, FilesSaveError) as error:
                    log.error(
                        "Failed to download file from object storage: "
                        f"{error}"
                    )
                    return False
                except HashCheckFailed:
                    log.error("File hash was changed due program execution.")
                    return False
                if callback:
                    count += 1
                    callback["setProgress"](count)
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

    def __init__(
        self,
        file_downloader: FileDownloaderProtocol,
        is_working: Callable[..., bool],
        config: Optional[ServerConfig] = None,
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
        self._is_working = is_working
        self.runtime_error: Optional[Exception] = None
        self._file_downloader = file_downloader

    def set_config(self, config: ServerConfig):
        """
        Set or update the configuration for the installation thread.
        """
        self.config = config

    def run(self) -> None:
        """Call main_worker an handle any exceptions."""
        self.runtime_error = None
        try:
            if not self.config:
                raise MinecraftLauncherConfigNotSet()
            self.main_worker()
            self.config.is_minecraft_installed = True
        except Exception as error:
            if self.config:
                self.config.is_minecraft_installed = False
            if self._is_working():
                log.error(
                    "Unexpected error in InstallThread thread:\n"
                    f"{traceback.format_exc()}"
                )
                self.runtime_error = error
            else:
                log.error("closeEvent was triggered, installation failed.")
                self.runtime_error = error

    @staticmethod
    def install_server_files(
        config: ServerConfig,
        file_downloader: FileDownloaderProtocol,
        callback: Optional[CallbackDict] = None,
    ):
        """
        Installs or updates the server files, ensuring necessary mods
        are downloaded and unwanted mods are removed.

        This method uses the provided configuration and downloader to:
        1. Download required mods and associated files, optionally
            using a callback for progress updates.
        2. Remove deprecated files that are no longer needed.
        3. Delete unknown or unlisted mods from the server
            directory to maintain consistency.

        Args:
            config (ServerConfig): The server configuration,
                containing file paths and mod data information.
            file_downloader (FileDownloaderProtocol): A downloader
                for retrieving necessary files.
            callback (Optional[CallbackDict]): Optional callback dictionary
                for tracking download progress.

        Returns:
            bool: True if all operations (download, deletion, and cleanup)
                were successful, False otherwise.
        """
        installer = ModsInstaller(
            minecraft_directory=config.minecraft_directory,
            file_downloader=file_downloader,
        )

        op_main_data, op_mutable_data = config.get_options(is_installed=True)
        status = installer.check_and_download(
            files_info_list=config.main_data + op_main_data,
            callback=callback,
        ) and installer.check_and_download(
            files_info_list=config.mutable_data + op_mutable_data,
            is_skip_existing=True,
            callback=callback,
        )
        if not status:
            log.error("Check_and_download operations failed.")
            return False

        del_main, _ = config.get_options(is_installed=False)
        installer.delete_files(del_main)
        status = installer.delete_unknown_mods(
            config.main_data + op_main_data + op_mutable_data
        )

        if not status:
            log.error("Delete_unknown_mods failed.")
            return False
        return True

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

        if not self.config.is_minecraft_installed:
            mine_lib.forge.install_forge_version(
                self.config.server_config.forge_version,
                self.config.minecraft_directory,
                callback=self._callback_dict,
            )

        if not self.install_server_files(
            self.config,
            self._file_downloader,
            self._callback_dict,
        ):
            self.runtime_error = True
            return
        self._callback_dict["setStatus"]("Launching minecraft...")


class MinecraftExecutorThread(QThread):
    """
    Thread for executing the Minecraft game.

    This class extends QThread. It handles the
    configuration and execution of Minecraft with a specified nickname.

    Attributes:
        auth_data (AuthData): Represents user credential data.
        server_config (ServerConfig): Current server config data.
        settings (SettingsManager): An instance of SettingsManager.
        file_downloader (FileDownloaderProtocol): A downloader
            for retrieving necessary files.
    """

    def __init__(
        self,
        auth_data: AuthData,
        server_config: ServerConfig,
        settings: SettingsManager,
        file_downloader: FileDownloaderProtocol,
    ):
        QThread.__init__(self)
        self._auth_data = auth_data
        self._config = server_config
        self._settings = settings
        self._file_downloader = file_downloader

        self.runtime_error: Optional[Exception] = None

    def create_launcher_options(
        self, allocate_ram: Optional[int] = None
    ) -> MinecraftOptions:
        """
        Create launcher options for connecting to a Minecraft server.

        This method generates and returns a dictionary of options for
        configuring the connection to a Minecraft server. It sets the
        username, server IP, and port based on the attributes of the current
        instance.

        Args:
            allocate_ram: Optional[int]: Amount of RAM in MB to allocate
                for the game.
        Returns:
            MinecraftOptions: A dictionary containing options for Minecraft
                server connection, including the username, server IP, and port.

        Note:
            The `MinecraftOptions` dictionary should be used to configure the
            connection to a Minecraft server.
        """
        options = mine_lib.utils.generate_test_options()
        options["username"] = self._auth_data.username
        options["uuid"] = self._auth_data.uuid
        options["token"] = self._auth_data.accessToken

        # auto-connect to the server:
        #  options["server"] = self._config.server_config.minecraft_server_ip
        #  options["port"] = self._config.server_config.minecraft_server_port

        if allocate_ram:
            log.debug(f"Allocating RAM: {allocate_ram}m")
            options["jvmArguments"] = [f"-Xmx{allocate_ram}m"]
        else:
            log.debug("Allocating RAM: auto")
        return options

    def run(self):
        """
        Execute the Minecraft game with the specified nickname.

        This method configures and executes the Minecraft game with the
        provided nickname. It sets the necessary options, including the
        nickname, and runs the Minecraft game.

        """
        self.runtime_error = None
        options = self.create_launcher_options(
            self._settings.get_ui_value("slider_ram_settings", int),
        )
        try:
            self._config.create_default_options()
            # options["gameDirectory"] = self.minecraft_directory
            minecraft_command = mine_lib.command.get_minecraft_command(
                self._config.server_config.minecraft_profile,
                self._config.minecraft_directory,
                options,
            )

            with subprocess.Popen(
                minecraft_command,
                cwd=self._config.minecraft_directory,
                creationflags=SUBPROCESS_CREATION_FLAGS,
                # Redirect stdout to PIPE to capture output
                # stdout=subprocess.PIPE,
                # Redirect stderr to PIPE to capture error output
                stderr=subprocess.PIPE,
                universal_newlines=True,  # Use text mode for stdout/stderr
            ) as minecraft_process:
                SecurityWorker(
                    minecraft_process,
                    self._config,
                    self._file_downloader,
                ).start()
        except Exception as error:
            self.runtime_error = error
            log.debug(
                "Unexpected error wile executing minecraft:\n"
                f"{traceback.format_exc()}"
            )
            self._config.update_default_options()
