from PySide6.QtCore import QThread, QObject, Signal
from typing import Optional


class RecallRecordServiceInstance(QObject):
    finished = Signal()

    def __init__(self) -> None:
        super().__init__()


class RecallRecordService:

    _recording_instance: Optional[RecallRecordServiceInstance] = None

    @classmethod
    def startRecording(cls) -> None:
        if cls._recording_instance is not None:
            raise RuntimeError("RecallRecordService already started")
