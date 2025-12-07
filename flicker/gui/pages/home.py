from PySide6.QtWidgets import QTextBrowser, QVBoxLayout
from flicker.gui.pages.base import FlickerPage
from flicker.gui.states import GlobalState
from flicker.gui.widgets.input import AIChatInput


class HomePage(FlickerPage):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.widget_input = AIChatInput(self)
        self.widget_input.messageSubmitted.connect(self.onMessageSubmitted)
        self.__initUILayout()

    def __initUILayout(self) -> None:
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.addStretch()
        main_layout.addWidget(self.widget_input)
        self.setLayout(main_layout)

    def getPageName(self) -> str:
        return "主页"

    def getPageId(self) -> str:
        return "#home"

    def onMessageSubmitted(self, message: str) -> None:
        GlobalState.getInstance().submitUserMessage(message)
