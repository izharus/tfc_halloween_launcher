"""Module for validating data tools."""
import webbrowser

from .design.utillity import MessageBoxManager
from .launcher_installer import MinecraftLauncherConfig, get_java_major_version
from .utillity.custom_exceptions import JavaGetVersionError


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

    def is_java_version_supported(self) -> bool:
        """
        Check if Java version correct.

        Returns:
            bool: if Java version supported, False otherwise.
        """
        required_version = MinecraftLauncherConfig.minecraft_java_version
        try:
            version = get_java_major_version()
        except JavaGetVersionError as error_msg:
            java_install_url = MinecraftLauncherConfig.java_install_url
            self.msg_box.warn(
                "Не удалось найти Java в система.",
                msg_box_info=str(error_msg),
                callback_function=lambda: webbrowser.open(java_install_url),
            )
            return False
        if version < required_version:
            java_install_url = MinecraftLauncherConfig.java_install_url
            self.msg_box.warn(
                f"Java {required_version} или выше не установлена в системе.",
                callback_function=lambda: webbrowser.open(java_install_url),
                msg_box_info=f"Версия java найдена: '{version}'. "
                "Проверьте чтобы java была добавлена в PATH.",
            )
            return False
        return True
