from flicker.services.llm.completion import ChatCompletionService, StreamCompletionChunk
from flicker.services.llm.types import ChatContext, UserMessage, AssistantMessage, SystemMessage
from flicker.utils.settings import Settings, ModelInstance
from PySide6.QtCore import QObject, Signal
from loguru import logger
from pathlib import Path
from uuid import uuid4
from enum import Enum
from typing import Any

import json


class TaskStatus(Enum):
    PENDING = 0
    RUNNING = 1


class TaskState(QObject):
    taskNameUpdated = Signal()
    taskStatusUpdated = Signal()

    def __init__(self, task_name: str, task_model: ModelInstance, mgr: 'TaskManagerState') -> None:
        super().__init__()
        self.task_id: str = str(uuid4())
        self.task_name: str = task_name
        self.task_status: TaskStatus = TaskStatus.PENDING
        self.task_context: ChatContext = ChatContext()
        self.task_model: ModelInstance = task_model
        self.task_manager: TaskManagerState = mgr

        """ indicates whether the task need to be saved to disk """
        self.need_save: bool = True

    def appendUserMessage(self, message: UserMessage) -> None:
        self.task_context.appendMessage(message)
        self.markStatusUpdated()

    def onChunkReceived(self, chunk: StreamCompletionChunk) -> None:
        # there is at least one message before starting completion
        message: AssistantMessage
        if self.task_context.messages[-1].role == 'user':
            message = AssistantMessage()
            self.task_context.messages.append(message)
        else:
            message = self.task_context.messages[-1]

        message.appendChunk(chunk.delta)
        self.markStatusUpdated()

        if chunk.finish_reason is not None:
            self.need_save = True
            self.task_manager.save()

    def markStatusUpdated(self):
        self.need_save = True
        self.taskStatusUpdated.emit()

    def start(self):
        ChatCompletionService.streamComplete(self.task_model, self.task_context, self.onChunkReceived)

    def save(self, path: Path) -> None:
        with open(path, 'w', encoding='utf-8') as f:
            task_json: dict[str, Any] = {
                "task_id": self.task_id,
                "task_name": self.task_name,
                "task_status": self.task_status.value,
                "task_context": self.task_context.model_dump(),
                "task_model": self.task_model.model_dump()
            }
            f.write(json.dumps(task_json, ensure_ascii=False, indent=4))

    @classmethod
    def load(cls, path: Path, mgr: 'TaskManagerState') -> 'TaskState':
        with open(path, 'r', encoding='utf-8') as f:
            task_json = json.loads(f.read())

        task = TaskState(
            task_name=task_json["task_name"],
            task_model=ModelInstance.model_validate(task_json["task_model"]),
            mgr=mgr
        )

        task.task_id = task_json["task_id"]
        task.task_context = ChatContext.model_validate(task_json["task_context"])

        return task


class TaskManagerState(QObject):
    taskCreated = Signal(TaskState)

    def __init__(self) -> None:
        super().__init__()
        self.tasks: list[TaskState] = []

    def submitUserMessage(self, message: str) -> TaskState:
        settings = Settings.loadDefault()
        task = TaskState(task_name=message, task_model=settings.getModelInstance(settings.default_model_alias), mgr=self)
        task.appendUserMessage(UserMessage.create(message))
        # task.task_context.system_prompt = SystemMessage(
        #     content=f"你是一个有用的助手，根据用户的画像，分析并回答他的问题，"
        #             f"用户的画像是：{settings.default_user.description}。"
        # )
        task.start()

        self.tasks.append(task)
        self.taskCreated.emit(task)

        return task

    def save(self) -> None:
        path = Settings.getSettingsDirectory() / "tasks"
        if not path.exists():
            path.mkdir(parents=True)

        with open(path / 'tasks.json', 'w', encoding='utf-8') as f:
            task_mgr_json = {
                "task_list": [task.task_id for task in self.tasks]
            }
            f.write(json.dumps(task_mgr_json, ensure_ascii=False, indent=4))

        for task in self.tasks:
            if not task.need_save:
                continue

            task_file_path = path / (task.task_id + ".json")
            task.save(task_file_path)

        logger.info(f"tasks saved to {path}")

    @classmethod
    def load(cls) -> 'TaskManagerState':
        path = Settings.getSettingsDirectory() / "tasks"
        if not path.exists():
            return TaskManagerState()

        task_manager_path = path / 'tasks.json'
        if not task_manager_path.exists():
            return TaskManagerState()

        manager = TaskManagerState()
        with open(task_manager_path, 'r', encoding='utf-8') as f:
            task_mgr_json = json.loads(f.read())

            for task_id in task_mgr_json["task_list"]:
                task_file_path = path / (task_id + ".json")
                try:
                    task = TaskState.load(task_file_path, manager)
                    manager.tasks.append(task)
                except Exception as ex:
                    logger.error(f"failed to load task {task_id} from {task_file_path}")

        return manager
