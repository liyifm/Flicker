from PySide6.QtWidgets import QTextBrowser, QVBoxLayout
from flicker.gui.pages.base import FlickerPage


ABOUT = """
# 关于弹指(Flicker)

*tba*
"""


class AboutPage(FlickerPage):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.widget_browser = QTextBrowser()
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.widget_browser)
        self.setLayout(main_layout)
        self.widget_browser.setMarkdown(ABOUT)

    def getPageName(self) -> str:
        return "关于弹指(Flicker)"

    def getPageId(self) -> str:
        return "#about"
