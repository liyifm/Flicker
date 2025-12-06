from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox, QStyleFactory
from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QIcon, QFont
from loguru import logger

from flicker.gui.windows.mainwindow import MainWindow
from flicker.gui.windows.hotkeywindow import HotkeyWindow
from flicker.utils.hotkey_manager import HotkeyManager
from flicker.services.proactive.intent_parser import IntentParser
from traceback import format_exc
import flicker.assets


def prepare_qt_env() -> None:
    if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)


class FlickerApplication(QApplication):

    def __init__(self, args):
        super().__init__(args)
        prepare_qt_env()

        flicker_icon = QIcon(":/icons/flicker.png")
        self.setApplicationDisplayName("Flicker")
        self.setApplicationName("Flicker")
        self.setApplicationVersion("0.0.1")
        self.setWindowIcon(flicker_icon)
        self.setFont(QFont("Microsoft YaHei", 10))

        self.setUpTrayIcon()
        self.setUpHotkeyManager()
        self.setQuitOnLastWindowClosed(False)

    def setUpTrayIcon(self) -> None:
        self.__tray_icon = QSystemTrayIcon(self)
        self.__tray_menu = QMenu()

        flicker_icon = QIcon(":/icons/flicker.png")
        self.__tray_icon.setIcon(flicker_icon)
        self.__tray_icon.setVisible(True)
        self.__tray_icon.setContextMenu(self.__tray_menu)

        self.__tray_menu.addAction("显示主界面", self.openMainWindow)
        self.__tray_menu.addSeparator()
        self.__tray_menu.addAction("用户设置")
        self.__tray_menu.addAction("关于弹指(Flicker)")
        self.__tray_menu.addAction("退出", self.confirmQuit)

    def setUpHotkeyManager(self) -> None:
        self.__hotkey_manager = HotkeyManager()
        self.__hotkey_manager.fullScreenFlick.connect(self.onFullScreenFlick)

        self.__hotkey_manager_thread = QThread()
        self.__hotkey_manager.moveToThread(self.__hotkey_manager_thread)
        self.__hotkey_manager_thread.started.connect(self.__hotkey_manager.start)
        self.__hotkey_manager_thread.start()

    def openMainWindow(self) -> None:
        MainWindow.wakeUp()

    def onFullScreenFlick(self):
        logger.info(f'full screen flick triggered')
        try:
            if not IntentParser.isParsing():
                HotkeyWindow.setClsIntentParsingResult(None)
                IntentParser.startParseScreen(callback=lambda result: HotkeyWindow.setClsIntentParsingResult(result))

            HotkeyWindow.popup()
        except Exception as ex:
            logger.error(f'failed to start screen-intent parsing')
            logger.info(format_exc())

    def confirmQuit(self) -> None:
        confirmed = QMessageBox.question(None, "确认", "确认退出？")  # type: ignore
        if confirmed == QMessageBox.StandardButton.Yes:
            self.__hotkey_manager_thread.terminate()
            self.__hotkey_manager_thread.wait()
            self.quit()
