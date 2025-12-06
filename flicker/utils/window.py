import sys

from PySide6.QtWidgets import QMainWindow


class WindowUtils:
    """ Utilities for window management """

    @staticmethod
    def __win32BringWindowToFront(hwnd: int) -> None:
        """ Bring a window to front """
        import ctypes
        user32 = ctypes.windll.user32
        # user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002)  # HWND_TOPMOST
        user32.SetWindowPos(hwnd, -2, 0, 0, 0, 0, 0x0001 | 0x0002)  # HWND_NOTOPMOST
        user32.SetForegroundWindow(hwnd)
        user32.BringWindowToTop(hwnd)
        user32.SetFocus(hwnd)

    @staticmethod
    def bringWindowToFront(window: QMainWindow) -> None:
        if sys.platform == "win32":
            WindowUtils.__win32BringWindowToFront(window.winId())

        window.activateWindow()
        window.raise_()
