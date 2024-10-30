"""A simple launcher for auto updating of main launcher."""
import json
import os
import platform
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

import requests
from loguru import logger as log
from src.launcher.launcher_configs import BinariesObjectKey, LauncherConfig
from src.launcher.utility._helper import init_loguru_logger
from src.launcher.utility.custom_exceptions import (
    DownloadServerHandshakeError,
    FileDownloadError,
)
from src.launcher.utility.file_downloader import (
    DownloadProgress,
    FileYOSDownloader,
)
from src.launcher.utility.path_manager import PathManager
from src.launcher.utility.pydantic_models import HashInfo, S3Credentials

launcher_config = LauncherConfig()
LAUNCHER_BINARY_PATH = (
    launcher_config.LAUNCHER_ROOT_DIR / f"{launcher_config.LAUNCHER_NAME}.exe"
)


def get_binary_download_key() -> Optional[BinariesObjectKey]:
    """
    Determines the appropriate download key for the current
    Windows platform.

    Returns:
        Optional[BinariesObjectKey]: The corresponding BinariesObjectKey
            based on the platform.
    """
    if not platform.win32_is_iot() and not platform.system() == "Windows":
        log.error(f"Platform not supported: {platform.version()}")
        return None  # or consider raising an exception

    platform_info = platform.win32_ver()
    log.debug(f"Platform: {platform_info}")

    version = platform_info[0]
    is_64_bit = sys.maxsize > 2**32

    if is_64_bit:
        log.debug("64-bit system recognized.")
        if version in ("6.1", "6.2", "6.3"):
            return BinariesObjectKey.WIN7X64
        else:
            return BinariesObjectKey.WIN10X64
    else:
        log.debug("32-bit system recognized.")
        return BinariesObjectKey.WIN7X86


class DownloaderApp:
    """A simple download application using Tkinter."""

    def __init__(self, root: tk.Tk):
        """Initializes the DownloaderApp.

        Sets up the main window, application title, icon, and progress bar.

        Args:
            root (tk.Tk): The root window of the application.
        """
        self.root = root
        self.root.title("Загрузчик")
        self.root.resizable(False, False)

        self.path_manager = PathManager(os.getcwd())
        icon_file_path = self.path_manager.get_current_root_path("icon.ico")
        self.root.iconbitmap(icon_file_path)

        self.progress_bar = ttk.Progressbar(
            root, orient="horizontal", length=280, mode="determinate"
        )
        self.progress_bar.pack()
        self._is_installation_complete = False
        binary_key = get_binary_download_key()
        if not binary_key:
            platform_string = f"{platform.system()} | {platform.version()}"
            log.critical(f"Platform not supported: {platform_string}.")
            messagebox.showerror(
                "Ошибка",
                f"Платформа не поддерживается: {platform_string}",
            )
            self.root.destroy()
            sys.exit(1)
        try:
            response = requests.get(
                launcher_config.API_URL_S3_INSTALLER_CRED, timeout=3
            )
            response.raise_for_status()
        except requests.RequestException as error:
            log.critical(f"Failed to receive connection settings: {error}")
            messagebox.showerror(
                "Ошибка",
                "Сервер недоступен.",
            )
            sys.exit(1)
        try:
            credential = S3Credentials.model_validate(
                json.loads(response.content)
            )
        except json.JSONDecodeError as error:
            log.critical(f"Unable to decode server response: {error}")
            messagebox.showerror(
                "Ошибка",
                "Не удалось обработать ответ от сервера.",
            )
            sys.exit(1)
        try:
            self.file_downloader = FileYOSDownloader(credential)
        except DownloadServerHandshakeError as error:
            log.critical(f"Handshake error: {repr(error)}")
            messagebox.showerror(
                "Ошибка",
                "Сервер отверг подключение.",
            )
            sys.exit(1)
        self.start_download(binary_key)

    def start_download(self, binary_key: BinariesObjectKey):
        """
        Initiates the download process and updates the progress bar.

        Args:
            binary_key (BinariesObjectKey): The key representing the binary
                to be downloaded.
        """
        self.progress_bar["value"] = 0

        callback = DownloadProgress(self.set_current, self.set_maximum)
        self.thread = threading.Thread(
            target=self.install,
            args=(
                binary_key,
                callback,
            ),
            daemon=True,
        )
        self.thread.start()
        self.root.after(100, self.wait_download)

    def install(
        self, binary_key: BinariesObjectKey, callback: DownloadProgress
    ):
        """
        Handles the installation of the binary file by downloading it and
        updating the provided progress callback.

        Args:
            binary_key (BinariesObjectKey): The key representing the binary
                to be downloaded.
            callback (DownloadProgress): A callback instance used to update
                the progress bar during the download process.
        """
        log.debug(f"Binary object key: {binary_key.value}")
        # Загружаем файл и передаем callback для обновления прогресса

        try:
            hash_info = HashInfo(
                value=self.file_downloader.get_hash(binary_key.value),
                algorithm="md5",
            )
            self.file_downloader.download_file(
                binary_key.value,
                LAUNCHER_BINARY_PATH,
                hash_info=hash_info,
                callback=callback,
            )
        except FileDownloadError as error:
            log.critical(f"Failed to download launcher: {repr(error)}")
            return
        self._is_installation_complete = True

    def wait_download(self):
        """
        Waits for a download thread to complete and then launches
        the main application.
        """
        if self.thread.is_alive():
            self.root.after(100, self.wait_download)
        elif self._is_installation_complete:
            self.root.withdraw()
            try:
                subprocess.run(LAUNCHER_BINARY_PATH, check=True)
            except Exception as error:
                log.critical(f"Failed to launch main app: {error}")
                messagebox.showerror("Ошибка", "Не удалось запустить лаунчер.")
            finally:
                self.root.destroy()
                sys.exit()
        else:
            log.critical("Failed to install launcher.")
            messagebox.showerror("Ошибка", "Не удалось установить лаунчер.")
            self.root.destroy()
            sys.exit(1)

    def set_maximum(self, maximum: int) -> None:
        """Set the maximum value of the progress bar.

        Args:
            maximum (int): The maximum value for the progress bar.
        """
        self.progress_bar["maximum"] = maximum

    def set_current(self, current: int) -> None:
        """Set the current progress value of the progress bar.

        Args:
            current (int): The current progress value.
        """
        self.progress_bar["value"] = current


def main():
    """Main entry point."""
    init_loguru_logger(launcher_config.LOGGING_DIR)
    root = tk.Tk()
    root.eval("tk::PlaceWindow . center")
    DownloaderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
