"""A QThread for loading server status and server icons."""

from concurrent.futures import ThreadPoolExecutor
from typing import List

from loguru import logger as log
from qtpy.QtCore import QThread, Signal, Slot

from .design.utility import ServerWidget
from .launcher_configs import LauncherConfig, ServerConfigManager
from .utility.custom_exceptions import (
    FileDownloadError,
    ServerQueryStatusError,
)
from .utility.file_downloader import FileDownloaderProtocol
from .utility.minecraft_query import JavaServerData


class MinecraftQueryThread(QThread):
    """
    Thread for managing server icon downloads and online player
    queries for Minecraft servers asynchronously.
    """

    set_icon = Signal(object, str)
    set_offline_status = Signal(object)
    set_online_status = Signal(object, int, int)

    def __init__(
        self,
        buttons: List[ServerWidget],
        downloader: FileDownloaderProtocol,
        config_manager: ServerConfigManager,
    ) -> None:
        """
        Initializes the MinecraftQueryThread with necessary resources.

        Args:
            buttons (List[ServerWidget]): List of server widgets to update.
            downloader (FileDownloaderProtocol): Downloader for fetching
                server icons.
            config_manager (ServerConfigManager): Configuration manager
                for server details.
        """
        super().__init__()
        self._buttons = buttons
        self._downloader = downloader
        self._config_manager = config_manager
        self._connect_signals()

    def run(self):
        """
        Executes the thread, processing icon downloads and online status
        queries.
        """
        with ThreadPoolExecutor() as executor:
            for button in self._buttons:
                for worker in (self.download_icon, self.query_online_status):
                    executor.submit(worker, button)

    def download_icon(self, button: ServerWidget) -> None:
        """
        Downloads and sets the server icon for a specific widget.

        Args:
            button (ServerWidget): The server widget for which to download
                and set the icon.

        Emits:
            set_icon (Signal): Emits the button and icon path if download
                is successful.
        """
        config = self._config_manager.get_modpack(button.config_name)
        icon_data = config.server_config.server_icon
        icon_path = LauncherConfig.get_icon_path(icon_data.hash.value)
        try:
            self._downloader.download_file(
                icon_data.yan_obj_storage,
                str(icon_path),
                hash_info=icon_data.hash,
            )
        except FileDownloadError as error:
            log.error(f"Failed to download server icon: {error}")
            return
        self.set_icon.emit(button, str(icon_path))

    def query_online_status(self, button: ServerWidget) -> None:
        """
        Queries the server for current online players and sets status.

        Args:
            button (ServerWidget): The server widget for which to query
                the online status.

        Emits:
            set_online_status (Signal): Emits button, current online, and max
                online if query is successful.
            set_offline_status (Signal): Emits button if server query fails.
        """
        config = self._config_manager.get_modpack(button.config_name)
        server = JavaServerData(config.server_config)
        try:
            cur_online, max_online = server.fetch_players()
            self.set_online_status.emit(
                button,
                cur_online,
                max_online,
            )
            log.info(
                f"Players fetched for '{button.config_name}'': "
                f"{cur_online}/{max_online}"
            )
        except ServerQueryStatusError as error:
            log.debug(
                f"Failed to fetch players for '{button.config_name}': {error}"
            )
            self.set_offline_status.emit(button)

    def _connect_signals(self):
        """Connect all signals."""
        self.set_icon.connect(self._set_icon_to_server_widget)
        self.set_offline_status.connect(self._set_widget_offline)
        self.set_online_status.connect(self._set_widget_online)

    @Slot(object, str)
    def _set_icon_to_server_widget(self, widget: ServerWidget, icon_path: str):
        """
        Sets the icon for the server widget.

        Args:
            widget (ServerWidget): The server widget to update.
            icon_path (str): The path to the server icon image.
        """
        widget.set_image(icon_path)

    @Slot(object)
    def _set_widget_offline(self, widget: ServerWidget):
        """
        Updates the server widget to show an offline status.

        Args:
            widget (ServerWidget): The server widget to set as offline.
        """
        widget.set_offline_label()

    @Slot(object, int, int)
    def _set_widget_online(
        self, widget: ServerWidget, cur_online: int, max_online: int
    ):
        """
        Updates the server widget to show the online player count.

        Args:
            widget (ServerWidget): The server widget to update.
            cur_online (int): The current number of online players.
            max_online (int): The maximum number of players allowed.
        """
        widget.set_online_label(cur_online, max_online)
