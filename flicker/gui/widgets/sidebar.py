from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from flicker.utils.theme import getCurrentTheme


SIDEBAR_STYLE = f"""
QWidget {{
}}
"""


class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUILayout()
        self.setMaximumWidth(250)
        self.setStyleSheet(SIDEBAR_STYLE)

    def setupUILayout(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        label = QLabel("侧边栏内容")
        layout.addWidget(label)
        self.setLayout(layout)
