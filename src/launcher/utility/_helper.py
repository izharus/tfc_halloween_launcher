"""Utility module for storing some static data."""

import os
import platform
import subprocess
import sys
from os import PathLike
from typing import Final

from loguru import logger as log

SUBPROCESS_CREATION_FLAGS: Final = (
    subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
)


def is_windows_8_or_older() -> bool:
    """Check if the user is running Windows 7 or an older version.

    This function retrieves the current version of the Windows operating
    system and checks if it is Windows 7 (version 6.1) or older.

    Returns:
        bool: True if the Windows version is 7 or older, False otherwise.
    """

    version = platform.version()
    major_version = int(version.split(".")[0])

    if platform.system() == "Windows" and major_version < 8:
        return True
    return False


def get_version():
    """
    Determines the version and architecture of the current Python environment.

    Returns:
        str: A string representing the operating system and architecture.
                Returns 'win7x64' or 'win7x86' if Python version is 3.8
                (indicating compatibility with Windows 7), and 'win10x64'
                or 'win10x86'  otherwise. 'x64' indicates 64-bit architecture,
                and 'x86' indicates 32-bit.
    """
    # Python version
    res = ""

    if platform.python_version().startswith("3.8"):
        res = "win7"
    else:
        res = "win10"

    # 32 or 64 bit
    if sys.maxsize > 2**32:
        res += "x64"
    else:
        res += "x86"

    return res


def init_loguru_logger(logging_dir: PathLike) -> None:
    """Initialize main logger."""
    log.add(
        logging_dir,
        rotation="1 month",
        retention="1 month",  # Retain log files for 1 month after rotation
        compression="zip",  # Optional: Enable compression for rotated logs
        level="DEBUG",
        serialize=False,
    )
