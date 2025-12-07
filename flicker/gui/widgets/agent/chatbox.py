from PySide6.QtWidgets import QWidget, QVBoxLayout


class ChatMessageContainer(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUILayout()

    def setupUILayout(self) -> None:
        layout = QVBoxLayout()
        self.setLayout(layout)


class ChatBox(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUILayout()

    def setupUILayout(self) -> None:
        layout = QVBoxLayout()
        self.setLayout(layout)
