"""A modules with custom exception classes"""


class JavaGetVersionError(ValueError):
    """Raises if java not found in the system"""

    def __init__(self, message="Failed to retrieve Java version"):
        super().__init__(message)
