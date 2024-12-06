"""A modules with custom exception classes"""


class ModpackNotfound(Exception):
    """
    Raised if the modpack was not found with the provided config name.
    """

    def __init__(
        self, message="Modpack was not found with the provided modpack name."
    ):
        super().__init__(message)


class DownloadServerHandshakeError(Exception):
    """Raised if failed to connect to the file store server."""

    def __init__(self, message="File server handshake error."):
        super().__init__(message)

    def __str__(self):
        return "Файловый сервер недоступен."


class MinecraftLauncherConfigNotSet(RuntimeError):
    """Raises if launcher config not set"""

    def __init__(self, message="Launcher config not set. Use set_config()."):
        super().__init__(message)

    def __str__(self):
        return "Не установлен конфиг лаунчера."


class FileDownloadError(Exception):
    """Raises in any error occurs deu downloading files."""

    def __init__(self, message="Failed to download a file.") -> None:
        super().__init__(message)


class ConfigDownloadError(FileDownloadError):
    """
    Raises if any error occurs due downloading a config file.
    """

    def __init__(
        self, message="Failed to download a configuration file."
    ) -> None:
        super().__init__(message)

    def __str__(self):
        return "Ошибка во время загрузки файла конфигурации."


class FileHashMismatchError(FileDownloadError):
    """
    Raised if the hash of a downloaded file does not match the expected hash.
    """

    def __init__(
        self, message="File hash does not match the expected hash."
    ) -> None:
        super().__init__(message)


class ConfigProcessingError(Exception):
    """
    Raises if any error occurs due processing a config file.
    """

    def __init__(
        self, message="Failed to process a configuration file."
    ) -> None:
        super().__init__(message)

    def __str__(self):
        return "Ошибка во время обработки файла конфигурации."


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

    def __str__(self):
        return "Ошибка вычисления хеш-суммы."


class AuthenticationError(Exception):
    """Base class for all errors within authentication."""


class AuthenticationServiceUnavailable(AuthenticationError):
    """Raises if authentication service unavailable."""

    def __init__(
        self, message: str = "Authentication service is unavailable."
    ) -> None:
        super().__init__(message)

    def __str__(self):
        return "Сервер авторизации недоступен."


class InvalidUserNameOrPassword(AuthenticationError):
    """Raises if user name or password is invalid."""

    def __init__(self, message: str = "Invalid username or password.") -> None:
        super().__init__(message)

    def __str__(self):
        return "Пользователь не найден."


class InternalAuthenticationError(AuthenticationError):
    """
    Raises if any error occurs due authentication operations.
    """

    def __init__(
        self,
        message: str = "An error occurred during authentication operation",
    ) -> None:
        super().__init__(message)

    def __str__(self):
        return "Ошибка #2."


class InvalidAuthenticationResponse(AuthenticationError):
    """
    Raises if an invalid authentication response was received.
    """

    def __init__(
        self,
        message: str = "Invalid authentication response.",
    ) -> None:
        super().__init__(f"{message}")

    def __str__(self):
        return "Ошибка #1."


class AuthDataNotSet(RuntimeError):
    """
    Raised if the username and password are not set for AuthorizationThread.
    """

    def __init__(self, message="Auth data not set. Use set_auth_data()."):
        super().__init__(message)

    def __str__(self):
        return "Некорректный ответ от сервера #3."


class Base64ParsingError(RuntimeError):
    """
    Custom exception for errors occurring during the parsing of base64 strings.
    """

    def __init__(
        self,
        message="Unable to parse base64 string.",
    ) -> None:
        super().__init__(f"{message}")

    def __str__(self):
        return "Не удалось прочитать файл."


class WidgetValueAssignmentError(Exception):
    """Custom exception for errors during value assignment to UI elements."""

    def __init__(self, message: str = "Incorrect value for widget."):
        self.message = message
        super().__init__(self.message)


class WidgetNotFound(Exception):
    """Exception raised when a specified widget cannot be found."""

    def __init__(self, message: str = "Widget was nof found."):
        self.message = message
        super().__init__(self.message)


class ServerQueryStatusError(Exception):
    """
    Exception raised if any error occurs due querying information
    from a minecraft server
    """

    def __init__(
        self, message: str = "Failed to query minecraft server online status."
    ):
        self.message = message
        super().__init__(self.message)
