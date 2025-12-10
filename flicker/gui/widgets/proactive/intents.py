from PySide6.QtWidgets import (
    QWidget, QLabel, QSizePolicy, QScrollArea,
    QVBoxLayout, QHBoxLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from flicker.services.proactive.intent_parser import IntentInstance
from typing import List, Optional


class IconView(QLabel):
    def __init__(self, icon_path: str):
        super().__init__()
        self.icon = QIcon(icon_path)
        self.setPixmap(self.icon.pixmap(32, 32))


class IntentView(QWidget):
    """ 意图视图 """

    STYLE = """
    QWidget#intent-view:hover {
        background-color: #FFFF00;
    }

    QWidget#intent-title {
        font-size: 14px;
        font-weight: bold;
    }
    """

    def __init__(self, intent: IntentInstance, parent=None):
        super().__init__(parent)
        self.intent = intent
        self.main_layout = QHBoxLayout()
        self.right_layout = QVBoxLayout()
        self.setObjectName("intent-view")
        self.setLayout(self.main_layout)
        self.main_layout.setSpacing(10)
        self.main_layout.addWidget(IconView(':/icons/bulb.png'))
        self.main_layout.addLayout(self.right_layout, 1)

        widget_title = QLabel(self.intent.name)
        widget_title.setObjectName("intent-title")
        widget_reason = QLabel(self.intent.reasoning.replace('\n', '').strip())
        widget_reason.setWordWrap(True)
        self.right_layout.addWidget(widget_title)
        self.right_layout.addWidget(widget_reason)
        self.right_layout.setSpacing(0)
        self.setStyleSheet(self.STYLE)


class ScrollableVBoxLayout(QScrollArea):

    STYLE = """
    QScrollArea {
        border: none;
    }
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.content_layout = QVBoxLayout()
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.content_layout.setSpacing(5)
        self.main_widget = QWidget(self)
        self.main_widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        self.main_widget.setLayout(self.content_layout)
        self.main_widget.setStyleSheet("")
        self.main_widget.setFixedWidth(self.width() - 20)

        self.setWidget(self.main_widget)
        self.setWidgetResizable(True)
        self.setStyleSheet(self.STYLE)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def addWidget(self, widget: QWidget) -> None:
        self.content_layout.addWidget(widget)

    def resizeEvent(self, ev) -> None:
        super().resizeEvent(ev)
        self.main_widget.setFixedWidth(self.width() - 20)

    def clear(self) -> None:
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.hide()
                widget.deleteLater()


class IntentListView(ScrollableVBoxLayout):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.updateIntentList([])

    def updateIntentList(self, intents: List[IntentInstance]) -> None:
        self.clear()
        if len(intents) == 0:
            self.addWidget(QLabel("正在识别意图……"))
            return

        for intent in intents:
            self.addWidget(IntentView(intent))
