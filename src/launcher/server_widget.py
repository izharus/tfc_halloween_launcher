"""
Server widget page. Launches specific modpack,
shows modpack description and etc.
"""

from typing import Optional

from loguru import logger as log
from PySide6.QtCore import Slot

from .design.design import Ui_MainWindow
from .design.utility import ServerWidget
from .launcher_configs import ServerConfigManager
from .utility.custom_exceptions import ModpackNotfound


class ServerWidgetPage:
    """
    A widget page for managing server configurations.
    """

    def __init__(
        self,
        config: ServerConfigManager,
        ui_instance: Ui_MainWindow,
    ):
        """Initializes the ServerWidgetPage.

        Args:
            config (ServerConfigManager): The configuration manager
                for server settings.
            ui_instance (Ui_MainWindow): The UI instance containing
                all UI components.
        """
        super().__init__()
        self._config = config
        self._ui = ui_instance
        self._create_signals()

        # Current ServerWidget
        self._server_widget: Optional[ServerWidget] = None
        # Position of self._server_widget in last layout
        self._last_layout_pos = 0

    def _create_signals(self):
        """Sets up signal connections for UI components."""
        self._ui.pushButton_back_from_server_settings.clicked.connect(
            self.back_arrow
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
