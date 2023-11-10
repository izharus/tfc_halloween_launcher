"""A modules with custom exception classes"""


class MinecraftLauncherConfigNotSet(RuntimeError):
    """Raises if lancher config not set"""

    def __init__(self, message="Lancher config not set. Use set_config()."):
        super().__init__(message)


class RequestDownloadError(Exception):
    """Raises in any HTTP errors that occur while downloading files."""

    def __init__(
        self, message="HTTP request error in attempting to download a file."
    ) -> None:
        super().__init__(message)


class FilesSaveError(Exception):
    """Raises when an error occurs while saving or writing files."""

    def __init__(
        self,
        message="Error occurred while saving or writing a file.",
    ) -> None:
        super().__init__(message)


class CalculateHashFailed(RuntimeError):
    """Raises if calculate_hash func raises any exception."""

    def __init__(self, message="Calculate_hash function failed.") -> None:
        super().__init__(message)
