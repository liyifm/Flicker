from PySide6.QtWidgets import (
    QMainWindow, QWidget, QFrame, QVBoxLayout, QLabel,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QTimer, QEvent
from PySide6.QtGui import QKeyEvent, QColor

from flicker.utils.window import WindowUtils
from flicker.services.proactive.intent_parser import IntentParsingResult
from flicker.gui.widgets.input import AIChatInput
from flicker.gui.widgets.proactive.intents import IntentListView

from typing import Optional


class HotkeyWindow(QMainWindow):

    _instance: Optional['HotkeyWindow'] = None

    @classmethod
    def popup(cls) -> None:
        if cls._instance is None:
            cls._instance = HotkeyWindow()

        window = cls._instance
        window.show()
        WindowUtils.bringWindowToFront(window)

    @classmethod
    def setClsIntentParsingResult(cls, result: Optional[IntentParsingResult] = None) -> None:
        if cls._instance is None:
            return

        window = cls._instance
        window.setIntentParsingResult(result)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("热键设置")
        self.setFixedSize(800, 400)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.widget_intents = IntentListView(self)
        self.widget_input = AIChatInput()

        self.setupUILayout()

    def setupUILayout(self) -> None:
        inner_layout = QVBoxLayout()
        inner_widget = QFrame()
        inner_widget.setLayout(inner_layout)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.addWidget(inner_widget)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        central_widget.setStyleSheet("background-color: transparent;")

        inner_layout.setContentsMargins(20, 20, 20, 20)

        inner_layout.addWidget(self.widget_input)
        inner_layout.addWidget(self.widget_intents)
        inner_layout.addStretch()

        # 设置样式
        inner_widget.setStyleSheet("""
        QWidget {
            background-color: #FEFEFE;
            border-radius: 20px;
        }
        """)

        # 这里必须要指定一个父组件，否则阴影效果不会显示
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)          # 模糊半径
        shadow.setXOffset(0)              # X 偏移
        shadow.setYOffset(0)              # Y 偏移
        shadow.setColor(QColor("#333333"))  # 阴影颜色和透明度
        inner_widget.setGraphicsEffect(shadow)

        self.setCentralWidget(central_widget)

    def changeEvent(self, event: QEvent):
        if event.type() is QEvent.Type.WindowDeactivate:
            self.close()

        return super().changeEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.close()

        return super().keyPressEvent(event)

    def setIntentParsingResult(self, result: Optional[IntentParsingResult] = None) -> None:
        self.widget_intents.updateIntentList([] if result is None else result.intents)
