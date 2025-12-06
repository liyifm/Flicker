from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from flicker.services.proactive.intent_parser import IntentInstance
from typing import List


class IntentListView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.updateIntentList([])

    def clear(self) -> None:
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.hide()
                widget.deleteLater()

    def updateIntentList(self, intents: List[IntentInstance]) -> None:
        self.clear()
        if len(intents) == 0:
            self.main_layout.addWidget(QLabel("正在识别意图……"))
            return

        for intent in intents:
            label = QLabel(intent.name + ": " + intent.reasoning, parent=self)
            self.main_layout.addWidget(label)
