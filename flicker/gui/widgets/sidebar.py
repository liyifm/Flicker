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
        self.setContentsMargins(0, 0, 0, 0)

    def setupUILayout(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel("侧边栏内容")
        layout.addWidget(label)
        self.setLayout(layout)
