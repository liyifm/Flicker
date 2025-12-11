from flicker.gui.states.task import TaskState, TaskManagerState
from PySide6.QtCore import QObject
from typing import ClassVar, Optional
from loguru import logger


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
        try:
            self.task_manager_state = TaskManagerState.load()
        except Exception as ex:
            logger.warning(f"failed to load task manager state: {ex}")
            self.task_manager_state = TaskManagerState()

    def submitUserMessage(self, message: str) -> None:
        self.task_manager_state.submitUserMessage(message)

    def save(self) -> None:
        self.task_manager_state.save()
