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


@dataclass
class ServerWidgetCSS:
    """Styles for ServerWidget."""

    main_widget: str = """
            QPushButton {
                background-color: rgba(0, 51, 102, 200);  /* Темно-синий цвет с прозрачностью */
                padding: 10px;
                border-radius: 25px;
                color: white;  /* Цвет текста */
                border: none;  /* Убираем границу */
            }

            QPushButton:hover {
                background-color: rgba(0, 76, 153, 200);  /* Более светлый темно-синий при наведении */
            }

            QPushButton:pressed {
                background-color: rgba(0, 102, 204, 200);  /* Более светлый синий при нажатии */
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
        """
    play_button = """
            QPushButton {
                background-color: rgba(255, 105, 180, 200); /* Розовый цвет с прозрачностью */
                padding: 10px; /* Отступы */
                border-radius: 10px; /* Скругление углов */
                color: white; /* Цвет текста */
                border: none; /* Убираем границу */
                font-size: 16px; /* Размер шрифта */
                font-weight: bold; /* Жирный шрифт */
            }

            QPushButton:hover {
                background-color: rgba(255, 20, 147, 200); /* Темный розовый при наведении */
            }

            QPushButton:pressed {
                background-color: rgba(255, 105, 180, 100); /* Более светлый розовый при нажатии */
            }
            """
    progress_bar_online = """
            QProgressBar {
                height: 20px;
                border: 1px solid #555555;
                border-radius: 10px;
                background-color: #3d3f43;
                font-weight: bold;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #7289da;
                border-radius: 10px;
            }
            """
    progress_bar_offline = """
        QProgressBar {
            height: 20px;
            border: 1px solid #aa0000;
            border-radius: 10px;
            background-color: #ffcccc;
            font-weight: bold;
            color: white;

        }
        QProgressBar::chunk {
            background-color: #ff0000;
            border-radius: 10px;
        }
        """
    progress_bar_loading = """
        QProgressBar {
            height: 20px;
            border: 1px solid #555555;
            border-radius: 10px;
            background-color: #f0f0f0;
            font-weight: bold;
            color: #333333;
        }
        QProgressBar::chunk {
            background-color: #00aaff;
            width: 20px;
            margin: 2px;
            border-radius: 10px;
        }
    """


CUSTOM_MESSAGE_BOX_STYLE = (
    """
            QWidget {
                background-color: rgba(26, 26, 64, 255);
                border-radius: 20px;
                font-size: 16px;
            }
            QTextEdit {
                background-color: rgba(0, 0, 0, 0);
                color: white;
            }
            """
    + ServerWidgetCSS.play_button
)

INSTALL_PROGRESS_BAR = """
            QProgressBar {
                border: 2px solid #555;
                border-radius: 15px;
                text-align: center;
                color: #FFFFFF;
                background-color: #3C3F41;
            }
            QProgressBar::chunk {
                border-radius: 15px;
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #66e, stop:1 #bbf
                );
            }
        """

ALLOCATE_RAM_SLIDER = """
QLabel {
    color: white;
    font-size: 24px;
}

QSlider::groove:horizontal {
    border: 1px solid #999999;
    height: 20px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #BBDEFB,  /* Светлый синий */
                                stop:1 #2196F3); /* Темный синий */
    border-radius: 4px;
    color: white;
}

QSlider::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #F06292,  /* Светлый розовый */
                                stop:1 #E91E63); /* Темный розовый */
    border: 1px solid #C2185B;
    width: 20px;
    height: 20px;
    border-radius: 10px;
    margin: -6px 0; /* Handle overlaps the groove */
    color: white;
}

QSlider::handle:horizontal:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #F48FB1,  /* Более светлый розовый при наведении */
                                stop:1 #D81B60); /* Более темный розовый */
}

QSlider::add-page:horizontal {
    background: #b3b3b3;  /* Серый цвет для неактивной части */
    border-radius: 4px;
    color: white;
}
"""

MODPACK_OPTION_CHECKBOX = """
QCheckBox {
    color: #1E90FF; /* Синий цвет текста */
    font: bold 24px;
}

QCheckBox::indicator {
    width: 32px;
    height: 32px;
    border: 2px solid #1E90FF; /* Синий цвет границы */
    background-color: white;
    border-radius: 4px; /* Округленные углы */
}

QCheckBox::indicator:checked {
    background-color: #1E90FF; /* Синий цвет при включении */
    border: 2px solid #104E8B; /* Темно-синий цвет границы */
}

QCheckBox::indicator:unchecked {
    background-color: white;
    border: 2px solid #1E90FF;
}

QCheckBox::indicator:disabled {
    background-color: #B0C4DE; /* Светло-серый с синим оттенком */
    border: 2px solid #A9A9A9; /* Серый цвет границы */
}

QCheckBox::indicator:checked:disabled {
    background-color: #A9A9A9;
    border: 2px solid #6E7B8B; /* Темный серо-синий цвет */
}

QCheckBox:hover {
    color: #4682B4; /* Осветленный синий при наведении */
}

QCheckBox::indicator:hover {
    border-color: #4682B4; /* Осветленный синий цвет границы */
}

"""
