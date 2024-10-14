"""Implementation of launcher choose server logic."""

from typing import List

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QLayout

from .design.design import Ui_MainWindow
from .design.utility import BaseWidget, ServerWidget, clear_layout
from .launcher_configs import ServerConfigManager


class ChoseServer(QObject, BaseWidget):
    """
    A class for choosing a server and managing server buttons.

    This class inherits from QThread and BaseWidget. It handles the
    creation of server buttons in the user interface and manages the
    communication of button clicks through signals.
    """

    launch_game = Signal(str)

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
            widget=main_window.choose_server_page,
            widget_parent=main_window.widget_main_window,
        )
        self._ui = main_window
        self._config_manager = config_manager

        self._buttons = self.update_server_buttons(self._ui.horizontalLayout_2)

    def _create_signals(self, buttons: List[ServerWidget]) -> None:
        """
        Connects button clicks to the launch_game signal.

        Args:
            buttons (List[ServerWidget]): A list of ServerWidget buttons
                to connect signals for.
        """
        for button in buttons:
            button.push_button.clicked.connect(
                lambda _, obj_name=button.objectName(): self.launch_game.emit(
                    obj_name
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
            button = ServerWidget(
                image_path=":/data/background/server-icon.png",
                title=data.server_config.display_name,
                subtitle=f"Minecraft {data.server_config.minecraft_version}",
                cur_online=15,
                max_online=30,
                parent=self._ui.scrollAreaWidgetContents,
            )
            button.setObjectName(name)
            buttons.append(button)
            self._ui.horizontalLayout_2.addWidget(button)

        self._ui.horizontalLayout_2.addStretch()

        self._create_signals(buttons)
        return buttons
