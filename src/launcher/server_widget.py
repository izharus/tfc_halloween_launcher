"""
Server widget page. Launches specific modpack,
shows modpack description and etc.
"""

from functools import partial
from typing import Optional

from loguru import logger as log
from qtpy.QtCore import QObject, Signal, Slot
from qtpy.QtWidgets import QCheckBox, QVBoxLayout

from .design.design import Ui_MainWindow
from .design.styles import MODPACK_OPTION_CHECKBOX
from .design.thread_data_utils import SettingsManager
from .design.utility import ServerWidget, clear_layout, open_directory
from .launcher_configs import LauncherConfig, ServerConfigManager
from .utility.custom_exceptions import ModpackNotfound
from .utility.pydantic_models import Modpack, OptionData


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
        settings: SettingsManager,
    ):
        """Initializes the ServerWidgetPage.

        Args:
            config (ServerConfigManager): The configuration manager
                for server settings.
            ui_instance (Ui_MainWindow): The UI instance containing
                all UI components.
            login (str): User login.
            settings (SettingsManager): An instance of SettingsManager.
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
        self._settings = settings

        self._options_manager = ModpackOptions(
            self._settings,
            self._ui.verticalLayout_modpack_options,
        )
        for modpack in self._config.map_json.modpacks.values():
            self._options_manager.create_modpack_options_page(modpack)

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
        self._ui.pushButton_modpack_options.clicked.connect(
            self._change_modpack_options_view
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

        self._set_description_page()
        if not server_config.modpack_options:
            self._ui.pushButton_modpack_options.hide()
        else:
            self._ui.pushButton_modpack_options.show()
        self._options_manager.create_modpack_options_page(server_config)

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

    def _set_modpack_options_page(self):
        self._ui.pushButton_modpack_options.setText("Описание")
        self._ui.stackedWidget_modpack_options.setCurrentWidget(
            self._ui.page_modpack_options,
        )

    def _set_description_page(self):
        self._ui.pushButton_modpack_options.setText("Настройки")
        self._ui.stackedWidget_modpack_options.setCurrentWidget(
            self._ui.page_server_description,
        )

    def _change_modpack_options_view(self):
        curr_widget = self._ui.stackedWidget_modpack_options.currentWidget()
        if curr_widget == self._ui.page_server_description:
            self._set_modpack_options_page()
        else:
            self._set_description_page()


class ModpackOptions:
    """
    A class for managing the modpack options UI and interactions.
    """

    def __init__(
        self,
        settings: SettingsManager,
        layout: QVBoxLayout,
    ):
        """
        Initializes the ModpackOptions class.

        Args:
            settings (SettingsManager): An instance of SettingsManager for
                handling user preferences.
            layout (QVBoxLayout): A QVBoxLayout instance where modpack options
                will be displayed.
        """
        self._settings = settings
        self._layout = layout

    def create_modpack_options_page(self, modpack: Modpack):
        """
        Creates and populates the modpack options page with checkboxes
        for each modpack option.

        Args:
            modpack (Modpack): The modpack instance containing options
                to display.

        Notes:
            - Clears the existing layout before adding new checkboxes.
            - Each checkbox represents a modpack option and its current state.
        """
        clear_layout(self._layout)
        for name, option in modpack.modpack_options.items():
            object_key = option.manifest.option_key
            status = self.is_options_installed(name, option, object_key)
            button = QCheckBox()
            button.setChecked(status)
            button.setObjectName(object_key)
            button.setText(option.manifest.feature_name)
            button.setStyleSheet(MODPACK_OPTION_CHECKBOX)
            button.clicked.connect(
                partial(
                    self._change_option_status,
                    button,
                    option,
                )
            )
            self._layout.addWidget(button)
        self._layout.addStretch()

    def is_options_installed(
        self,
        option_name: str,
        option_data: OptionData,
        object_key: str,
    ) -> bool:
        """
        Checks if a specific modpack option is installed or enabled.

        Args:
            option_name (str): The name of the modpack option.
            option_data (OptionData): The data object representing
                the modpack option.
            object_key (str): The unique identifier key for the option.

        Returns:
            bool: True if the option is enabled, False otherwise.

        Notes:
            - If no value is found in settings, it uses the default value
                and updates the settings.
        """
        value = self._settings.get_user_value(object_key)
        if value is None:
            default = option_data.manifest.is_default_enabled
            log.debug(f"Option '{option_name}' is None, set to '{default}'.")
            self._settings.set_user_value(
                object_key,
                1 if default else 0,
            )
            return default
        else:
            return bool(value)

    @Slot()
    def _change_option_status(
        self,
        option_checkbox: QCheckBox,
        option_data: OptionData,
    ):
        """
        Updates the status of a modpack option when the associated
        checkbox is toggled.

        Args:
            option_checkbox (QCheckBox): The checkbox widget
                representing the modpack option.
            option_data (OptionData): The data object representing
                the modpack option.
        """
        object_name = option_checkbox.objectName()
        if option_checkbox.isChecked():
            self._settings.set_user_value(object_name, 1)
            option_data.manifest.is_default_enabled = True
            log.debug(f"'{object_name}' CHECKED TRUE.")
        else:
            self._settings.set_user_value(object_name, 0)
            option_data.manifest.is_default_enabled = False
            log.debug(f"'{object_name}' CHECKED FALSE.")
