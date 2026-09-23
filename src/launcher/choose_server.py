"""Implementation of launcher choose server logic."""

from functools import partial
from typing import List

from loguru import logger as log
from qtpy.QtCore import Signal
from qtpy.QtWidgets import QLayout

from .design.design import Ui_MainWindow
from .design.utility import BaseWidget, ServerWidget, clear_layout
from .launcher_configs import LauncherConfig, ServerConfigManager
from .utility.custom_exceptions import ModpackNotfound


class ChoseServer(BaseWidget):
    """
    A class for choosing a server and managing server buttons.

    This class inherits from QThread and BaseWidget. It handles the
    creation of server buttons in the user interface and manages the
    communication of button clicks through signals.
    """

    launch_game = Signal(str)
    switch_to_server_page = Signal(str, object)

    def __init__(
        self, main_window: Ui_MainWindow, config_manager: ServerConfigManager
    ):
        """Initializes the ChoseServer class.

        Args:
            main_window (Ui_MainWindow): The main window UI instance.
            config_manager (ServerConfigManager): The configuration manager
                for the server settings.
        """
        super().__init__(
            widget=main_window.stackedWidget,
            parent_widget=main_window.widget_main_window_child,
        )
        self._ui = main_window
        self._config_manager = config_manager

        self._buttons = self.update_server_buttons(self._ui.horizontalLayout_2)

    @property
    def server_buttons(self) -> List[ServerWidget]:
        """Return all ServerWidget instances."""
        return self._buttons

    def _create_signals(self, buttons: List[ServerWidget]) -> None:
        """
        Connects signals from the provided list of ServerWidget buttons
        to their respective slots.

        Args:
            buttons (List[ServerWidget]): A list of ServerWidget instances
                containing buttons to connect signals for.
        """
        for button in buttons:
            button.push_button.clicked.connect(
                partial(self.launch_game.emit, button.objectName())
            )
            button.clicked.connect(
                partial(
                    self.switch_to_server_page.emit,
                    button.objectName(),
                    button,
                )
            )

    def update_server_buttons(self, layout: QLayout) -> List[ServerWidget]:
        """
        Updates the server buttons in the specified layout.

        Clears the existing layout and creates new ServerWidget buttons
        based on the server configuration.

        Args:
            layout (QLayout): The layout to update with new server buttons.

        Returns:
            List[ServerWidget]: A list of created ServerWidget buttons.
        """
        clear_layout(layout)
        buttons = []
        for name, data in self._config_manager.map_json.modpacks.items():
            try:
                modpack = self._config_manager.get_modpack(name)
            except ModpackNotfound:
                log.critical(f"Modpack name no found: '{name}'")
                continue
            icon_image = LauncherConfig.get_icon_file(
                modpack.server_config.server_icon.hash.value
            )
            button = ServerWidget(
                config_name=name,
                title=data.server_config.display_name,
                subtitle=f"Minecraft {data.server_config.vanilla_version}",
                parent=self._ui.scrollAreaWidgetContents,
                image=icon_image,
            )
            buttons.append(button)
            self._ui.horizontalLayout_2.addWidget(button)

        self._ui.horizontalLayout_2.addStretch()

        self._create_signals(buttons)
        return buttons
