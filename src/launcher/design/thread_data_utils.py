"""
thread_data_utils.py

A module containing utility classes for handling threaded data and user
input data.
"""

from contextlib import contextmanager
from dataclasses import dataclass
from functools import partial
from typing import Any, Dict, List, Optional, Type, TypeVar, overload

from loguru import logger as log
from qtpy.QtCore import QMutex, QObject, QSettings, Signal, Slot
from qtpy.QtWidgets import (
    QCheckBox,
    QComboBox,
    QLineEdit,
    QRadioButton,
    QSpinBox,
    QTextEdit,
    QWidget,
)

from ..utility.custom_exceptions import (
    WidgetNotFound,
    WidgetValueAssignmentError,
)

T = TypeVar("T")


@dataclass
class UiInfo:
    """
    Data class to store information about a UI element
    and its connection to the settings status.
    """

    ui_elem: QWidget
    is_connected: bool


class SettingsStorage:
    """
    Interact with the file system to store and retrieve application settings.
    """

    def __init__(
        self,
        company_name: str,
        app_name: str,
    ) -> None:
        """
        Initialize SettingsStorage with the company and application names.

        Args:
            company_name: The name of the company.
            app_name: The name of the application.
        """
        self._storage = QSettings(company_name, app_name)
        self._mutex_manager = QMutexContextManager()

    def get_value(
        self,
        key: str,
        return_type: Optional[Type] = None,
        default_value: Any = None,
    ) -> Any:
        """
        Extract a value from the file system.

        Args:
            key: The key associated with the desired value.
            return_type: The expected type of the returned value.
            default_value: The value to return if the key does not exist
                or an error occurs.

        Returns:
            The value associated with the key, converted to the specified
                return_type, or default_value if the key is not found.
        """
        with self._mutex_manager.lock():
            try:
                if return_type:
                    return self._storage.value(key, type=return_type)
                return self._storage.value(key)
            except Exception as error:
                log.error(f"Failed to parse key '{key}': {error}")
                return default_value

    def set_value(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Save a value to the file system.

        Args:
            key: The key to associate with the value.
            value: The value to be stored.
        """
        with self._mutex_manager.lock():
            return self._storage.setValue(key, value)


class UIManager:
    """Manage UI elements and their interactions."""

    SUPPORTED_ELEMENTS = [
        QLineEdit,
        QTextEdit,
        QSpinBox,
        QCheckBox,
        QComboBox,
        QRadioButton,
    ]

    def __init__(
        self,
        ui_instance: QWidget,
        excluded_widgets: List[str],
    ) -> None:
        """
        Initialize UIManager with a UI instance and optional excluded widgets.

        Args:
            ui_instance: The main QWidget instance containing the UI elements.
            excluded_widgets: A list of object names for widgets to exclude
                from management.
        """
        self._ui_elements_dict: Dict[str, UiInfo] = {}

        self.update_ui_elements(
            ui_instance=ui_instance,
            excluded_widgets=excluded_widgets,
        )

    def update_ui_elements(
        self,
        ui_instance: QWidget,
        excluded_widgets: Optional[List[str]] = None,
    ) -> None:
        """
        Update the dictionary of UI elements, excluding specified widgets.

        Args:
            ui_instance: The QWidget instance to search for UI elements.
            excluded_widgets: A list of object names for widgets to exclude
                from management.
        """
        for supported_type in self.SUPPORTED_ELEMENTS:
            ui_elements = ui_instance.findChildren(supported_type)
            for ui_elem in ui_elements:
                object_name = ui_elem.objectName()

                # Skip elements without object names
                # Skip elements that were stored previously
                if not object_name or object_name in self._ui_elements_dict:
                    continue

                # Exclude black list elements
                if excluded_widgets and object_name in excluded_widgets:
                    continue
                self._ui_elements_dict[object_name] = UiInfo(
                    ui_elem=ui_elem,
                    is_connected=False,
                )

    @property
    def ui_elements_dict(self) -> Dict[str, UiInfo]:
        """
        Return dict with current ui_elements.
        """
        return self._ui_elements_dict

    @staticmethod
    def get_ui_value(
        ui_element: QWidget,
        default_value: Any = None,
    ) -> Any:
        """
        Extract the value from a specified UI input element.

        Args:
            ui_element: The UI element from which to extract the value.
            default_value: The value to return if extraction fails.

        Returns:
            The extracted value or the default_value if extraction fails.
        """
        res = default_value
        if isinstance(ui_element, QTextEdit):
            res = ui_element.toPlainText()
        elif isinstance(ui_element, QLineEdit):
            res = ui_element.text()
        elif isinstance(ui_element, QSpinBox):
            res = ui_element.value()
        elif isinstance(ui_element, (QCheckBox, QRadioButton)):
            res = 1 if ui_element.isChecked() else 0
        elif isinstance(ui_element, QComboBox):
            res = ui_element.currentIndex()
        return res

    @staticmethod
    def set_ui_value(
        ui_element: QWidget,
        value: Any,
    ) -> None:
        """
        Set a specified value to a UI input element.

        Args:
            ui_element: The UI element to which the value should be assigned.
            value: The value to assign to the UI element.

        Raises:
            WidgetValueAssignmentError: If the assignment fails due
                to type errors or invalid values.
        """
        try:
            if isinstance(ui_element, (QLineEdit, QTextEdit)):
                ui_element.setText(value)
            elif isinstance(ui_element, QSpinBox):
                ui_element.setValue(value)
            elif isinstance(ui_element, (QCheckBox, QRadioButton)):
                ui_element.setChecked(value)
            elif isinstance(ui_element, QComboBox):
                ui_element.setCurrentIndex(value)
            else:
                log.warning(
                    f"Unsupported UI element: {type(ui_element).__name__}"
                )
        except (TypeError, ValueError) as error:
            error_text = (
                f"Failed to assign value '{value}' to "
                f"{type(ui_element).__name__}/{ui_element.objectName()}: "
                f"{error}"
            )
            log.error(error_text)
            raise WidgetValueAssignmentError(error_text) from error


class SettingsManager(QObject):
    """
    A class to manage UI element settings in a PyQt application.

    The SettingsManager is responsible for saving and loading settings
    for various UI elements, ensuring that their states are persisted
    across sessions.
    """

    update_ui_signal = Signal(QWidget, object)

    EXPECTED_TYPES = {
        QLineEdit: str,
        QTextEdit: str,
        QSpinBox: int,
        QCheckBox: bool,
        QComboBox: int,
        QRadioButton: bool,
    }

    SIGNAL_MAP = {
        QLineEdit: lambda e: e.textEdited,
        QTextEdit: lambda e: e.textChanged,
        QSpinBox: lambda e: e.valueChanged,
        QCheckBox: lambda e: e.toggled,
        QComboBox: lambda e: e.currentIndexChanged,
        QRadioButton: lambda e: e.toggled,
    }

    def __init__(
        self,
        ui_instance: QWidget,
        company_name: str,
        app_name: str,
        excluded_widgets: Optional[List[str]] = None,
    ) -> None:
        """
        Initializes the SettingsManager.

        Args:
            ui_instance (QWidget): The main UI instance containing the widgets.
            company_name (str): The name of the company for settings storage.
            app_name (str): The name of the application for settings storage.
            excluded_widgets (Optional[List[str]]): A list of widget
                object names to exclude from settings management.
        """
        super().__init__()
        if not excluded_widgets:
            excluded_widgets = []
        self._settings = SettingsStorage(
            company_name=company_name,
            app_name=app_name,
        )
        self._ui_manager = UIManager(
            ui_instance=ui_instance,
            excluded_widgets=excluded_widgets,
        )
        self._ui_key_prefix = "ui_elements_data"
        self._user_data_key_prefix = "user_data"
        self._ui_instance = ui_instance
        self._create_signals()
        self._setup_settings()

    @Slot(QWidget, object)
    def set_value_to_ui(self, ui_element: QWidget, value: Any) -> None:
        """
        Set a value to a UI element from a non-Qt main thread.

        Args:
            ui_element (QWidget): The UI element to which the value
                will be set.
            value (Any): The value to set for the specified UI element.

        Returns:
            None
        """
        try:
            self._ui_manager.set_ui_value(ui_element, value)
        except WidgetValueAssignmentError:
            return
        self._settings.set_value(
            self._get_ui_key(ui_element.objectName()), value
        )

    def update_ui_inputs(self) -> None:
        """
        Update the UI elements and setup settings.
        This method should be called when the UI needs to be synchronized
        with the current state of the application settings and when new
        UI elements are introduced.
        """
        self._ui_manager.update_ui_elements(self._ui_instance)
        self._setup_settings()

    @overload
    def get_ui_value(self, object_name: str) -> Any: ...
    @overload
    def get_ui_value(self, object_name: str, return_type: Type[T]) -> T: ...

    def get_ui_value(
        self, object_name: str, return_type: Optional[Type[T]] = None
    ) -> T:
        """
        Retrieve the value of a UI element based on its object name.

        Args:
            object_name (str): The object name of the UI element whose value
                is to be retrieved.
            return_type (Optional[Type[T]]): The expected type of the returned
                value. If provided, the value will be cast to this type.

        Returns:
            T: The value associated with the UI element, cast to the specified
                return type.

        Raises:
            WidgetNotFound: If the UI element with the specified object
                name does not exist.
        """
        ui_info = self._ui_manager.ui_elements_dict.get(object_name, None)
        if not ui_info:
            raise WidgetNotFound
        key = self._get_ui_key(object_name)
        return self._settings.get_value(
            key=key,
            return_type=return_type,
        )

    def set_ui_value(self, object_name: str, value: Any) -> None:
        """
        Set the value for a UI element and emit a signal to update it.

        - `str` for `QLineEdit`
        - `str` for `QTextEdit`
        - `int` for `QSpinBox`
        - `bool` for `QCheckBox`
        - `int` (current index) for `QComboBox`
        - `bool` for `QRadioButton`

        Args:
            object_name (str): The object name of the UI element whose
                value is to be set.
            value (Any): The value to set for the UI element, which must match
                the expected type.

        Returns:
            None

        Raises:
            WidgetValueAssignmentError: If the UI element with the given
                object name is not found in the UI manager or if the value
                type does not match the expected type for the specified
                UI element.
        """
        ui_info = self._ui_manager.ui_elements_dict.get(object_name, None)
        if not ui_info:
            raise WidgetValueAssignmentError(
                f"UI element with object_name '{object_name}' "
                "was not found."
            )

        # Determine the expected type based on the widget type
        widget_type = type(ui_info.ui_elem)
        expected_type = self.EXPECTED_TYPES.get(widget_type, None)
        # Validate the value type
        if not expected_type or not isinstance(value, expected_type):
            raise WidgetValueAssignmentError(
                "Expected value of type "
                f"{expected_type} for {object_name}, got {type(value)}"
            )
        self.update_ui_signal.emit(ui_info.ui_elem, value)

    @overload
    def get_user_value(self, key: str) -> Any: ...

    @overload
    def get_user_value(self, key: str, return_type: Type[T]) -> T: ...

    def get_user_value(
        self, key: str, return_type: Optional[Type[T]] = None
    ) -> T:
        """
        Retrieve a user value associated with a specified key.

        Args:
            key (str): The key associated with the user value to be retrieved.
            return_type (Optional[Type[T]]): The expected type of
                the returned value. If provided, the value will be cast
                to this type.

        Returns:
            T: The value associated with the specified key,
                cast to the specified return type,
                or Any if no return type is specified.
        """
        key = self._get_user_key(key)
        return self._settings.get_value(
            key=key,
            return_type=return_type,
        )

    def set_user_value(self, key: str, value: Any) -> None:
        """
        Set a user value associated with a specified key.

        Args:
            key (str): The key under which the user value will be stored.
            value (Any): The value to store, which can be of any type.

        Returns:
            None
        """
        key = self._get_user_key(key)
        return self._settings.set_value(
            key=key,
            value=value,
        )

    def _create_signals(self) -> None:
        """
        Connects UI elements' signals to save their state to QSettings.
        """

        for ui_info in self._ui_manager.ui_elements_dict.values():

            if not ui_info.is_connected:
                signal = self.SIGNAL_MAP.get(
                    type(ui_info.ui_elem), lambda e: None
                )(ui_info.ui_elem)
                if signal:
                    signal.connect(
                        partial(self._save_ui_element_value, ui_info.ui_elem)
                    )
                    ui_info.is_connected = True

                else:
                    log.error(
                        "Unsupported ui_element for new signal: "
                        f"{type(ui_info.ui_elem)}"
                    )

    @Slot()
    def _save_ui_element_value(
        self,
        ui_element: QWidget,
        *args,  # pylint: disable=W0613
    ) -> None:
        """Save ui_input values to the QSettings."""

        object_name = ui_element.objectName()
        if object_name:
            value = self._ui_manager.get_ui_value(ui_element)
            widget_object_key = "/".join([self._ui_key_prefix, object_name])
            self._settings.set_value(
                widget_object_key,
                value,
            )

    def _setup_settings(self) -> None:
        """
        Loads settings from QSettings and applies them to the UI elements.
        Saves default values from the new ui_input elements,
        """
        for ui_info in self._ui_manager.ui_elements_dict.values():
            object_name = ui_info.ui_elem.objectName()
            if not object_name:
                continue
            widget_object_key = self._get_ui_key(object_name)
            value = self._settings.get_value(widget_object_key)
            if value is None:
                # New input found
                value = self._ui_manager.get_ui_value(ui_info.ui_elem)

                self._settings.set_value(widget_object_key, value)
            else:
                # Load value to the old input from settings
                try:
                    self._ui_manager.set_ui_value(ui_info.ui_elem, value)
                except WidgetValueAssignmentError:
                    log.debug(
                        "Fixing incorrect settings value for "
                        f"'{widget_object_key}'"
                    )
                    default_value = self._ui_manager.get_ui_value(
                        ui_info.ui_elem
                    )
                    self._settings.set_value(widget_object_key, default_value)

    def _get_ui_key(self, object_name: str) -> str:
        """Generate a key for storing UI element data in QSettings."""
        return "/".join([self._ui_key_prefix, object_name])

    def _get_user_key(self, object_name: str) -> str:
        """
        Generate a key for storing user data associated with a UI element.
        """
        return "/".join([self._user_data_key_prefix, object_name])


class QMutexContextManager:
    """
    A context manager for safely acquiring and releasing a QMutex lock..
    """

    def __init__(self):
        self._mutex = QMutex()

    @contextmanager
    def lock(self):
        """
        Acquire the QMutex lock for the 'with' block and release it when
        exiting the block.

        Usage:
            with QMutexContextManager().lock():
                # Code that requires thread-safe execution

        Returns:
            None
        """
        self._mutex.lock()
        try:
            yield
        finally:
            self._mutex.unlock()

    @property
    def mutex(self) -> QMutex:
        """Return current QMutex."""
        return self._mutex
