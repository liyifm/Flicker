from flicker.gui.states.task import TaskState, TaskManagerState
from PySide6.QtCore import QObject
from typing import ClassVar, Optional


class GlobalState(QObject):
    """ Global gui state of flicker """

    _instance: Optional['GlobalState'] = None

    @classmethod
    def getInstance(cls) -> 'GlobalState':
        if cls._instance is not None:
            return cls._instance

        cls._instance = GlobalState()
        return cls._instance

    def __init__(self):
        super().__init__()
        self.task_manager_state = TaskManagerState()

    def submitUserMessage(self, message: str) -> None:
        self.task_manager_state.submitUserMessage(message)
