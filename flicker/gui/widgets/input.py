from PySide6.QtWidgets import QLineEdit


INPUT_STYLE = """
QLineEdit {
    border: 2px solid #cccccc;
    border-radius: 15px;
    padding: 8px;
    background-color: white;
    font-size: 12px;
}

QLineEdit :focus {
    border: 2px solid #4CAF50;
    background-color: #fafafa;
}
"""


class AIChatInput(QLineEdit):
    """输入框组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("请输入内容...")
        self.setStyleSheet(INPUT_STYLE)
