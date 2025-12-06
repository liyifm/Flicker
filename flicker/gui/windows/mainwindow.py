"""
主窗口组件
"""
from typing import Optional
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QSplitter,
    QHBoxLayout,
    QVBoxLayout,
    QTabWidget,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLineEdit,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QIcon, QFont


MAIN_WINDOW_STYLE = """
QMainWindow {
    background-color: #ECEFF1;
}
"""


class MainWindow(QMainWindow):
    """主窗口类"""

    _instance: Optional['MainWindow'] = None

    @classmethod
    def wakeUp(cls) -> None:
        if cls._instance is None:
            cls._instance = MainWindow()

        cls._instance.show()
        cls._instance.activateWindow()
        cls._instance.raise_()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("AI 生产力工作空间")
        self.setMinimumSize(1000, 600)
        self.setWindowIcon(QIcon(":/icons/flicker.png"))
        self.__setupLayout()
        MainWindow._instance = self

    def __setupLayout(self):
        self.setStyleSheet(MAIN_WINDOW_STYLE)
        central_widget = QSplitter(Qt.Horizontal)
        self.setCentralWidget(central_widget)
        self.setContentsMargins(20, 20, 20, 20)
        central_widget.addWidget(QLabel("侧边栏"))
        central_widget.addWidget(QLabel("侧边栏"))
