"""
This module provides a decorator, handle_exceptions, for handling exceptions
raised by a function.

The handle_exceptions decorator can be applied to any function and wraps it
with exception handling logic.
If the decorated function raises an exception, the decorator catches it,
logs an error message with the name of the calling function and the error
details, and returns False.

Usage:
    To use the handle_exceptions decorator, apply it to the desired
    function using the @handle_exceptions syntax.
"""
import inspect
import logging
import traceback
from functools import wraps
from typing import Any, Callable


def handle_exceptions(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to handle exceptions raised by a function.

    This decorator wraps a function with exception handling logic. It catches
    any exception raised by the function and logs an error message, including
    the name of the calling function and the error details. If an exception
    occurs, it returns False.

    Args:
        func (Callable[..., Any]): The function to decorate.

    Returns:
        Callable[..., Any]: The wrapped function.

    Raises:
        N/A

    Example:
        @handle_exceptions
        def my_function():
            # Function logic here
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as error:
            calling_function = inspect.stack()[1].function
            logging.error(f"{calling_function}: {str(error)}")
            traceback_str = (
                traceback.format_exc()
            )  # This will generate the traceback as a string
            logging.debug(f"Traceback:\n{traceback_str}")
            return False

    return wrapper


def log_operation(func):
    """
    Decorator that logs the start, success, or failure of an operation.

    This decorator adds log messages for the start, success, or failure of an
    operation. If the decorated method returns False an error message is
    logged. If the decorated method returns anything other than False, a
    success message is logged.

    Args:
        func (function): The function to be decorated.

    Returns:
        function: The decorated function.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        Wrapper function that adds log messages for operation.

        This wrapper function adds log messages for the start, success, or
        failure of an operation. If the decorated method returns False an
        error message is logged. If the decorated method returns anything
        other than False, a success message is logged.

        Args:
            *args: Positional arguments passed to the decorated method.
            **kwargs: Keyword arguments passed to the decorated method.

        Returns:
            The result of the decorated function.
        """
        logging.debug(f"Operation started: {func.__name__}")
        result = func(*args, **kwargs)
        if result is False:
            logging.error(f"Operation failed: {func.__name__}")
        else:
            logging.debug(f"Operation success: {func.__name__}")

        return result

    return wrapper
