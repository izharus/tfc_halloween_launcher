"""A modules with custom exception classes"""


class ConfigLoaderInitError(Exception):
    """Raises if failed to initialize ConfigLoader"""

    def __init__(self, message="Failed to initialize ConfigLoader."):
        super().__init__(message)

    def __str__(self):
        return "Не удалось установить связь с сервером."


class MinecraftLauncherConfigNotSet(RuntimeError):
    """Raises if launcher config not set"""

    def __init__(self, message="Launcher config not set. Use set_config()."):
        super().__init__(message)

    def __str__(self):
        return "Не установлен конфиг лаунчера."


class RequestDownloadError(Exception):
    """Raises in any HTTP errors that occur while downloading files."""

    def __init__(
        self, message="HTTP request error in attempting to download a file."
    ) -> None:
        super().__init__(message)

    def __str__(self):
        return "Ошибка во время загрузки файлов."


class ConfigDownloadError(Exception):
    """
    Raises if any error occurs due loading a config file.
    """

    def __init__(self, message="Failed to load a configuration file.") -> None:
        super().__init__(message)

    def __str__(self):
        return "Ошибка во время загрузки файла конфигурации."


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

    def __str__(self):
        return "Файловая ошибка I/O."


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
