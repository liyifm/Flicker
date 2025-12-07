from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox, QStyleFactory
from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QIcon, QFont
from loguru import logger

from flicker.gui.states import GlobalState
from flicker.gui.windows.mainwindow import MainWindow
from flicker.gui.windows.hotkeywindow import HotkeyWindow
from flicker.utils.hotkey_manager import HotkeyManager
from flicker.services.proactive.intent_parser import IntentParser

from typing import Optional
from traceback import format_exc

import flicker.assets


def prepare_qt_env() -> None:
    if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)


class FlickerApp(QApplication):

    _instance: Optional['FlickerApp'] = None

    def __init__(self, args):
        super().__init__(args)
        prepare_qt_env()

        self.state = GlobalState.getInstance()

        self.__tray_icon = QSystemTrayIcon(self)
        self.__tray_menu = QMenu()
        self.__hotkey_manager = HotkeyManager()
        self.__hotkey_manager_thread = QThread()

        flicker_icon = QIcon(":/icons/flicker.png")
        self.setApplicationDisplayName("Flicker")
        self.setApplicationName("Flicker")
        self.setApplicationVersion("0.0.1")
        self.setWindowIcon(flicker_icon)
        self.setFont(QFont("Microsoft YaHei", 10))
        # self.setStyle(QStyleFactory.create("Fusion"))

        self.setUpTrayIcon()
        self.setUpHotkeyManager()
        self.setQuitOnLastWindowClosed(False)

        FlickerApp._instance = self

    @classmethod
    def getInstance(cls) -> 'FlickerApp':
        if cls._instance is None:
            raise Exception("FlickerApplication has not been initialized yet")

        return cls._instance

    @classmethod
    def sendErrorMessage(cls, title: str, message: str) -> None:
        instance = cls.getInstance()
        instance.__tray_icon.showMessage(title, message, QSystemTrayIcon.MessageIcon.Critical, 5000)

    @classmethod
    def sendInfoMessage(cls, title: str, message: str) -> None:
        instance = cls.getInstance()
        instance.__tray_icon.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 1000)

    def setUpTrayIcon(self) -> None:
        flicker_icon = QIcon(":/icons/flicker.png")
        self.__tray_icon.setIcon(flicker_icon)
        self.__tray_icon.setVisible(True)
        self.__tray_icon.setContextMenu(self.__tray_menu)

        self.__tray_menu.addAction("显示主界面", self.openMainWindow)
        self.__tray_menu.addSeparator()
        self.__tray_menu.addAction("用户设置", lambda: self.openMainWindow().openSettingPage())
        self.__tray_menu.addAction("关于弹指(Flicker)", lambda: self.openMainWindow().openAboutPage())
        self.__tray_menu.addAction("退出", self.confirmQuit)

    def setUpHotkeyManager(self) -> None:
        self.__hotkey_manager.fullScreenFlick.connect(self.onFullScreenFlick)
        self.__hotkey_manager.moveToThread(self.__hotkey_manager_thread)
        self.__hotkey_manager_thread.started.connect(self.__hotkey_manager.start)
        self.__hotkey_manager_thread.start()

    def openMainWindow(self) -> MainWindow:
        return MainWindow.wakeUp()

    def onFullScreenFlick(self):
        logger.info(f'full screen flick triggered')
        try:
            HotkeyWindow.popup()
            if not IntentParser.isParsing():
                logger.info("Starting intent parsing from screen...")
                screen = QApplication.primaryScreen()
                screenshot = screen.grabWindow().scaledToWidth(1200)
                HotkeyWindow.setClsIntentParsingResult(None)
                IntentParser.startParseScreen(screenshot, lambda result: HotkeyWindow.setClsIntentParsingResult(result))
        except Exception as ex:
            logger.error(f'failed to start screen-intent parsing')
            logger.info(format_exc())

    def confirmQuit(self) -> None:
        confirmed = QMessageBox.question(None, "确认", "确认退出？")  # type: ignore
        if confirmed == QMessageBox.StandardButton.Yes:
            self.__hotkey_manager_thread.terminate()
            self.__hotkey_manager_thread.wait()
            self.quit()
