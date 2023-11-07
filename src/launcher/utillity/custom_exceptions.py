"""A modules with custom exception classes"""


class JavaGetVersionError(ValueError):
    """Raises if java not found in the system"""

    def __init__(self, message="Failed to retrieve Java version"):
        super().__init__(message)


class UndefinedMinecraftLauncherConfig(ValueError):
    """Raises if lancher access to undefined MinecraftLauncherConfig."""

    def __init__(self, message="Undefined MinecraftLauncherConfig."):
        super().__init__(message)


class MinecraftLauncherConfigNotSet(RuntimeError):
    """Raises if lancher config not set"""

    def __init__(self, message="Lancher config not set. Use set_config()."):
        super().__init__(message)
