"""A modules with custom exception classes"""


class MinecraftLauncherConfigNotSet(RuntimeError):
    """Raises if lancher config not set"""

    def __init__(self, message="Lancher config not set. Use set_config()."):
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


class AuthorizationServiceUnavailable(RuntimeError):
    """Raises if authorization service unavailable."""

    def __init__(self, message="Authorization service unavailable.") -> None:
        super().__init__(message)

    def __str__(self):
        return "Сервер авторизации недоступен."


class AuthDataNotSet(RuntimeError):
    """
    Raised if the username and password are not set for AuthorizationThread.
    """

    def __init__(self, message="Auth data not set. Use set_auth_data()."):
        super().__init__(message)

    def __str__(self):
        return "Некорректный ответ от сервера #3."


class UserAuthenticationError(Exception):
    """Custom exception for user authentication failures."""

    def __init__(self, message="Invalid username or password.") -> None:
        super().__init__(message)

    def __str__(self):
        return "Неправильное имя пользователя или пароль."


class IternalAuthenticationError(RuntimeError):
    """
    Custom exception raised for errors related to authentication operations.
    """

    def __init__(
        self,
        message="An error occurred during authentication operation",
        error_code="500",
    ) -> None:
        super().__init__(f"{message}: {error_code}.")
        self.error_code = error_code

    def __str__(self):
        return "Некорректный ответ от сервера #2."


class IvalidAuthenticationResponseError(RuntimeError):
    """
    Custom exception for invalid authentication responses.
    """

    def __init__(
        self,
        message="Invalid authentication response.",
    ) -> None:
        super().__init__(f"{message}")

    def __str__(self):
        return "Некорректный ответ от сервера #1."
