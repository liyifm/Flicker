from PySide6.QtCore import QObject, Signal
from uuid import uuid4
from enum import Enum

from flicker.services.llm.completion import ChatCompletionService, StreamCompletionChunk
from flicker.services.llm.types import ChatContext, UserMessage, AssistantMessage, SystemMessage
from flicker.utils.settings import Settings, ModelInstance


class TaskStatus(Enum):
    PENDING = 0
    RUNNING = 1


class TaskState(QObject):
    taskNameUpdated = Signal()
    taskStatusUpdated = Signal()

    def __init__(self, task_name: str, task_model: ModelInstance) -> None:
        super().__init__()
        self.task_id: str = str(uuid4())
        self.task_name: str = task_name
        self.task_status: TaskStatus = TaskStatus.PENDING
        self.task_context: ChatContext = ChatContext()
        self.task_model: ModelInstance = task_model

    def appendUserMessage(self, message: UserMessage) -> None:
        self.task_context.appendMessage(message)
        self.taskStatusUpdated.emit()

    def onChunkReceived(self, chunk: StreamCompletionChunk) -> None:
        # there is at least one message before starting completion
        message: AssistantMessage
        if self.task_context.messages[-1].role == 'user':
            message = AssistantMessage()
            self.task_context.messages.append(message)
        else:
            message = self.task_context.messages[-1]

        message.appendChunk(chunk.delta)
        self.taskStatusUpdated.emit()

    def start(self):
        ChatCompletionService.streamComplete(self.task_model, self.task_context, self.onChunkReceived)


class TaskManagerState(QObject):
    taskCreated = Signal(TaskState)

    def __init__(self) -> None:
        super().__init__()
        self.tasks: list[TaskState] = []

    def submitUserMessage(self, message: str) -> TaskState:
        settings = Settings.loadDefault()
        task = TaskState(task_name=message, task_model=settings.getModelInstance(settings.default_model_alias))
        task.appendUserMessage(UserMessage.create(message))
        # task.task_context.system_prompt = SystemMessage(
        #     content=f"你是一个有用的助手，根据用户的画像，分析并回答他的问题，"
        #             f"用户的画像是：{settings.default_user.description}。"
        # )
        task.start()

        self.tasks.append(task)
        self.taskCreated.emit(task)

        return task
