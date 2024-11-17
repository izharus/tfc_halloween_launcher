"""
Server widget page. Launches specific modpack,
shows modpack description and etc.
"""

from typing import Optional

from loguru import logger as log
from qtpy.QtCore import QObject, Signal, Slot

from .design.design import Ui_MainWindow
from .design.utility import ServerWidget, open_directory
from .launcher_configs import LauncherConfig, ServerConfigManager
from .utility.custom_exceptions import ModpackNotfound


class ServerWidgetPage(QObject):
    """
    A widget page for managing server configurations.
    """

    check_game_files = Signal(str)

    def __init__(
        self,
        config: ServerConfigManager,
        ui_instance: Ui_MainWindow,
        login: str,
    ):
        """Initializes the ServerWidgetPage.

        Args:
            config (ServerConfigManager): The configuration manager
                for server settings.
            ui_instance (Ui_MainWindow): The UI instance containing
                all UI components.
            login (str): User login.
        """
        super().__init__()
        self._config = config
        self._ui = ui_instance
        self._create_signals()

        # Current ServerWidget
        self._server_widget: Optional[ServerWidget] = None
        # Position of self._server_widget in last layout
        self._last_layout_pos = 0
        self._ui.label_player_name.setText(login)

    def _create_signals(self):
        """Sets up signal connections for UI components."""
        self._ui.pushButton_back_from_server_settings.clicked.connect(
            self.back_arrow
        )
        self._ui.pushButton_check_server_files.clicked.connect(
            self._restore_server_files
        )
        self._ui.pushButton_open_modpack_dir.clicked.connect(
            self._open_current_modpack_dir
        )

    @Slot()
    def back_arrow(self):
        """
        Handles the action for the back button.

        This method inserts the current server widget back into the layout and
        switches the stacked widget to the choose server page.
        """
        self._ui.horizontalLayout_2.insertWidget(
            self._last_layout_pos, self._server_widget
        )
        self._ui.stackedWidget.setCurrentWidget(self._ui.choose_server_page)
        self._server_widget = None

    @Slot(str, object)
    def switch_to_server_page(
        self,
        modpack_name: str,
        widget: ServerWidget,
    ):
        """
        Switches to the specified server settings page.

        Args:
            modpack_name (str): The name of the modpack.
                to switch to.
            widget (ServerWidget): The ServerWidget instance
                to be displayed.
        """
        if self._server_widget == widget:
            return
        try:
            server_config = self._config.get_modpack(modpack_name)
        except ModpackNotfound:
            log.critical(
                f"Failed to switch page to the modpack: {modpack_name}"
            )
            return

        self._ui.stackedWidget.setCurrentWidget(self._ui.server_settings_page)
        self._ui.label_server_description.setWordWrap(True)
        self._ui.label_server_description.setText(
            server_config.server_config.description
        )
        self._last_layout_pos = self._ui.horizontalLayout_2.indexOf(widget)
        self._server_widget = widget
        self._ui.gridLayout.addWidget(widget)

    @Slot(str)
    def _restore_server_files(self):
        """Start the process of checking game files."""

        modpack_name = self._server_widget.config_name
        log.debug(f"Check files started for: {modpack_name}")
        self.check_game_files.emit(modpack_name)

    @Slot()
    def _open_current_modpack_dir(self):
        """Open the directory of current server."""

        modpack_name = self._server_widget.config_name
        modpack_dir = LauncherConfig().get_servers_data_dir(modpack_name)
        if modpack_dir.exists():
            open_directory(str(modpack_dir))
