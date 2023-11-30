"""Module with QT elements styles."""
from dataclasses import dataclass


@dataclass
class MainButtonData:
    """
    Data class defining default text values for authorization,
    installation, and launch buttons.
    """

    install_text: str = "Установить и войти"
    launch_text: str = "Войти"
