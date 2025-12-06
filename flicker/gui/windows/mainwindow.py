from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QSplitter,
    QHBoxLayout,
    QVBoxLayout,
    QTabWidget,
    QLabel
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QIcon, QFont
from flicker.gui.widgets.sidebar import Sidebar
from flicker.gui.pages.base import FlickerPage
from flicker.utils.window import WindowUtils
from typing import Optional, Callable


class MainWindow(QMainWindow):
    """ Main window of tha application """

    _instance: Optional['MainWindow'] = None

    @classmethod
    def wakeUp(cls) -> 'MainWindow':
        if cls._instance is None:
            cls._instance = MainWindow()

        cls._instance.show()
        WindowUtils.bringWindowToFront(cls._instance)
        return cls._instance

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("AI 生产力工作空间")
        self.setMinimumSize(800, 500)
        self.setWindowIcon(QIcon(":/icons/flicker.png"))
        # self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self.widget_tabs = QTabWidget()
        self.widget_sidebar = Sidebar()

        self.__setupLayout()
        self.openHomePage()
        MainWindow._instance = self

    def __setupLayout(self):
        central_widget = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(central_widget)
        central_widget.addWidget(self.widget_sidebar)
        central_widget.addWidget(self.widget_tabs)

    def openPage(self, page_id: str, page_generator: Callable[[], FlickerPage]) -> None:
        for i in range(self.widget_tabs.count()):
            page = self.widget_tabs.widget(i)
            if not isinstance(page, FlickerPage):
                continue

            if page.getPageId() == page_id:
                self.widget_tabs.setCurrentIndex(i)
                return

        new_page = page_generator()
        self.widget_tabs.addTab(new_page, new_page.getPageName())

    def openHomePage(self) -> None:
        from flicker.gui.pages.home import HomePage
        home_page = HomePage()
        self.openPage(home_page.getPageId(), lambda: home_page)

    def openSettingPage(self) -> None:
        from flicker.gui.pages.setting import SettingPage
        setting_page = SettingPage()
        self.openPage(setting_page.getPageId(), lambda: setting_page)

    def openAboutPage(self) -> None:
        from flicker.gui.pages.about import AboutPage
        about_page = AboutPage()
        self.openPage(about_page.getPageId(), lambda: about_page)
