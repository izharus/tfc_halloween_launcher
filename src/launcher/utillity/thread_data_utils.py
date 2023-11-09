"""
thread_data_utils.py

A module containing utility classes for handling threaded data and user
input data.

This module provides various utility classes for managing threaded data and
handling user input data in PyQt6 applications. It includes classes for
storing long-term program data, managing UI inputs, updating QLabel and
QTextEdit widgets in a thread-safe manner, and writing log lines to a
QTextEdit widget with thread safety.
External Dependencies:
- PyQt6: A library for creating desktop applications with graphical user
    interfaces using the Qt framework.

Classes:
- ThreadData: A class for storing long-term program data.
- ThreadUiInputData: A class that extends ThreadData to work with UI inputs.
- QMutexContextManager: A context manager based on QMutex for ensuring thread
    safety.
- LabelTextEditUpdater: A class for updating the text of a QLabel or
    QTextEdit widget in a thread-safe manner.
- TextEditLogWriter: A class for writing log lines to a QTextEdit widget in
    a thread-safe manner.
- LastVeryGoodCounter: A class that keeps track of the time since the last
    "VeryGood" event andraises an error if a certain time limit is exceeded.

Each class is designed to provide specific functionality related to threaded
data and user input handling in PyQt6 applications. Refer to the individual
class docstrings for more details on their usage and methods.

Usage examples and detailed explanations are provided within the docstrings
of each class.

Note: This module requires the PyQt6 library to be installed.

"""

import json

# from log_wizard import log as main_log
import logging
import os
import threading
import time
import typing
from contextlib import contextmanager
from typing import Any, Dict, Union

from PyQt6 import QtCore, QtWidgets


class ThreadData:
    """
    Class to store long-term program data.
    """

    def __init__(self, str_path: str = "data\\ui_inputs_data\\input_data"):
        """
        Initialize the ThreadData instance.

        Args:
            str_path (str): Path to the data file.
        """
        str_dir = os.path.dirname(str_path)
        if str_dir != "" and not os.path.exists(str_dir):
            os.makedirs(str_dir)
        self.str_path = str_path
        self.dict_thread_data: Dict[str, Any] = {}
        self.mutex = threading.Lock()
        self.get_data_from_file()

    def get_data_from_file(self) -> bool:
        """
        Load data from the file.

        Returns:
            bool: True if the data is loaded successfully, False otherwise.
        """
        with self.mutex:
            try:
                with open(self.str_path, encoding="utf-8") as file_read:
                    self.dict_thread_data = json.load(file_read)
            except Exception:
                return False
            return True

    def put_data_to_file(self, data: Dict, app_name: str = "default") -> bool:
        """
        Store the provided data with the given name.

        Args:
            data (Dict): Data to be stored.
            app_name (str): Name for the data for key in dict (default is
                "default").

        Returns:
            bool: True if the data is stored successfully, False otherwise.
        """
        with self.mutex:
            self.dict_thread_data[app_name] = data
            try:
                with open(self.str_path, "w", encoding="utf-8") as file_write:
                    json.dump(self.dict_thread_data, file_write)
            except Exception as error:
                logging.error(f"put_data_to_file() failed: {error}")
                return False
        return True

    def get_input_data(self, app_name: str = "default") -> Dict[str, Any]:
        """
        Retrieve the data associated with the given name.

        Args:
            app_name (str): Name of the data to retrieve (default is
                "default").

        Returns:
            Any: Retrieved data if available, False otherwise.
        """
        try:
            return self.dict_thread_data[app_name]
        except Exception:
            logging.info(f"Creating input_data for new app: {app_name}")
            return {}


