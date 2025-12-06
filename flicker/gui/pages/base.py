from PySide6.QtWidgets import QWidget


class FlickerPage(QWidget):
    """ Base class for all pages in the application """

    def getPageName(self) -> str:
        """ Returns the display name of the page """
        return "未命名页面"

    def getPageId(self) -> str:
        """ Returns the unique identifier of the page """
        raise NotImplementedError
