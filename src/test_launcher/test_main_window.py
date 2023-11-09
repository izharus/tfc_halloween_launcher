"""Tests for mainw qt Window class."""
import sys

from PyQt6 import QtWidgets
from src.launcher.launcher_configs import SUPPORTED_CONFIGS, get_config
from src.launcher.main_window import Window


def test_combobox_server_type_and_supported_configs_do_not_match():
    """SUPPORTED_CONFIGS should fully matches with text in ui element."""
    with QtWidgets.QApplication(sys.argv):
        window = Window()
        for config_name in SUPPORTED_CONFIGS:
            assert window.input_data.extract_element(config_name) is not False

        # pylint: disable = W0212
        q_combobox = window._ui_instance.comboBox_server_type

        all_items = [q_combobox.itemText(i) for i in range(q_combobox.count())]
        assert len(all_items) == 2

        for q_combobox in all_items:
            get_config(q_combobox)