class ThreadUiInputData(ThreadData):
    """
    A class that extends ThreadData to work with UI inputs.

    The ThreadUiInputData class is designed to handle UI inputs and store them
    in a data dictionary. It provides methods to generate a dictionary of UI
    data, populate missing input data, update UI elements based on the input
    data, and update the input data from the UI elements.

    Args:
        ThreadData: The parent class that handles thread instances and
            long-term program data.

    Attributes:
        dict_ui_data (Dict[str, Dict[str, Any]]): A dictionary containing UI
            data categorized by UI element types.
        ui_instance (Any): An instance of the UI class.
        dict_input_data (Dict[str, Any]): The data dictionary that stores the
            input data.
        time_delay (int): The time delay in milliseconds for autosave
            operations (default is 2000).

    Methods:
        update_dict_ui_data(ui_instance: Any) -> None:
            Generates a dictionary of UI data based on the provided UI
            instance and stores it into self.dict_input_data.

        populate_missing_input_data() -> None:
            Checks and populates missing input data with default values.

        update_ui_with_input_data() -> None:
            Loads input data from the dictionary and updates the UI elements
            accordingly.

        update_input_data_from_ui() -> None:
            Updates the data dictionary with the current values from the UI
            elements and saves it to the file.

        change_input_edit_status(bool_stop_edit: bool = False) -> None:
            Enables or disables editing of the input elements in the UI.

    """

    # Define constants for UI element types
    UI_ELEMENT_TYPES = [
        "spinBox",
        "lineEdit",
        "comboBox",
        "checkBox",
        "textEdit",
    ]

    def __init__(
        self,
        ui_instance: Any,
        str_path: str = "data\\ui_inputs_data\\input_data",
    ):
        """
        Initialize the ThreadUiInputData instance.

        Args:
            ui_instance (Any): An instance of the UI class.
            str_path (str): Path to the data file.
        """
        ThreadData.__init__(self, str_path)
        self.time_delay = 2000  # 2 seconds
        self.dict_input_data = self.get_input_data()

        self.dict_ui_data: Dict[str, Dict[str, Any]] = {
            "spinBox": {},
            "lineEdit": {},
            "comboBox": {},
            "checkBox": {},
            "textEdit": {},
            "pushButton": {},
        }
        self.update_dict_ui_data(ui_instance)

    def update_dict_ui_data(self, ui_instance: Any) -> None:
        """
        Generate a dictionary of UI data based on the provided UI instance.

        This method iterates through the UI elements of different types in the
        provided UI instance and populates the corresponding dictionaries in
        'self.dict_ui_data' with the UI elements.

        UI items with 'disable_long_tern_save' in their name will be excluded.

        Args:
            ui_instance (Any): An instance of the UI class.

        Raises:
            ValueError: If duplicate UI elements are found.

        Returns:
            None
        """
        ui_element_types = [
            ("spinBox", QtWidgets.QSpinBox),
            ("lineEdit", QtWidgets.QLineEdit),
            ("comboBox", QtWidgets.QComboBox),
            ("checkBox", QtWidgets.QCheckBox),
            ("textEdit", QtWidgets.QTextEdit),
            ("pushButton", QtWidgets.QPushButton),
        ]

        # print("====")
        for attr_name in dir(ui_instance):
            if "disable_long_tern_save" not in attr_name:
                ui_element = getattr(ui_instance, attr_name)
                for element_type, element_class in ui_element_types:
                    if isinstance(ui_element, element_class):
                        if attr_name in self.dict_ui_data[element_type]:
                            raise ValueError(
                                f"Duplicates in UI found: \
                                    {ui_element} | {attr_name}"
                            )
                        self.dict_ui_data[element_type][attr_name] = ui_element
                        # print(attr_name)
                        break

        self.populate_missing_input_data()
        self.update_ui_with_input_data()

        self.put_data_to_file(self.dict_input_data)

    def extract_element(self, element_name: str) -> Any:
        """
        Extracts an element from the dict_input_data dictionary and returns
        its value.

        Args:
            element_name (str): The name of the element to extract.

        Returns:
            Any: The value of the extracted element, or None if the element
                does not exist.
        """
        return self.dict_input_data.get(element_name)

    def populate_missing_input_data(self) -> None:
        """
        Check and populate missing input data with default values.

        This method checks each UI element in the dict_ui_data and populates
        the dict_input_data dictionary with default values for any missing UI
        elements.

        Returns:
            None
        """
        for spinbox_name, spinbox_ui in self.dict_ui_data["spinBox"].items():
            if spinbox_name not in self.dict_input_data:
                try:
                    value = int(spinbox_ui.text().split(" ")[0])
                except ValueError:
                    value = 1
                self.dict_input_data[spinbox_name] = value

        for ui_name, lineedit_ui in self.dict_ui_data["lineEdit"].items():
            if ui_name not in self.dict_input_data:
                self.dict_input_data[ui_name] = lineedit_ui.text()

        for ui_name, textedit_ui in self.dict_ui_data["textEdit"].items():
            if ui_name not in self.dict_input_data:
                self.dict_input_data[ui_name] = textedit_ui.toPlainText()

        for ui_name, checkbox_ui in self.dict_ui_data["checkBox"].items():
            if ui_name not in self.dict_input_data:
                self.dict_input_data[ui_name] = checkbox_ui.isChecked()

        for ui_name, combobox_ui in self.dict_ui_data["comboBox"].items():
            if ui_name not in self.dict_input_data:
                self.dict_input_data[ui_name] = combobox_ui.currentText()

    def update_ui_with_input_data(self) -> None:
        """
        Load input data from the dictionary and update the UI elements
        accordingly.

        This method retrieves the input data from the dict_input_data
        dictionary and sets the values of the corresponding UI elements in the
        dict_ui_data.

        Returns:
            None
        """

        for ui_name, spinbox_ui in self.dict_ui_data["spinBox"].items():
            spinbox_ui.setValue(self.dict_input_data[ui_name])

        for ui_name, lineedit_ui in self.dict_ui_data["lineEdit"].items():
            lineedit_ui.setText(self.dict_input_data[ui_name])

        for ui_name, checkbox_ui in self.dict_ui_data["checkBox"].items():
            checkbox_ui.setChecked(self.dict_input_data[ui_name])

        for ui_name, textedit_ui in self.dict_ui_data["textEdit"].items():
            textedit_ui.setText(self.dict_input_data[ui_name])

        # нужно по тексту выбрать элемент в комбобоксе
        for ui_name, combobox_ui in self.dict_ui_data["comboBox"].items():
            try:
                combobox_ui.setCurrentIndex(
                    combobox_ui.findText(self.dict_input_data[ui_name])
                )
            # If text in file was changed
            except Exception:
                pass

    def update_input_data_from_ui(self, app_name: str = "default") -> None:
        """
        Update the dict_input_data with the current values from the UI elements
        and save it to the file.

        This method retrieves the current values from the UI elements and
        updates the corresponding entries in the dict_input_data dictionary.
        Args:
            app_name (str): The name of app (key for data in dict)
        Returns:
            None
        """
        self.dict_input_data = {}
        for spinbox_name, spinbox_ui in self.dict_ui_data["spinBox"].items():
            self.dict_input_data[spinbox_name] = spinbox_ui.value()

        for ui_name, lineedit_ui in self.dict_ui_data["lineEdit"].items():
            self.dict_input_data[ui_name] = lineedit_ui.text()

        for ui_name, checkbox_ui in self.dict_ui_data["checkBox"].items():
            self.dict_input_data[ui_name] = checkbox_ui.isChecked()

        for ui_name, textinput_ui in self.dict_ui_data["textEdit"].items():
            self.dict_input_data[ui_name] = textinput_ui.toPlainText()

        for ui_name, combobox_ui in self.dict_ui_data["comboBox"].items():
            self.dict_input_data[ui_name] = combobox_ui.currentText()

        self.put_data_to_file(self.dict_input_data, app_name)

    def change_input_edit_status(self, bool_stop_edit: bool = False) -> None:
        """
        Enable or disable editing of the input elements.

        This method allows enabling or disabling the editing status of the
        input elements in the UI.

        Args:
            bool_stop_edit (bool):
                A boolean indicating whether to stop or allow editing of the
                input elements. Defaults to False, allowing editing.

        Returns:
            None
        """
        for ui_elem in self.dict_ui_data["spinBox"].values():
            ui_elem.setReadOnly(bool_stop_edit)

        for ui_elem in self.dict_ui_data["lineEdit"].values():
            ui_elem.setReadOnly(bool_stop_edit)

        for ui_elem in self.dict_ui_data["checkBox"].values():
            ui_elem.setEnabled(not bool_stop_edit)

        for ui_elem in self.dict_ui_data["textEdit"].values():
            ui_elem.setReadOnly(bool_stop_edit)

        for ui_elem in self.dict_ui_data["comboBox"].values():
            ui_elem.setEnabled(not bool_stop_edit)

        for ui_elem in self.dict_ui_data["pushButton"].values():
            ui_elem.setEnabled(not bool_stop_edit)

    @contextmanager
    def change_input_edit_status_context(self):
        """
        Context manager for changing the input edit status within a controlled
        context.

        Yields:
            None

        Raises:
            Any: Any exception raised within the context.

        Example:
            # Assuming you have an instance of the ThreadUiInputData class
            # named 'input_data'
            with input_data.change_input_edit_status_context():
                # Perform actions with input edit status changed

            # Input edit status will be automatically restored after exiting
            # the 'with' block
        """
        try:
            self.change_input_edit_status(True)
            yield
        finally:
            self.change_input_edit_status(False)


