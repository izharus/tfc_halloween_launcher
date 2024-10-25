"""Utility module for storing some static data."""

import os
import subprocess
from typing import Final

SUBPROCESS_CREATION_FLAGS: Final = (
    subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
)
