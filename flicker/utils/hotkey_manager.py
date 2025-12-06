from PySide6.QtCore import QObject, QThread, Signal
from enum import Enum, auto
from typing import Set, Callable, Dict
from loguru import logger

import keyboard


class HotkeyManager(QObject):

    fullScreenFlick = Signal()

    def __init__(self) -> None:
        super().__init__()

    def onFullScreenFlick(self):
        self.fullScreenFlick.emit()

    def start(self):
        keyboard.add_hotkey('alt+space', self.onFullScreenFlick, suppress=True)
