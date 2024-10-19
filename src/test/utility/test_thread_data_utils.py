"""Module with tests for src.launcher.design.thread_data_utils."""

# pylint: disable=R0903,W0621,W0212,W0613,E0401

import pytest
from qtpy.QtCore import QSettings
from qtpy.QtWidgets import (
    QCheckBox,
    QComboBox,
    QLineEdit,
    QRadioButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from src.launcher.design.thread_data_utils import SettingsManager
from src.launcher.utility.custom_exceptions import WidgetNotFound


class MockMainWindow(QWidget):
    """A mocked QMainWindow for tests."""

    def __init__(self):
        super().__init__()
        self.line_edit = QLineEdit()
        self.line_edit.setObjectName("line_edit")

        self.text_edit = QTextEdit()
        self.text_edit.setObjectName("text_edit")

        self.spin_box = QSpinBox()
        self.spin_box.setObjectName("spin_box")

        self.check_box = QCheckBox()
        self.check_box.setObjectName("check_box")

        self.combo_box = QComboBox()
        self.combo_box.setObjectName("combo_box")

        self.radio_button = QRadioButton()
        self.radio_button.setObjectName("radio_button")

        layout = QVBoxLayout()
        layout.addWidget(self.line_edit)
        layout.addWidget(self.text_edit)
        layout.addWidget(self.spin_box)
        layout.addWidget(self.check_box)
        layout.addWidget(self.combo_box)
        layout.addWidget(self.radio_button)
        self.setLayout(layout)


@pytest.fixture()
def widget(qtbot) -> MockMainWindow:
    """Mock widget."""
    return MockMainWindow()


# pylint: disable=W0201
class TestSettingsManager:
    """Unit tests for SettingsManage."""

    @classmethod
    def setup_class(cls):
        """Setup for TestSettingsManager."""
        cls.company_name = "IzharusTest"
        cls.app_name = "TestApp"

    def setup_method(self):
        """Clean existing settings."""
        self.settings = QSettings(self.company_name, self.app_name)
        self.settings.clear()

    def test__setup_settings_loading_valid_line_edit(self, widget):
        """
        Tests '_setup_settings' when settings contain a valid type
        for line_edit. The value from the settings should be applied
        to the UI element.
        """
        expected_value = "new_line_edit_text"
        settings = SettingsManager(widget, settings=self.settings)

        # Set a valid value in the settings for line_edit
        settings._settings.set_value(
            settings._get_ui_key(widget.line_edit.objectName()), expected_value
        )

        settings._setup_settings()

        # Assert that value from settings is applied to UI element
        assert widget.line_edit.text() == expected_value

    def test__setup_settings_loading_invalid_type_line_edit(self, widget):
        """
        Tests '_setup_settings' when settings contain an invalid type
        for line_edit. The default value from the UI element should
        be saved to the settings.
        """
        line_edit_text = "line_edit_text"
        widget.line_edit.setText(line_edit_text)

        settings = SettingsManager(widget, settings=self.settings)

        # Simulate invalid setting type for line_edit
        settings._settings.set_value(
            settings._get_ui_key(widget.line_edit.objectName()), 123
        )

        settings._setup_settings()

        # Assert that default value from UI element is loaded
        assert (
            settings.get_ui_value(widget.line_edit.objectName())
            == line_edit_text
        )

    def test__setup_settings_loading_valid_text_edit(self, widget):
        """
        Tests '_setup_settings' when settings contain a valid type
        for text_edit. The value from the settings should be applied
        to the UI element.
        """
        expected_value = "new_text_edit_text"
        settings = SettingsManager(widget, settings=self.settings)

        # Set a valid value in the settings for text_edit
        settings._settings.set_value(
            settings._get_ui_key(widget.text_edit.objectName()), expected_value
        )

        settings._setup_settings()

        # Assert that value from settings is applied to UI element
        assert widget.text_edit.toPlainText() == expected_value

    def test__setup_settings_loading_invalid_type_text_edit(self, widget):
        """
        Tests '_setup_settings' when settings contain an invalid type
        for text_edit. The default value from the UI element should
        be saved to the settings.
        """
        text_edit_text = "text_edit_text"
        widget.text_edit.setText(text_edit_text)

        settings = SettingsManager(widget, settings=self.settings)

        # Simulate invalid setting type for text_edit
        settings._settings.set_value(
            settings._get_ui_key(widget.text_edit.objectName()), 3466
        )

        settings._setup_settings()

        # Assert that default value from UI element is loaded
        assert (
            settings.get_ui_value(widget.text_edit.objectName())
            == text_edit_text
        )

    def test__setup_settings_loading_valid_spin_box(self, widget):
        """
        Tests '_setup_settings' when settings contain a valid type
        for spin_box. The value from the settings should be applied
        to the UI element.
        """
        expected_value = 20
        settings = SettingsManager(widget, settings=self.settings)

        # Set a valid value in the settings for spin_box
        settings._settings.set_value(
            settings._get_ui_key(widget.spin_box.objectName()), expected_value
        )

        settings._setup_settings()

        # Assert that value from settings is applied to UI element
        assert widget.spin_box.value() == expected_value

    def test__setup_settings_loading_invalid_type_spin_box(self, widget):
        """
        Tests '_setup_settings' when settings contain an invalid type
        for spin_box. The default value from the UI element should
        be saved to the settings.
        """
        spin_box_val = 10
        widget.spin_box.setValue(spin_box_val)

        settings = SettingsManager(widget, settings=self.settings)

        # Simulate invalid setting type for spin_box
        settings._settings.set_value(
            settings._get_ui_key(widget.spin_box.objectName()), "invalid"
        )

        settings._setup_settings()

        # Assert that default value from UI element is loaded
        assert (
            settings.get_ui_value(widget.spin_box.objectName()) == spin_box_val
        )

    def test__setup_settings_loading_valid_check_box(self, widget):
        """
        Tests '_setup_settings' when settings contain a valid type
        for check_box. The value from the settings should be applied
        to the UI element.
        """
        expected_value = 1
        settings = SettingsManager(widget, settings=self.settings)

        # Set a valid value in the settings for check_box
        settings._settings.set_value(
            settings._get_ui_key(widget.check_box.objectName()), expected_value
        )

        settings._setup_settings()

        # Assert that value from settings is applied to UI element
        assert widget.check_box.isChecked() == expected_value

    def test__setup_settings_loading_invalid_type_check_box(self, widget):
        """
        Tests '_setup_settings' when settings contain an invalid type
        for check_box. The default value from the UI element should
        be saved to the settings.
        """
        check_box_state = 0
        widget.check_box.setChecked(check_box_state)

        settings = SettingsManager(widget, settings=self.settings)

        # Simulate invalid setting type for check_box
        settings._settings.set_value(
            settings._get_ui_key(widget.check_box.objectName()), "invalid"
        )

        settings._setup_settings()

        # Assert that default value from UI element is loaded
        assert (
            settings.get_ui_value(widget.check_box.objectName())
            == check_box_state
        )

    def test__setup_settings_loading_valid_combo_box(self, widget):
        """
        Tests '_setup_settings' when settings contain a valid index
        for combo_box. The value from the settings should be applied
        to the UI element.
        """
        combo_box_lines = ["test1", "test2"]
        expected_index = 1
        widget.combo_box.addItems(combo_box_lines)

        settings = SettingsManager(widget, settings=self.settings)

        # Set a valid index in the settings for combo_box
        settings._settings.set_value(
            settings._get_ui_key(widget.combo_box.objectName()), expected_index
        )

        settings._setup_settings()

        # Assert that value from settings is applied to UI element
        assert widget.combo_box.currentIndex() == expected_index

    def test__setup_settings_loading_invalid_type_combo_box(self, widget):
        """
        Tests '_setup_settings' when settings contain an invalid index
        for combo_box.
        The default value from the UI element should be saved to the settings.
        """
        combo_box_lines = ["test1", "test2"]
        combo_box_index = 1
        widget.combo_box.addItems(combo_box_lines)
        widget.combo_box.setCurrentIndex(combo_box_index)

        settings = SettingsManager(widget, settings=self.settings)

        # Simulate invalid setting (index out of bounds) for combo_box
        settings._settings.set_value(
            settings._get_ui_key(widget.combo_box.objectName()),
            "invalid_index",
        )

        settings._setup_settings()

        # Assert that default value from UI element is loaded
        assert (
            settings.get_ui_value(widget.combo_box.objectName())
            == combo_box_index
        )

    def test__setup_settings_loading_valid_radio_button(self, widget):
        """
        Tests '_setup_settings' when settings contain a valid type
        for radio_button. The value from the settings should be applied
        to the UI element.
        """
        expected_value = 1
        settings = SettingsManager(widget, settings=self.settings)

        # Set a valid value in the settings for radio_button
        settings._settings.set_value(
            settings._get_ui_key(widget.radio_button.objectName()),
            expected_value,
        )
        settings._setup_settings()

        # Assert that value from settings is applied to UI element
        assert widget.radio_button.isChecked() == expected_value

    def test__setup_settings_loading_invalid_type_radio_button(self, widget):
        """
        Tests '_setup_settings' when settings contain an invalid type
        for radio_button.
        The default value from the UI element should be saved to the settings.
        """
        radio_button_state = 0
        widget.radio_button.setChecked(radio_button_state)

        settings = SettingsManager(widget, settings=self.settings)

        # Simulate invalid setting type for radio_button
        settings._settings.set_value(
            settings._get_ui_key(widget.radio_button.objectName()), "invalid"
        )

        settings._setup_settings()

        # Assert that default value from UI element is loaded
        assert (
            settings.get_ui_value(widget.radio_button.objectName())
            == radio_button_state
        )

    def test_update_ui_inputs_new_value_saved(self, widget):
        """
        Test that a new value in QLineEdit is saved
        correctly by SettingsManager.
        """
        new_line_edit = QLineEdit(widget)

        settings = SettingsManager(widget, settings=self.settings)

        new_line_edit.setObjectName("new_line_edit")
        new_line_edit.setText("new_line_edit")

        settings.update_ui_inputs()
        assert settings.get_ui_value("new_line_edit") == "new_line_edit"

    def test_update_ui_inputs_old_value_exists(self, widget):
        """
        Test that the old value in QLineEdit is preserved
        by SettingsManager after updating UI inputs.
        """
        widget.line_edit.setText("line_edit")
        settings = SettingsManager(widget, settings=self.settings)
        new_line_edit = QLineEdit(widget)
        new_line_edit.setObjectName("new_line_edit")
        new_line_edit.setText("new_line_edit")

        settings.update_ui_inputs()
        assert settings.get_ui_value("line_edit") == "line_edit"

    def test_get_ui_value_non_exists_object_key(
        self,
        widget,
    ):
        """
        Test that SettingsManager raises WidgetNotFound for
        a non-existent object key.
        """
        settings = SettingsManager(widget, settings=self.settings)
        with pytest.raises(WidgetNotFound):
            settings.get_ui_value("non_exists")

    def test_get_user_value_exists(
        self,
        widget,
    ):
        """
        Test that SettingsManager correctly retrieves
        an existing user value by key.
        """
        settings = SettingsManager(widget, settings=self.settings)
        key = "secret"
        data = {"super-secret": 1234}
        settings._settings.set_value(settings._get_user_key("secret"), data)

        assert settings.get_user_value(key) == data

    def test_get_user_value_non_exists(
        self,
        widget,
    ):
        """
        Test that SettingsManager returns None when
        a user value does not exist.
        """
        settings = SettingsManager(widget, settings=self.settings)

        assert settings.get_user_value("non_exists") is None

    def test_get_user_value_invalid_type(
        self,
        widget,
    ):
        """
        Test that SettingsManager returns a falsy value
        when the stored type does not match the requested type.
        """
        settings = SettingsManager(widget, settings=self.settings)
        key = "secret"
        data = "non_digit"
        settings._settings.set_value(settings._get_user_key("secret"), data)

        assert not settings.get_user_value(key, int)
