from PySide6.QtWidgets import QTextBrowser, QVBoxLayout
from flicker.gui.pages.base import FlickerPage


class SettingPage(FlickerPage):

    def __init__(self, parent=None):
        super().__init__(parent)

    def getPageName(self) -> str:
        return "设置"

    def getPageId(self) -> str:
        return "#setting"
