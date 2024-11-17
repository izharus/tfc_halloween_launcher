"""Tests for settings_widget."""

# pylint: disable=W0212

from unittest.mock import MagicMock

from pytest_mock import MockerFixture
from src.launcher.main_window import Window
from src.launcher.settings_widget import SettingsWidget


class TestSettingsWidget:
    """Tests for SettingsWidget"""

    def test_setup_ui_initial(
        self,
        main_window: Window,
        mocker: MockerFixture,
    ):
        """
        Tests that `_setup_ui` is called exactly once during the
        initialization of the first `SettingsWidget` instance.
        """
        mock_setup_ui = MagicMock()
        mocker.patch.object(SettingsWidget, "_setup_ui", mock_setup_ui)
        main_window._settings_widget.IS_UI_INSTALLED = False

        SettingsWidget(
            main_window._ui_instance,
            main_window._launcher_config,
            main_window._settings,
        )

        mock_setup_ui.assert_called_once()

    def test_setup_ui_not_called_after_initial(
        self,
        main_window: Window,
        mocker: MockerFixture,
    ):
        """
        Tests that `_setup_ui` is not called again after the first
        `SettingsWidget` initialization, regardless of the number of
        instances created.
        """
        mock_setup_ui = MagicMock()
        mocker.patch.object(SettingsWidget, "_setup_ui", mock_setup_ui)
        main_window._settings_widget.IS_UI_INSTALLED = False

        for _ in range(10):
            SettingsWidget(
                main_window._ui_instance,
                main_window._launcher_config,
                main_window._settings,
            )

        mock_setup_ui.assert_called_once()
