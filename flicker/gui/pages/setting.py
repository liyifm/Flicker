from PySide6.QtWidgets import QLabel, QPlainTextEdit, QVBoxLayout, QToolBar
from PySide6.QtGui import QFont, QIcon

from flicker.gui.pages.base import FlickerPage
from flicker.utils.settings import Settings


ERROR_STYLE = """
QLabel {
    background-color: #F46537;
    border-radius: 10px;
    color: white;
    padding: 10px;
}
"""


class SettingPage(FlickerPage):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.widget_toolbar = QToolBar()
        self.widget_editor = QPlainTextEdit()
        self.widget_editor.setFont(QFont("Consolas"))
        self.widget_editor.setPlainText(
            Settings.loadDefault().model_dump_json(indent=4, ensure_ascii=False)
        )
        self.widget_error = QLabel("")
        self.widget_error.setWordWrap(True)
        self.widget_error.setStyleSheet(ERROR_STYLE)

        action = self.widget_toolbar.addAction('保存')
        action.triggered.connect(self.onSaveSettings)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.widget_toolbar)
        main_layout.addWidget(self.widget_editor, 1)
        main_layout.addWidget(self.widget_error)

        self.widget_error.hide()
        self.setLayout(main_layout)

    def onSaveSettings(self) -> None:
        try:
            settings = Settings.model_validate_json(self.widget_editor.toPlainText())
            settings.saveAsDefault()
            self.widget_error.setText("")
            self.widget_error.hide()
        except Exception as ex:
            self.widget_error.setText(str(ex))
            self.widget_error.show()

    def getPageName(self) -> str:
        return "设置"

    def getPageId(self) -> str:
        return "#setting"