class QMutexContextManager:
    """
    A context manager for safely acquiring and releasing a QMutex lock.

    This class enables the use of a QMutex lock as a context manager using
    the 'with' statement, ensuring that critical sections of code are executed
    in a thread-safe manner.

    Usage:
        mutex_manager = QMutexContextManager()
        with mutex_manager.lock():
            # Code that requires thread-safe execution

    Note:
        The QMutex object will be automatically locked when entering the 'with'
        block and unlocked upon exit.
    """

    def __init__(self):
        """
        Initialize a QMutexContextManager object.

        Args:
            None

        Returns:
            None
        """
        self._mutex = QtCore.QMutex()

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

    def get_mutex(self) -> QtCore.QMutex:
        """
        Get the underlying QMutex object used by the context manager.

        This method allows direct access to the QMutex object if more
        fine-grained control is needed. It can be useful in scenarios where
        manual locking and unlocking are required.

        Returns:
            QtCore.QMutex: The QMutex object used by the context manager.
        """
        return self._mutex


class LabelTextEditUpdater(QtCore.QObject):
    """
    A class for updating the text of a QLabel or QTextEdit widget in a
    thread-safe manner.

    This class provides methods for updating the text of a QLabel or QTextEdit
    widget from multiple threads, ensuring thread safety by using a mutex lock.

    Usage:
    - Create an instance of LabelTextEditUpdater and pass the QLabel or
        QTextEditwidget to update.
    - Connect the signal to a slot or function that updates the widget
        with the received data.
    - Call the write_to_widget method to update the widget's text from a
        different thread.
    - Alternatively, you can directly call the update_data method to update
        the widget's text within the same thread.

    label = QtWidgets.QLabel()
    updater = LabelTextEditUpdater(label)
    updater.signal.connect(label.setText)
    updater.write_to_widget("New text")
    """

    signal = QtCore.pyqtSignal(str)

    def __init__(
        self,
        ui_widget: typing.Union[QtWidgets.QLabel, QtWidgets.QTextEdit],
    ):
        """
        Initialize the LabelTextEditUpdater instance.

        Args:
            log_widget (Union[QLabel, QTextEdit]):
                The QLabel or QTextEdit widget to update.
        """
        self.ui_widget: typing.Union[QtWidgets.QLabel, QtWidgets.QTextEdit]
        self.ui_widget = ui_widget
        super().__init__()
        self.mutex = QMutexContextManager()

    def update_data(self, text_data: Union[str, int]) -> None:
        """
        Update the text of the widget with the given data.

        Args:
            text_data (str, int): The text data to update.

        Returns:
            None
        """
        with self.mutex.lock():
            self.ui_widget.setText(str(text_data))

    def write_to_widget(self, text_data: Union[str, int]) -> None:
        """
        Emit a signal to update the text of the widget with the given data.

        Args:
            text_data (int, str): The text data to update.

        Returns:
            None
        """
        self.signal.emit(str(text_data))


