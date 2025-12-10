from PySide6.QtWidgets import (
    QWidget, QLabel, QHBoxLayout, QVBoxLayout, QScrollArea, QPushButton,
    QSizePolicy
)
from PySide6.QtCore import Qt
from os import startfile
from pathlib import Path
from typing import Optional


class FileView(QWidget):
    def __init__(self, path: str) -> None:
        super().__init__()
        self.path = Path(path)
        self.widget_filename = QLabel(self.path.name)
        self.widget_path = QLabel(path)
        self.widget_open = QPushButton("打开")
        self.widget_open.clicked.connect(self.openFile)
        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.widget_open)
        self.main_layout.addWidget(self.widget_filename)
        self.main_layout.addWidget(self.widget_path, 1)
        self.setLayout(self.main_layout)

    def openFile(self) -> None:
        startfile(self.path)


class FileListView(QScrollArea):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.content_layout = QVBoxLayout()
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.content_layout.setSpacing(5)
        content_widget = QWidget(self)
        content_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        content_widget.setLayout(self.content_layout)
        content_widget.setStyleSheet("")
        self.setWidget(content_widget)
        self.setWidgetResizable(True)
        self.widget_files: list[FileView] = []
        self.setFilePaths([])

    def clear(self) -> None:
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.hide()
                widget.deleteLater()

        self.widget_files.clear()

    def setFilePaths(self, paths: list[str]) -> None:
        self.clear()
        for path in paths:
            widget_file = FileView(path)
            self.content_layout.addWidget(widget_file)
            self.widget_files.append(widget_file)
