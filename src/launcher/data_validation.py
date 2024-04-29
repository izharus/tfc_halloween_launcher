"""Module for validating data tools."""

import subprocess
import traceback

from loguru import logger as log

from .design.utility import MessageBoxManager


class Validator:
    """Validatin data in MainWindow."""

    def __init__(
        self,
        icon_path: str,
    ):
        self.msg_box = MessageBoxManager(icon_path)

    def is_valid_nickname(self, nickname: str) -> bool:
        """
        Check if nickname is valid.

        Args:
            nickname (int): nickname check for.

        Returns:
            bool: True if nickname is valid, False otherwise.
        """
        if len(nickname) < 3:
            msg_title = "Никнейм отсутствует или слишком короткий."
            self.msg_box.warn(msg_title)
            return False
        return True

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
            )
            return True
        except Exception as error:
            log.error(
                f"Failed to get java version: {error}."
                "Java maybe not installed, or not added to the PATH."
            )
            log.debug(traceback.format_exc())
            return False
