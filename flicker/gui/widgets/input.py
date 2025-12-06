from PySide6.QtWidgets import QLineEdit


class AIChatInput(QLineEdit):
    """输入框组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("请输入内容...")
