"""Utility module for storing some static data."""

import os
import subprocess
from typing import Final

SUBPROCESS_CREATION_FLAGS: Final = (
    subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
)
import platform

def is_windows_8_or_older() -> bool:
    """Check if the user is running Windows 7 or an older version.

    This function retrieves the current version of the Windows operating
    system and checks if it is Windows 7 (version 6.1) or older.

    Returns:
        bool: True if the Windows version is 7 or older, False otherwise.
    """

    version = platform.version()
    major_version = int(version.split('.')[0])

    if platform.system() == "Windows" and major_version < 8:
        return True
    return False