# class TextEditLogWriter
class TextEditLogWriter(QtCore.QObject):
    """
    A class for writing log lines to a QTextEdit widget in a thread-safe
    manner.

    Usage:
        log_widget = QtWidgets.QTextEdit()
        log_writer = TextEditLogWriter(log_widget)
        log_writer.signal.connect(log_writer.add_log_line)
        log_writer.write_to_log("Log line 1")
        log_writer.write_to_log("Log line 2")
    """

    signal = QtCore.pyqtSignal(str)

    def __init__(self, log_widget):
        """
        Initialize the TextEditLogWriter instance.

        Args:
            log_widget (QTextEdit): The QTextEdit widget to write log lines to.
        """
        super().__init__()
        self.log_widget = log_widget
        self.current_line = 0
        self.max_line_count = 100_000
        self.mutex = QMutexContextManager()

    def add_log_line(self, log_line: str) -> None:
        """
        Add a log line to the QTextEdit widget.

        Args:
            log_line (str): The log line to add.

        Returns:
            None
        """
        with self.mutex.lock():
            self.current_line += 1
            if self.current_line >= self.max_line_count:
                self.log_widget.clear()
                self.current_line = 0
            self.log_widget.append(log_line)

    def write_to_log(self, log_line: str) -> None:
        """
        Emit a signal to write a log line to the QTextEdit widget.

        Args:
            log_line (str): The log line to write.

        Returns:
            None
        """
        self.signal.emit(log_line)


