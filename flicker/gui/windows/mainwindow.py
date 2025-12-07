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

from flicker.gui.pages.task import TaskPage
from flicker.gui.states import GlobalState
from flicker.gui.states.task import TaskState
from flicker.gui.widgets.sidebar import Sidebar
from flicker.gui.pages.base import FlickerPage
from flicker.utils.window import WindowUtils
from typing import Optional, Callable


TABS_STYLE = """
QTabWidget::pane {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    border-top-left-radius: 15px;
    border-top-right-radius: 15px;
    margin-top: 8px;
}

QTabWidget::tab-bar {

}

QTabBar::tab {
    background-color: #f0f0f0;
    color: #666666;
    border: none;
    padding: 8px 20px;
    margin-right: 5px;
    margin-top: 10px;
    border-radius: 12px;
    min-width: 80px;
}

QTabBar::tab:selected {
    background-color: #7B618B;
    color: white;
}

QTabBar::tab:hover:!selected {
    background-color: #B1AABF;
    color: #FEFEFE;
}

QTabBar::tab:!selected {

}
"""

WINDOW_STYLE = """
QMainWindow {
    background-color: #EBE8EC;
}
"""

SPLITTER_STYLE = """
QSplitter::handle {
    background-color: rgba(0, 0, 0, 0);  /* 完全透明 */
    border: none;
}
QSplitter::handle:horizontal {
    width: 3px;  /* 保留一些宽度便于拖拽 */
}
QSplitter::handle:vertical {
    height: 3px;  /* 保留一些高度便于拖拽 */
}
"""


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
        self.setStyleSheet(WINDOW_STYLE)
        # self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self.widget_tabs = QTabWidget()
        self.widget_sidebar = Sidebar()

        self.__setUpLayout()
        self.__setUpSignals()

        self.openHomePage()
        MainWindow._instance = self

    def __setUpLayout(self):
        central_widget = QSplitter(Qt.Orientation.Horizontal)
        central_widget.setStyleSheet(SPLITTER_STYLE)
        self.setCentralWidget(central_widget)
        central_widget.addWidget(self.widget_sidebar)
        central_widget.addWidget(self.widget_tabs)

        self.widget_tabs.setStyleSheet(TABS_STYLE)

    def __setUpSignals(self):
        globalState = GlobalState.getInstance()
        globalState.task_manager_state.taskCreated.connect(self.openTaskPage)

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
        self.widget_tabs.setCurrentWidget(new_page)

    def openTaskPage(self, task_state: TaskState) -> None:
        task_page_id = f"#task-{task_state.task_id}"
        self.openPage(task_page_id, lambda: TaskPage(task_state))

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
