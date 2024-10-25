"""Module for validating data tools."""

import subprocess
import traceback

from loguru import logger as log

from .utility._helper import SUBPROCESS_CREATION_FLAGS


class Validator:
    """Validation data in MainWindow."""

    @staticmethod
    def is_java_installed() -> bool:
        """
        Check if Java is installed on the system.

        Returns:
            bool: True if Java is installed, False otherwise.
        """
        try:
            # Run the 'java -version' command to check the Java version

            # This function return output from console
            # If needed, we can parse current Java version from the console
            subprocess.check_output(
                ["java", "-version"],
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                creationflags=SUBPROCESS_CREATION_FLAGS,
            )
            return True
        except Exception as error:
            log.error(
                f"Failed to get java version: {error}."
                "Java maybe not installed, or not added to the PATH."
            )
            log.debug(traceback.format_exc())
            return False
