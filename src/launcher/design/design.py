# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'design.ui'
##
## Created by: Qt User Interface Compiler version 6.7.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QProgressBar, QPushButton, QRadioButton, QScrollArea,
    QSizePolicy, QSpacerItem, QStackedWidget, QVBoxLayout,
    QWidget)
from resources import resources


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(1050, 600)
        MainWindow.setMinimumSize(QSize(1050, 600))
        MainWindow.setMaximumSize(QSize(1050, 600))
        MainWindow.setStyleSheet(u"")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setMinimumSize(QSize(1050, 550))
        self.centralwidget.setMaximumSize(QSize(1050, 550))
        self.centralwidget.setStyleSheet(u"")
        self.gridLayout_5 = QGridLayout(self.centralwidget)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.widget_main_window = QWidget(self.centralwidget)
        self.widget_main_window.setObjectName(u"widget_main_window")
        self.widget_main_window.setMinimumSize(QSize(950, 525))
        self.widget_main_window.setMaximumSize(QSize(950, 500))
        self.widget_main_window.setStyleSheet(u"#widget_main_window {\n"
"background-image: url(:/data/background/main_back.jpg);\n"
"}\n"
"\n"
"\n"
"\n"
"#stackedWidget {\n"
"background-image: url(:/data/background/main_back.jpg);\n"
"}")
        self.verticalLayout_3 = QVBoxLayout(self.widget_main_window)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.widget_main_window_child = QWidget(self.widget_main_window)
        self.widget_main_window_child.setObjectName(u"widget_main_window_child")
        self.verticalLayout = QVBoxLayout(self.widget_main_window_child)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_top_menu = QHBoxLayout()
        self.horizontalLayout_top_menu.setObjectName(u"horizontalLayout_top_menu")
        self.horizontalLayout_top_menu.setContentsMargins(-1, 10, 10, -1)
        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_top_menu.addItem(self.horizontalSpacer_6)

        self.pushButton_collapse_app = QPushButton(self.widget_main_window_child)
        self.pushButton_collapse_app.setObjectName(u"pushButton_collapse_app")
        self.pushButton_collapse_app.setMaximumSize(QSize(32, 32))
        self.pushButton_collapse_app.setStyleSheet(u"QPushButton {\n"
"    background-image: url(:/data/background/collapse_icon.png);\n"
"    background-position: center;\n"
"    background-repeat: no-repeat;\n"
"    border: none; /* \u0423\u0431\u0438\u0440\u0430\u0435\u043c \u0433\u0440\u0430\u043d\u0438\u0446\u044b */\n"
"    border-radius: 10px; /* \u0421\u043a\u0440\u0443\u0433\u043b\u044f\u0435\u043c \u0443\u0433\u043b\u044b \u043a\u043d\u043e\u043f\u043a\u0438 */\n"
"    padding: 10px; /* \u0414\u043e\u0431\u0430\u0432\u043b\u044f\u0435\u043c \u0432\u043d\u0443\u0442\u0440\u0435\u043d\u043d\u0438\u0435 \u043e\u0442\u0441\u0442\u0443\u043f\u044b */\n"
"    color: white; /* \u0423\u0441\u0442\u0430\u043d\u0430\u0432\u043b\u0438\u0432\u0430\u0435\u043c \u0446\u0432\u0435\u0442 \u0442\u0435\u043a\u0441\u0442\u0430 */\n"
"    font-size: 16px; /* \u0423\u0441\u0442\u0430\u043d\u0430\u0432\u043b\u0438\u0432\u0430\u0435\u043c \u0440\u0430\u0437\u043c\u0435\u0440 \u0448\u0440\u0438\u0444\u0442\u0430 */\n"
"    font-weight: bold; /* \u0423\u0441\u0442\u0430\u043d\u0430"
                        "\u0432\u043b\u0438\u0432\u0430\u0435\u043c \u0436\u0438\u0440\u043d\u044b\u0439 \u0448\u0440\u0438\u0444\u0442 */\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: rgba(255, 255, 255, 0.2); /* \u0414\u043e\u0431\u0430\u0432\u043b\u044f\u0435\u043c \u044d\u0444\u0444\u0435\u043a\u0442 \u043f\u0440\u0438 \u043d\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0438 */\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: rgba(255, 255, 255, 0.4); /* \u0414\u043e\u0431\u0430\u0432\u043b\u044f\u0435\u043c \u044d\u0444\u0444\u0435\u043a\u0442 \u043f\u0440\u0438 \u043d\u0430\u0436\u0430\u0442\u0438\u0438 */\n"
"}\n"
"")

        self.horizontalLayout_top_menu.addWidget(self.pushButton_collapse_app)

        self.pushButton_close_app = QPushButton(self.widget_main_window_child)
        self.pushButton_close_app.setObjectName(u"pushButton_close_app")
        self.pushButton_close_app.setMinimumSize(QSize(32, 32))
        self.pushButton_close_app.setMaximumSize(QSize(32, 32))
        self.pushButton_close_app.setStyleSheet(u"QPushButton {\n"
"    background-image: url(:/data/background/close_icon.png);\n"
"    background-position: center;\n"
"    background-repeat: no-repeat;\n"
"    border: none; /* \u0423\u0431\u0438\u0440\u0430\u0435\u043c \u0433\u0440\u0430\u043d\u0438\u0446\u044b */\n"
"    border-radius: 10px; /* \u0421\u043a\u0440\u0443\u0433\u043b\u044f\u0435\u043c \u0443\u0433\u043b\u044b \u043a\u043d\u043e\u043f\u043a\u0438 */\n"
"    padding: 10px; /* \u0414\u043e\u0431\u0430\u0432\u043b\u044f\u0435\u043c \u0432\u043d\u0443\u0442\u0440\u0435\u043d\u043d\u0438\u0435 \u043e\u0442\u0441\u0442\u0443\u043f\u044b */\n"
"    color: white; /* \u0423\u0441\u0442\u0430\u043d\u0430\u0432\u043b\u0438\u0432\u0430\u0435\u043c \u0446\u0432\u0435\u0442 \u0442\u0435\u043a\u0441\u0442\u0430 */\n"
"    font-size: 16px; /* \u0423\u0441\u0442\u0430\u043d\u0430\u0432\u043b\u0438\u0432\u0430\u0435\u043c \u0440\u0430\u0437\u043c\u0435\u0440 \u0448\u0440\u0438\u0444\u0442\u0430 */\n"
"    font-weight: bold; /* \u0423\u0441\u0442\u0430\u043d\u0430"
                        "\u0432\u043b\u0438\u0432\u0430\u0435\u043c \u0436\u0438\u0440\u043d\u044b\u0439 \u0448\u0440\u0438\u0444\u0442 */\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: rgba(255, 255, 255, 0.2); /* \u0414\u043e\u0431\u0430\u0432\u043b\u044f\u0435\u043c \u044d\u0444\u0444\u0435\u043a\u0442 \u043f\u0440\u0438 \u043d\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0438 */\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: rgba(255, 255, 255, 0.4); /* \u0414\u043e\u0431\u0430\u0432\u043b\u044f\u0435\u043c \u044d\u0444\u0444\u0435\u043a\u0442 \u043f\u0440\u0438 \u043d\u0430\u0436\u0430\u0442\u0438\u0438 */\n"
"}\n"
"")

        self.horizontalLayout_top_menu.addWidget(self.pushButton_close_app)


        self.verticalLayout.addLayout(self.horizontalLayout_top_menu)

        self.stackedWidget = QStackedWidget(self.widget_main_window_child)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setMinimumSize(QSize(0, 0))
        self.stackedWidget.setMaximumSize(QSize(10000, 10000))
        self.stackedWidget.setStyleSheet(u"")
        self.login_page = QWidget()
        self.login_page.setObjectName(u"login_page")
        self.gridLayout_3 = QGridLayout(self.login_page)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer, 0, 2, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer_2, 0, 0, 1, 1)

        self.widget_login = QWidget(self.login_page)
        self.widget_login.setObjectName(u"widget_login")
        self.widget_login.setMinimumSize(QSize(450, 0))
        self.widget_login.setMaximumSize(QSize(450, 16777215))
        self.widget_login.setStyleSheet(u"#widget_login {\n"
"	\n"
"	background-image: url(:/data/background/login_back.jpg);\n"
"	border-radius: 50px;\n"
"}\n"
"\n"
"/* \u0421\u0442\u0438\u043b\u044c \u0434\u043b\u044f \u043a\u043d\u043e\u043f\u043a\u0438 \u0441 \u0441\u0438\u043d\u0438\u043c \u0446\u0432\u0435\u0442\u043e\u043c */\n"
"QPushButton {\n"
"    background-color: #FF77A3; \n"
"    border: 2px solid #FF77A3;;\n"
"    color: rgb(181, 255, 214); \n"
"    padding: 10px 20px; /* \u0412\u043d\u0443\u0442\u0440\u0435\u043d\u043d\u0438\u0435 \u043e\u0442\u0441\u0442\u0443\u043f\u044b */\n"
"    text-align: center;\n"
"    font-size: 24px;\n"
"	font-weight: bold; /* \u0416\u0438\u0440\u043d\u044b\u0439 \u0442\u0435\u043a\u0441\u0442 */\n"
"    border-radius: 10px; /* \u0417\u0430\u043a\u0440\u0443\u0433\u043b\u0435\u043d\u043d\u044b\u0435 \u0443\u0433\u043b\u044b */\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #FF4DA3; /* \u0411\u043e\u043b\u0435\u0435 \u0442\u0451\u043c\u043d\u044b\u0439 \u0441\u0438\u043d\u0438\u0439 \u043f\u0440"
                        "\u0438 \u043d\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0438 */\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color:  #FF00A3; /* \u0415\u0449\u0451 \u0431\u043e\u043b\u0435\u0435 \u0442\u0451\u043c\u043d\u044b\u0439 \u0441\u0438\u043d\u0438\u0439 \u043f\u0440\u0438 \u043d\u0430\u0436\u0430\u0442\u0438\u0438 */\n"
"}\n"
"QPushButton:disabled {\n"
"    background-color: #D3D3D3; /* \u0421\u0435\u0440\u044b\u0439 \u0446\u0432\u0435\u0442 \u0444\u043e\u043d\u0430 */\n"
"    border: 2px solid #A9A9A9; /* \u0421\u0435\u0440\u044b\u0439 \u0446\u0432\u0435\u0442 \u0433\u0440\u0430\u043d\u0438\u0446\u044b */\n"
"    color: #A9A9A9; /* \u0421\u0435\u0440\u044b\u0439 \u0446\u0432\u0435\u0442 \u0442\u0435\u043a\u0441\u0442\u0430 */\n"
"}\n"
"\n"
"QLabel {\n"
"    color: rgb(19, 255, 19);\n"
"    text-decoration: underline;\n"
"    font-size: 18px; /* \u0420\u0430\u0437\u043c\u0435\u0440 \u0442\u0435\u043a\u0441\u0442\u0430 */\n"
"}\n"
"QLabel:hover {\n"
"    color: rgb(0, 255, 255); /* \u0426\u0432\u0435\u0442"
                        " \u043f\u0440\u0438 \u043d\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0438 */\n"
"    font-size: 20px; /* \u0418\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u0435 \u0440\u0430\u0437\u043c\u0435\u0440\u0430 \u043f\u0440\u0438 \u043d\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0438 (\u043e\u043f\u0446\u0438\u043e\u043d\u0430\u043b\u044c\u043d\u043e) */\n"
"    text-decoration: none; /* \u0423\u0431\u0438\u0440\u0430\u0435\u043c \u043f\u043e\u0434\u0447\u0435\u0440\u043a\u0438\u0432\u0430\u043d\u0438\u0435 \u043f\u0440\u0438 \u043d\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0438 */\n"
"}\n"
"\n"
"\n"
"#pushButton_error_info {\n"
"    background-color: rgba(220, 50, 50, 0.9); /* Slightly lighter semi-transparent red background */\n"
"    color: white; /* White text */\n"
"    border: 2px solid #b22222; /* Firebrick color for the border */\n"
"    border-radius: 5px; /* Rounded corners */\n"
"    padding: 10px; /* Internal padding */\n"
"    font-weight: bold; /* Bold font */\n"
"    text-align: center; /* Centered te"
                        "xt */\n"
"}\n"
"\n"
"/* Optional: Hover state for button */\n"
"#pushButton_error_info:hover {\n"
"    background-color: rgba(220, 50, 50, 1); /* Fully opaque red on hover */\n"
"}\n"
"\n"
"/* Optional: Pressed state for button */\n"
"#pushButton_error_info:pressed {\n"
"    background-color: rgba(180, 30, 30, 0.8); /* Darker red on press */\n"
"}\n"
"")
        self.verticalLayout_8 = QVBoxLayout(self.widget_login)
        self.verticalLayout_8.setSpacing(0)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer_4, 1, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 50, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_4.addItem(self.verticalSpacer, 0, 1, 1, 1)

        self.pushButton_login = QPushButton(self.widget_login)
        self.pushButton_login.setObjectName(u"pushButton_login")

        self.gridLayout_4.addWidget(self.pushButton_login, 5, 1, 1, 1)

        self.label_reset_password = QLabel(self.widget_login)
        self.label_reset_password.setObjectName(u"label_reset_password")
        self.label_reset_password.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_4.addWidget(self.label_reset_password, 4, 1, 1, 1)

        self.lineEdit_password = QLineEdit(self.widget_login)
        self.lineEdit_password.setObjectName(u"lineEdit_password")
        self.lineEdit_password.setMinimumSize(QSize(250, 0))
        self.lineEdit_password.setMaximumSize(QSize(300, 16777215))
        self.lineEdit_password.setStyleSheet(u"/* Modern Style QLineEdit */\n"
".QLineEdit {\n"
"  border: 2px solid #ccc;\n"
"  background-color: #f9f9f9;\n"
"  color: #333;\n"
"  padding: 10px;\n"
"  font-size: 16px;\n"
"  border-radius: 15px; /* Adjust the value to control the corner smoothness */\n"
"}\n"
"\n"
".QLineEdit:focus {\n"
"  outline: none;\n"
"  border-color: #4287f5;\n"
"  background-color: #fff;\n"
"}\n"
"\n"
".QLineEdit::placeholder {\n"
"  color: #999;\n"
"}\n"
"\n"
".QLineEdit:hover {\n"
"  border-color: #999;\n"
"}\n"
"")
        self.lineEdit_password.setEchoMode(QLineEdit.EchoMode.Password)

        self.gridLayout_4.addWidget(self.lineEdit_password, 2, 1, 1, 1)

        self.lineEdit_nickname = QLineEdit(self.widget_login)
        self.lineEdit_nickname.setObjectName(u"lineEdit_nickname")
        self.lineEdit_nickname.setMinimumSize(QSize(250, 0))
        self.lineEdit_nickname.setMaximumSize(QSize(300, 16777215))
        self.lineEdit_nickname.setStyleSheet(u"/* Modern Style QLineEdit */\n"
".QLineEdit {\n"
"  border: 2px solid #ccc;\n"
"  background-color: #f9f9f9;\n"
"  color: #333;\n"
"  padding: 10px;\n"
"  font-size: 16px;\n"
"  border-radius: 15px; /* Adjust the value to control the corner smoothness */\n"
"}\n"
"\n"
".QLineEdit:focus {\n"
"  outline: none;\n"
"  border-color: #4287f5;\n"
"  background-color: #fff;\n"
"}\n"
"\n"
".QLineEdit::placeholder {\n"
"  color: #999;\n"
"}\n"
"\n"
".QLineEdit:hover {\n"
"  border-color: #999;\n"
"}\n"
"")

        self.gridLayout_4.addWidget(self.lineEdit_nickname, 1, 1, 1, 1)

        self.label_creat_account = QLabel(self.widget_login)
        self.label_creat_account.setObjectName(u"label_creat_account")
        self.label_creat_account.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_4.addWidget(self.label_creat_account, 3, 1, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer_3, 1, 2, 1, 1)


        self.verticalLayout_8.addLayout(self.gridLayout_4)

        self.widget_3 = QWidget(self.widget_login)
        self.widget_3.setObjectName(u"widget_3")
        self.widget_3.setEnabled(True)
        self.widget_3.setMinimumSize(QSize(250, 150))
        self.widget_3.setMaximumSize(QSize(800, 50))
        self.widget_3.setStyleSheet(u"")
        self.gridLayout_6 = QGridLayout(self.widget_3)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.gridLayout_6.setContentsMargins(-1, 0, -1, -1)
        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_6.addItem(self.verticalSpacer_2, 1, 0, 1, 1)

        self.pushButton_error_info = QPushButton(self.widget_3)
        self.pushButton_error_info.setObjectName(u"pushButton_error_info")
        self.pushButton_error_info.setEnabled(True)

        self.gridLayout_6.addWidget(self.pushButton_error_info, 0, 0, 1, 1)


        self.verticalLayout_8.addWidget(self.widget_3)


        self.gridLayout_3.addWidget(self.widget_login, 0, 1, 1, 1)

        self.stackedWidget.addWidget(self.login_page)
        self.choose_server_page = QWidget()
        self.choose_server_page.setObjectName(u"choose_server_page")
        self.verticalLayout_2 = QVBoxLayout(self.choose_server_page)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(-1, -1, -1, 25)
        self.widget = QWidget(self.choose_server_page)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.widget_4 = QWidget(self.widget)
        self.widget_4.setObjectName(u"widget_4")

        self.horizontalLayout.addWidget(self.widget_4)

        self.pushButton_logout = QPushButton(self.widget)
        self.pushButton_logout.setObjectName(u"pushButton_logout")
        self.pushButton_logout.setMinimumSize(QSize(64, 64))
        self.pushButton_logout.setMaximumSize(QSize(64, 64))
        self.pushButton_logout.setStyleSheet(u"QPushButton {\n"
"    background-image: url(:/data/background/logout.png);\n"
"    background-position: center;\n"
"    background-repeat: no-repeat;\n"
"    border: none; /* \u0423\u0431\u0438\u0440\u0430\u0435\u043c \u0433\u0440\u0430\u043d\u0438\u0446\u044b */\n"
"    border-radius: 10px; /* \u0421\u043a\u0440\u0443\u0433\u043b\u044f\u0435\u043c \u0443\u0433\u043b\u044b \u043a\u043d\u043e\u043f\u043a\u0438 */\n"
"    padding: 10px; /* \u0414\u043e\u0431\u0430\u0432\u043b\u044f\u0435\u043c \u0432\u043d\u0443\u0442\u0440\u0435\u043d\u043d\u0438\u0435 \u043e\u0442\u0441\u0442\u0443\u043f\u044b */\n"
"    color: white; /* \u0423\u0441\u0442\u0430\u043d\u0430\u0432\u043b\u0438\u0432\u0430\u0435\u043c \u0446\u0432\u0435\u0442 \u0442\u0435\u043a\u0441\u0442\u0430 */\n"
"    font-size: 16px; /* \u0423\u0441\u0442\u0430\u043d\u0430\u0432\u043b\u0438\u0432\u0430\u0435\u043c \u0440\u0430\u0437\u043c\u0435\u0440 \u0448\u0440\u0438\u0444\u0442\u0430 */\n"
"    font-weight: bold; /* \u0423\u0441\u0442\u0430\u043d\u0430\u0432"
                        "\u043b\u0438\u0432\u0430\u0435\u043c \u0436\u0438\u0440\u043d\u044b\u0439 \u0448\u0440\u0438\u0444\u0442 */\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: rgba(255, 255, 255, 0.2); /* \u0414\u043e\u0431\u0430\u0432\u043b\u044f\u0435\u043c \u044d\u0444\u0444\u0435\u043a\u0442 \u043f\u0440\u0438 \u043d\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0438 */\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: rgba(255, 255, 255, 0.4); /* \u0414\u043e\u0431\u0430\u0432\u043b\u044f\u0435\u043c \u044d\u0444\u0444\u0435\u043a\u0442 \u043f\u0440\u0438 \u043d\u0430\u0436\u0430\u0442\u0438\u0438 */\n"
"}\n"
"")

        self.horizontalLayout.addWidget(self.pushButton_logout)

        self.pushButton_settings = QPushButton(self.widget)
        self.pushButton_settings.setObjectName(u"pushButton_settings")
        self.pushButton_settings.setMinimumSize(QSize(64, 64))
        self.pushButton_settings.setMaximumSize(QSize(64, 64))
        self.pushButton_settings.setAutoFillBackground(False)
        self.pushButton_settings.setStyleSheet(u"QPushButton {\n"
"    background-image: url(:/data/background/settings.png);\n"
"    background-position: center;\n"
"    background-repeat: no-repeat;\n"
"    border: none; /* \u0423\u0431\u0438\u0440\u0430\u0435\u043c \u0433\u0440\u0430\u043d\u0438\u0446\u044b */\n"
"    border-radius: 10px; /* \u0421\u043a\u0440\u0443\u0433\u043b\u044f\u0435\u043c \u0443\u0433\u043b\u044b \u043a\u043d\u043e\u043f\u043a\u0438 */\n"
"    padding: 10px; /* \u0414\u043e\u0431\u0430\u0432\u043b\u044f\u0435\u043c \u0432\u043d\u0443\u0442\u0440\u0435\u043d\u043d\u0438\u0435 \u043e\u0442\u0441\u0442\u0443\u043f\u044b */\n"
"    color: white; /* \u0423\u0441\u0442\u0430\u043d\u0430\u0432\u043b\u0438\u0432\u0430\u0435\u043c \u0446\u0432\u0435\u0442 \u0442\u0435\u043a\u0441\u0442\u0430 */\n"
"    font-size: 16px; /* \u0423\u0441\u0442\u0430\u043d\u0430\u0432\u043b\u0438\u0432\u0430\u0435\u043c \u0440\u0430\u0437\u043c\u0435\u0440 \u0448\u0440\u0438\u0444\u0442\u0430 */\n"
"    font-weight: bold; /* \u0423\u0441\u0442\u0430\u043d\u0430"
                        "\u0432\u043b\u0438\u0432\u0430\u0435\u043c \u0436\u0438\u0440\u043d\u044b\u0439 \u0448\u0440\u0438\u0444\u0442 */\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: rgba(255, 255, 255, 0.2); /* \u0414\u043e\u0431\u0430\u0432\u043b\u044f\u0435\u043c \u044d\u0444\u0444\u0435\u043a\u0442 \u043f\u0440\u0438 \u043d\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0438 */\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: rgba(255, 255, 255, 0.4); /* \u0414\u043e\u0431\u0430\u0432\u043b\u044f\u0435\u043c \u044d\u0444\u0444\u0435\u043a\u0442 \u043f\u0440\u0438 \u043d\u0430\u0436\u0430\u0442\u0438\u0438 */\n"
"}\n"
"")
        self.pushButton_settings.setIconSize(QSize(160, 160))
        self.pushButton_settings.setFlat(True)

        self.horizontalLayout.addWidget(self.pushButton_settings)


        self.verticalLayout_2.addWidget(self.widget)

        self.scrollArea = QScrollArea(self.choose_server_page)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setMinimumSize(QSize(0, 350))
        self.scrollArea.setMaximumSize(QSize(16777215, 350))
        self.scrollArea.setStyleSheet(u"#scrollArea, #scrollAreaWidgetContents{\n"
"\n"
"background-color: rgba(255, 255, 255, 0);  /* \u041f\u043e\u043b\u043d\u043e\u0441\u0442\u044c\u044e \u043f\u0440\u043e\u0437\u0440\u0430\u0447\u043d\u044b\u0439 \u0444\u043e\u043d */\n"
"border: none; /* \u0423\u0431\u0438\u0440\u0430\u0435\u0442 \u0433\u0440\u0430\u043d\u0438\u0446\u0443 \u043a\u043d\u043e\u043f\u043a\u0438 */\n"
"}\n"
"\n"
"\n"
"    QScrollBar:horizontal {\n"
"        border: none; /* \u0423\u0431\u0438\u0440\u0430\u0435\u043c \u0433\u0440\u0430\u043d\u0438\u0446\u044b */\n"
"        background: rgba(0, 51, 102, 200); /* \u0422\u0435\u043c\u043d\u043e-\u0441\u0438\u043d\u0438\u0439 \u0444\u043e\u043d \u0434\u043b\u044f \u0433\u043e\u0440\u0438\u0437\u043e\u043d\u0442\u0430\u043b\u044c\u043d\u043e\u0439 \u043f\u043e\u043b\u043e\u0441\u044b */\n"
"        height: 10px; /* \u0412\u044b\u0441\u043e\u0442\u0430 \u043f\u043e\u043b\u043e\u0441\u044b \u043f\u0440\u043e\u043a\u0440\u0443\u0442\u043a\u0438 */\n"
"        margin: 0px 22px; /* \u041e\u0442"
                        "\u0441\u0442\u0443\u043f\u044b \u0434\u043b\u044f \u0443\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u044f \u043a\u043d\u043e\u043f\u043a\u0430\u043c\u0438 */\n"
"    }\n"
"\n"
"    QScrollBar::handle:horizontal {\n"
"        background: rgba(0, 76, 153, 200); /* \u0411\u043e\u043b\u0435\u0435 \u0441\u0432\u0435\u0442\u043b\u044b\u0439 \u0442\u0435\u043c\u043d\u043e-\u0441\u0438\u043d\u0438\u0439 \u0434\u043b\u044f \u043f\u043e\u043b\u0437\u0443\u043d\u043a\u0430 */\n"
"        min-width: 20px; /* \u041c\u0438\u043d\u0438\u043c\u0430\u043b\u044c\u043d\u0430\u044f \u0448\u0438\u0440\u0438\u043d\u0430 \u043f\u043e\u043b\u0437\u0443\u043d\u043a\u0430 */\n"
"        border-radius: 5px; /* \u0421\u043a\u0440\u0443\u0433\u043b\u0435\u043d\u0438\u0435 \u0443\u0433\u043b\u043e\u0432 \u043f\u043e\u043b\u0437\u0443\u043d\u043a\u0430 */\n"
"    }\n"
"\n"
"    QScrollBar::handle:horizontal:hover {\n"
"        background: rgba(0, 102, 204, 200); /* \u0421\u0432\u0435\u0442\u043b\u044b\u0439 \u0441\u0438\u043d\u0438\u0439"
                        " \u043f\u0440\u0438 \u043d\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0438 */\n"
"    }\n"
"\n"
"    QScrollBar::add-line:horizontal,\n"
"    QScrollBar::sub-line:horizontal {\n"
"        background: none; /* \u0423\u0431\u0438\u0440\u0430\u0435\u043c \u0444\u043e\u043d \u0434\u043b\u044f \u0441\u0442\u0440\u0435\u043b\u043e\u043a */\n"
"        border: none; /* \u0423\u0431\u0438\u0440\u0430\u0435\u043c \u0433\u0440\u0430\u043d\u0438\u0446\u044b \u0434\u043b\u044f \u0441\u0442\u0440\u0435\u043b\u043e\u043a */\n"
"    }\n"
"\n"
"    QScrollBar::left-arrow:horizontal,\n"
"    QScrollBar::right-arrow:horizontal {\n"
"        background: none; /* \u0423\u0431\u0438\u0440\u0430\u0435\u043c \u0444\u043e\u043d \u0434\u043b\u044f \u0441\u0442\u0440\u0435\u043b\u043e\u043a */\n"
"        width: 0px; /* \u0423\u0431\u0438\u0440\u0430\u0435\u043c \u0448\u0438\u0440\u0438\u043d\u0443 \u0441\u0442\u0440\u0435\u043b\u043e\u043a */\n"
"        height: 0px; /* \u0423\u0431\u0438\u0440\u0430\u0435\u043c \u0432\u044b\u0441\u043e"
                        "\u0442\u0443 \u0441\u0442\u0440\u0435\u043b\u043e\u043a */\n"
"    }\n"
"\n"
"    QScrollBar::add-page:horizontal,\n"
"    QScrollBar::sub-page:horizontal {\n"
"        background: none; /* \u0423\u0431\u0438\u0440\u0430\u0435\u043c \u0444\u043e\u043d \u0434\u043b\u044f \u043e\u0431\u043b\u0430\u0441\u0442\u0438 \u043f\u0440\u043e\u043a\u0440\u0443\u0442\u043a\u0438 */\n"
"    }")
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 6180, 340))
        self.horizontalLayout_2 = QHBoxLayout(self.scrollAreaWidgetContents)
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(-1, 0, -1, 0)
        self.pushButton_2 = QPushButton(self.scrollAreaWidgetContents)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setMinimumSize(QSize(150, 200))
        self.pushButton_2.setMaximumSize(QSize(200, 300))

        self.horizontalLayout_2.addWidget(self.pushButton_2)

        self.pushButton = QPushButton(self.scrollAreaWidgetContents)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setMinimumSize(QSize(6000, 200))
        self.pushButton.setMaximumSize(QSize(6000, 300))
        self.pushButton.setAutoRepeat(False)

        self.horizontalLayout_2.addWidget(self.pushButton)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_5)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_2.addWidget(self.scrollArea)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_3)

        self.stackedWidget.addWidget(self.choose_server_page)
        self.server_settings_page = QWidget()
        self.server_settings_page.setObjectName(u"server_settings_page")
        self.pushButton_5 = QPushButton(self.server_settings_page)
        self.pushButton_5.setObjectName(u"pushButton_5")
        self.pushButton_5.setGeometry(QRect(240, 10, 500, 500))
        self.pushButton_5.setMinimumSize(QSize(500, 500))
        self.stackedWidget.addWidget(self.server_settings_page)
        self.launcher_settings_page = QWidget()
        self.launcher_settings_page.setObjectName(u"launcher_settings_page")
        self.pushButton_delete_skin = QPushButton(self.launcher_settings_page)
        self.pushButton_delete_skin.setObjectName(u"pushButton_delete_skin")
        self.pushButton_delete_skin.setGeometry(QRect(745, 261, 152, 46))
        self.pushButton_delete_skin.setStyleSheet(u"QPushButton {\n"
"  background-color: #FF0000; /* Red color */\n"
"  border: none;\n"
"  border-radius: 30px;\n"
"  padding: 12px 24px;\n"
"  color: #FFFFFF;\n"
"  font-weight: bold;\n"
"  text-align: center;\n"
"  text-decoration: none;\n"
"  font-size: 16px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"  background-color: #CC0000; /* Darker red on hover */\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"  background-color: #990000; /* Even darker red when pressed */\n"
"  border: 1px solid #660000; /* Dark border when pressed */\n"
"}\n"
"")
        self.pushButton_delete_cape = QPushButton(self.launcher_settings_page)
        self.pushButton_delete_cape.setObjectName(u"pushButton_delete_cape")
        self.pushButton_delete_cape.setGeometry(QRect(745, 346, 158, 46))
        self.pushButton_delete_cape.setStyleSheet(u"QPushButton {\n"
"  background-color: #FF0000; /* Red color */\n"
"  border: none;\n"
"  border-radius: 30px;\n"
"  padding: 12px 24px;\n"
"  color: #FFFFFF;\n"
"  font-weight: bold;\n"
"  text-align: center;\n"
"  text-decoration: none;\n"
"  font-size: 16px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"  background-color: #CC0000; /* Darker red on hover */\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"  background-color: #990000; /* Even darker red when pressed */\n"
"  border: 1px solid #660000; /* Dark border when pressed */\n"
"}\n"
"")
        self.progressBar = QProgressBar(self.launcher_settings_page)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setGeometry(QRect(300, 210, 108, 24))
        self.progressBar.setValue(24)
        self.groupBox = QGroupBox(self.launcher_settings_page)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(300, 240, 122, 88))
        self.groupBox.setStyleSheet(u"/* Custom Style QGroupBox */\n"
"QGroupBox {\n"
"  font-size: 16px;\n"
"  border: 2px solid #4287f5; /* Border color for the group box */\n"
"  border-radius: 8px; /* Border radius for rounded corners */\n"
"  margin-top: 10px; /* Adjust margin as needed */\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"  subcontrol-origin: margin;\n"
"  subcontrol-position: top center;\n"
"  padding: 0 5px; /* Padding for the title text */\n"
"}\n"
"\n"
"/* Apply the style for the child QRadioButton inside the QGroupBox */\n"
"QGroupBox QRadioButton::indicator {\n"
"  width: 20px;\n"
"  height: 20px;\n"
"  border-radius: 10px; /* Make the indicator circular */\n"
"}\n"
"\n"
"QGroupBox QRadioButton::indicator:unchecked {\n"
"  border: 2px solid #ccc;\n"
"  background-color: #f9f9f9;\n"
"}\n"
"\n"
"QGroupBox QRadioButton::indicator:checked {\n"
"  border: 2px solid #4287f5;\n"
"  background-color: #4287f5;\n"
"}\n"
"\n"
"QGroupBox QRadioButton::indicator:hover {\n"
"  border: 2px solid #999;\n"
"}\n"
"\n"
"QGroupBox QRadioButton::indica"
                        "tor:checked:hover {\n"
"  background-color: #3264ad;\n"
"}\n"
"")
        self.gridLayout_2 = QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.radioButton_male = QRadioButton(self.groupBox)
        self.radioButton_male.setObjectName(u"radioButton_male")
        self.radioButton_male.setStyleSheet(u"/* Custom Style QCheckBox and QRadioButton */\n"
"QCheckBox, QRadioButton {\n"
"  spacing: 5px;\n"
"  font-size: 16px;\n"
"}\n"
"\n"
"QCheckBox::indicator, QRadioButton::indicator {\n"
"  width: 20px;\n"
"  height: 20px;\n"
"  border-radius: 10px; /* Set border-radius to half of width/height for a circular shape */\n"
"}\n"
"\n"
"QCheckBox::indicator:unchecked, QRadioButton::indicator:unchecked {\n"
"  border: 2px solid #ccc;\n"
"  background-color: #f9f9f9;\n"
"}\n"
"\n"
"QCheckBox::indicator:checked, QRadioButton::indicator:checked {\n"
"  border: 2px solid #4287f5;\n"
"  background-color: #4287f5;\n"
"}\n"
"\n"
"QCheckBox::indicator:hover, QRadioButton::indicator:hover {\n"
"  border: 2px solid #999;\n"
"}\n"
"\n"
"QCheckBox::indicator:checked:hover, QRadioButton::indicator:checked:hover {\n"
"  background-color: #3264ad;\n"
"}\n"
"")
        self.radioButton_male.setChecked(True)

        self.verticalLayout_6.addWidget(self.radioButton_male)

        self.radioButton_female = QRadioButton(self.groupBox)
        self.radioButton_female.setObjectName(u"radioButton_female")
        self.radioButton_female.setStyleSheet(u"/* Custom Style QCheckBox and QRadioButton */\n"
"QCheckBox, QRadioButton {\n"
"  spacing: 5px;\n"
"  font-size: 16px;\n"
"}\n"
"\n"
"QCheckBox::indicator, QRadioButton::indicator {\n"
"  width: 20px;\n"
"  height: 20px;\n"
"  border-radius: 10px; /* Set border-radius to half of width/height for a circular shape */\n"
"}\n"
"\n"
"QCheckBox::indicator:unchecked, QRadioButton::indicator:unchecked {\n"
"  border: 2px solid #ccc;\n"
"  background-color: #f9f9f9;\n"
"}\n"
"\n"
"QCheckBox::indicator:checked, QRadioButton::indicator:checked {\n"
"  border: 2px solid #4287f5;\n"
"  background-color: #4287f5;\n"
"}\n"
"\n"
"QCheckBox::indicator:hover, QRadioButton::indicator:hover {\n"
"  border: 2px solid #999;\n"
"}\n"
"\n"
"QCheckBox::indicator:checked:hover, QRadioButton::indicator:checked:hover {\n"
"  background-color: #3264ad;\n"
"}\n"
"")

        self.verticalLayout_6.addWidget(self.radioButton_female)


        self.gridLayout_2.addLayout(self.verticalLayout_6, 0, 0, 1, 1)

        self.pushButton_choose_cape = QPushButton(self.launcher_settings_page)
        self.pushButton_choose_cape.setObjectName(u"pushButton_choose_cape")
        self.pushButton_choose_cape.setGeometry(QRect(500, 334, 200, 70))
        self.pushButton_choose_cape.setMinimumSize(QSize(200, 70))
        self.pushButton_choose_cape.setStyleSheet(u"QPushButton {\n"
"  background-color: #3A92F7;\n"
"  border: none;\n"
"  border-radius: 30px;\n"
"  padding: 12px 24px;\n"
"  color: #FFFFFF;\n"
"  font-weight: bold;\n"
"  text-align: center;\n"
"  text-decoration: none;\n"
"  font-size: 16px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"  background-color: #303EF7;\n"
"}\n"
"\n"
"\n"
"QPushButton:pressed {\n"
"  background-color: #1000F7;\n"
"  border: 1px solid #00274D;\n"
"}\n"
"")
        self.pushButton_choose_skin = QPushButton(self.launcher_settings_page)
        self.pushButton_choose_skin.setObjectName(u"pushButton_choose_skin")
        self.pushButton_choose_skin.setGeometry(QRect(500, 249, 200, 70))
        self.pushButton_choose_skin.setMinimumSize(QSize(200, 70))
        self.pushButton_choose_skin.setMaximumSize(QSize(16777215, 70))
        self.pushButton_choose_skin.setStyleSheet(u"QPushButton {\n"
"  background-color: #3A92F7;\n"
"  border: none;\n"
"  border-radius: 30px;\n"
"  padding: 12px 24px;\n"
"  color: #FFFFFF;\n"
"  font-weight: bold;\n"
"  text-align: center;\n"
"  text-decoration: none;\n"
"  font-size: 16px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"  background-color: #303EF7;\n"
"}\n"
"\n"
"\n"
"QPushButton:pressed {\n"
"  background-color: #1000F7;\n"
"  border: 1px solid #00274D;\n"
"}\n"
"")
        self.checkBox_is_install_shaders = QCheckBox(self.launcher_settings_page)
        self.checkBox_is_install_shaders.setObjectName(u"checkBox_is_install_shaders")
        self.checkBox_is_install_shaders.setGeometry(QRect(300, 357, 184, 24))
        self.checkBox_is_install_shaders.setMinimumSize(QSize(0, 0))
        self.checkBox_is_install_shaders.setMaximumSize(QSize(250, 16777215))
        self.checkBox_is_install_shaders.setStyleSheet(u"/* Custom Style QCheckBox */\n"
"QCheckBox {\n"
"  spacing: 5px;\n"
"  font-size: 16px;\n"
"\n"
"}\n"
"\n"
"QCheckBox::indicator {\n"
"  width: 20px;\n"
"  height: 20px;\n"
"}\n"
"\n"
"QCheckBox::indicator:unchecked {\n"
"  border: 2px solid #ccc;\n"
"  background-color: #f9f9f9;\n"
"}\n"
"\n"
"QCheckBox::indicator:checked {\n"
"  border: 2px solid #4287f5;\n"
"  background-color: #4287f5;\n"
"}\n"
"\n"
"QCheckBox::indicator:hover {\n"
"  border: 2px solid #999;\n"
"}\n"
"\n"
"QCheckBox::indicator:checked:hover {\n"
"  background-color: #3264ad;\n"
"}")
        self.widget_2 = QWidget(self.launcher_settings_page)
        self.widget_2.setObjectName(u"widget_2")
        self.widget_2.setGeometry(QRect(70, 30, 168, 240))
        self.verticalLayout_4 = QVBoxLayout(self.widget_2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_information_text = QLabel(self.launcher_settings_page)
        self.label_information_text.setObjectName(u"label_information_text")
        self.label_information_text.setGeometry(QRect(510, 90, 300, 50))
        self.label_information_text.setMaximumSize(QSize(300, 50))
        self.label_information_text.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.label_information_text.setStyleSheet(u"            background-color: #3498db;\n"
"            color: #ecf0f1;\n"
"            padding: 15px;\n"
"            font-size: 18px;\n"
"            border-radius: 20px;")
        self.label_information_text.setScaledContents(True)
        self.label_information_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pushButton_minecraft_dir_disable_long_tern_save = QPushButton(self.launcher_settings_page)
        self.pushButton_minecraft_dir_disable_long_tern_save.setObjectName(u"pushButton_minecraft_dir_disable_long_tern_save")
        self.pushButton_minecraft_dir_disable_long_tern_save.setGeometry(QRect(220, 80, 200, 46))
        self.pushButton_minecraft_dir_disable_long_tern_save.setMinimumSize(QSize(200, 0))
        self.pushButton_minecraft_dir_disable_long_tern_save.setMaximumSize(QSize(200, 16777215))
        self.pushButton_minecraft_dir_disable_long_tern_save.setStyleSheet(u"QPushButton {\n"
"  background-color: #3A92F7;\n"
"  border: none;\n"
"  border-radius: 5px;\n"
"  padding: 12px 24px;\n"
"  color: #FFFFFF;\n"
"  font-weight: bold;\n"
"  text-align: center;\n"
"  text-decoration: none;\n"
"  font-size: 16px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"  background-color: #303EF7;\n"
"}\n"
"\n"
"\n"
"QPushButton:pressed {\n"
"  background-color: #1000F7;\n"
"  border: 1px solid #00274D;\n"
"}\n"
"")
        self.pushButton_back_arrow = QPushButton(self.launcher_settings_page)
        self.pushButton_back_arrow.setObjectName(u"pushButton_back_arrow")
        self.pushButton_back_arrow.setGeometry(QRect(0, 10, 64, 64))
        self.pushButton_back_arrow.setMinimumSize(QSize(64, 64))
        self.pushButton_back_arrow.setMaximumSize(QSize(64, 64))
        self.pushButton_back_arrow.setStyleSheet(u"QPushButton {\n"
"    background-image: url(:/data/background/back_arrow.png);\n"
"    background-position: center;\n"
"    background-repeat: no-repeat;\n"
"    border: none; /* \u0423\u0431\u0438\u0440\u0430\u0435\u043c \u0433\u0440\u0430\u043d\u0438\u0446\u044b */\n"
"    border-radius: 10px; /* \u0421\u043a\u0440\u0443\u0433\u043b\u044f\u0435\u043c \u0443\u0433\u043b\u044b \u043a\u043d\u043e\u043f\u043a\u0438 */\n"
"    padding: 10px; /* \u0414\u043e\u0431\u0430\u0432\u043b\u044f\u0435\u043c \u0432\u043d\u0443\u0442\u0440\u0435\u043d\u043d\u0438\u0435 \u043e\u0442\u0441\u0442\u0443\u043f\u044b */\n"
"    color: white; /* \u0423\u0441\u0442\u0430\u043d\u0430\u0432\u043b\u0438\u0432\u0430\u0435\u043c \u0446\u0432\u0435\u0442 \u0442\u0435\u043a\u0441\u0442\u0430 */\n"
"    font-size: 16px; /* \u0423\u0441\u0442\u0430\u043d\u0430\u0432\u043b\u0438\u0432\u0430\u0435\u043c \u0440\u0430\u0437\u043c\u0435\u0440 \u0448\u0440\u0438\u0444\u0442\u0430 */\n"
"    font-weight: bold; /* \u0423\u0441\u0442\u0430\u043d\u0430"
                        "\u0432\u043b\u0438\u0432\u0430\u0435\u043c \u0436\u0438\u0440\u043d\u044b\u0439 \u0448\u0440\u0438\u0444\u0442 */\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: rgba(255, 255, 255, 0.2); /* \u0414\u043e\u0431\u0430\u0432\u043b\u044f\u0435\u043c \u044d\u0444\u0444\u0435\u043a\u0442 \u043f\u0440\u0438 \u043d\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0438 */\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: rgba(255, 255, 255, 0.4); /* \u0414\u043e\u0431\u0430\u0432\u043b\u044f\u0435\u043c \u044d\u0444\u0444\u0435\u043a\u0442 \u043f\u0440\u0438 \u043d\u0430\u0436\u0430\u0442\u0438\u0438 */\n"
"}\n"
"")
        self.stackedWidget.addWidget(self.launcher_settings_page)

        self.verticalLayout.addWidget(self.stackedWidget)


        self.verticalLayout_3.addWidget(self.widget_main_window_child)


        self.gridLayout_5.addWidget(self.widget_main_window, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.pushButton_collapse_app.setText("")
        self.pushButton_close_app.setText("")
        self.pushButton_login.setText(QCoreApplication.translate("MainWindow", u"\u0412\u041e\u0419\u0422\u0418", None))
        self.label_reset_password.setText(QCoreApplication.translate("MainWindow", u"\u0412\u043e\u0441\u0441\u0442\u0430\u043d\u043e\u0432\u0438\u0442\u044c \u043f\u0430\u0440\u043e\u043b\u044c", None))
        self.lineEdit_password.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u041f\u0430\u0440\u043e\u043b\u044c", None))
        self.lineEdit_nickname.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u041d\u0438\u043a \u0438\u0433\u0440\u043e\u043a\u0430", None))
        self.label_creat_account.setText(QCoreApplication.translate("MainWindow", u"\u0421\u043e\u0437\u0434\u0430\u0442\u044c \u0430\u043a\u043a\u0430\u0443\u043d\u0442", None))
        self.pushButton_error_info.setText(QCoreApplication.translate("MainWindow", u"ERROR_BUTTON", None))
        self.pushButton_logout.setText("")
        self.pushButton_settings.setText("")
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"\u0421\u0435\u0440\u0432\u0435\u0440 1", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"\u0421\u0435\u0440\u0432\u0435\u0440 2", None))
        self.pushButton_5.setText(QCoreApplication.translate("MainWindow", u"\u0418\u0413\u0420\u0410\u0422\u042c", None))
        self.pushButton_delete_skin.setText(QCoreApplication.translate("MainWindow", u"\u0423\u0434\u0430\u043b\u0438\u0442\u044c \u0441\u043a\u0438\u043d", None))
        self.pushButton_delete_cape.setText(QCoreApplication.translate("MainWindow", u"\u0423\u0434\u0430\u043b\u0438\u0442\u044c \u043f\u043b\u0430\u0449", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"\u0422\u0438\u043f \u0441\u043a\u0438\u043d\u0430", None))
        self.radioButton_male.setText(QCoreApplication.translate("MainWindow", u"\u041c\u0443\u0436\u0441\u043a\u043e\u0439", None))
        self.radioButton_female.setText(QCoreApplication.translate("MainWindow", u"\u0416\u0435\u043d\u0441\u043a\u0438\u0439", None))
        self.pushButton_choose_cape.setText(QCoreApplication.translate("MainWindow", u"\u0412\u044b\u0431\u0440\u0430\u0442\u044c \u043f\u043b\u0430\u0449", None))
        self.pushButton_choose_skin.setText(QCoreApplication.translate("MainWindow", u"\u0412\u044b\u0431\u0440\u0430\u0442\u044c \u0441\u043a\u0438\u043d", None))
        self.checkBox_is_install_shaders.setText(QCoreApplication.translate("MainWindow", u"\u0423\u0441\u0442\u0430\u043d\u043e\u0432\u0438\u0442\u044c \u0448\u0435\u0439\u0434\u0435\u0440\u044b", None))
        self.label_information_text.setText("")
        self.pushButton_minecraft_dir_disable_long_tern_save.setText(QCoreApplication.translate("MainWindow", u"\u041f\u0430\u043f\u043a\u0430 \u0441 \u0438\u0433\u0440\u043e\u0439", None))
        self.pushButton_back_arrow.setText("")
    # retranslateUi

