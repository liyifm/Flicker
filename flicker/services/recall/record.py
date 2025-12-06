from PySide6.QtCore import QThread, QObject, Signal


class RecallRecordServiceInstance(QObject):
    finished = Signal()


class RecallRecordService:
    pass