# class LastVeryGoodCounter()
class LastVeryGoodCounter:
    """
    A class that keeps track of the time since the last "VeryGood" event
    and raises an error if a certain time limit is exceeded.
    """

    def __init__(self, time_to_stop, is_working):
        """
        Initialize the LastVeryGoodCounter instance.

        Args:
            time_to_stop (int):
                The time limit (in seconds) after which an error is raised
                if no "VeryGood" event occurs.
            is_working (func):
                if Fause - stop timer

        Attributes:
            time_to_stop (int):
                The time limit (in seconds) after which an error is raised
                if no "VeryGood" event occurs.
            mutex (threading.Lock): A mutex used for thread safety.
                time_of_last_verygood (float): The timestamp of the last
                "VeryGood" event. was_error (bool): Indicates if an error
                has occurred.
            callback_time (int):
                The time interval (in seconds) between each check for the
                last "VeryGood" event.
            timer (threading.Timer):
                The timer object that triggers the check for the last
                "VeryGood" event at regular intervals.
        """

        self.time_to_stop = time_to_stop

        self.mutex = threading.Lock()
        self.time_of_last_verygood = 0
        self.uppdate_last_verygood_time()
        self.was_error = False
        self.callback_time = 10
        self.is_working = is_working
        threading.Timer(self.callback_time, self.update_last_check).start()

    def update_last_check(self, proc_id: str = "main_worker") -> None:
        """
        Update the last check for the last "VeryGood" event and raise an error
        if the time limit is exceeded.

        Args:
            proc_id (str): The ID of the process triggering the update.

        Returns:
            None
        """
        if time.time() - self.time_of_last_verygood > self.time_to_stop:
            logging.error(
                f"{proc_id} СТОП, VeryGood не было более "
                + str(self.time_to_stop / 60)
                + " минут"
            )
            self.was_error = True

        elif self.is_working():
            threading.Timer(self.callback_time, self.update_last_check).start()

    def get_error_status(self) -> bool:
        """
        Get the error status.

        Returns:
            bool: True if an error has occurred, False otherwise.
        """
        return self.was_error

    def uppdate_last_verygood_time(self) -> None:
        """
        Update the timestamp of the last "VeryGood" event.

        Returns:
            None
        """
        with self.mutex:
            self.time_of_last_verygood = time.time()
