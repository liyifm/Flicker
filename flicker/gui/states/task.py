from PySide6.QtCore import QObject, Signal
from uuid import uuid4
from enum import Enum

from flicker.services.llm.completion import ModelRef, ChatCompletionService, StreamCompletionChunk
from flicker.services.llm.types import ChatContext, UserMessage, AssistantMessage


class TaskStatus(Enum):
    PENDING = 0
    RUNNING = 1


class TaskState(QObject):
    taskNameUpdated = Signal()
    taskStatusUpdated = Signal()

    def __init__(self, task_name: str) -> None:
        super().__init__()
        self.task_id: str = str(uuid4())
        self.task_name: str = task_name
        self.task_status: TaskStatus = TaskStatus.PENDING
        self.task_context: ChatContext = ChatContext()

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
        # if self.task_status is not TaskStatus.PENDING:
        #     raise RuntimeError("Task already started")
        #
        # self.task_status = TaskStatus.RUNNING
        model = ModelRef.fromOpenRouter("qwen/qwen3-30b-a3b-instruct-2507")
        ChatCompletionService.streamComplete(model, self.task_context, self.onChunkReceived)


class TaskManagerState(QObject):
    taskCreated = Signal(TaskState)

    def __init__(self) -> None:
        super().__init__()
        self.tasks: list[TaskState] = []

    def submitUserMessage(self, message: str) -> TaskState:
        task = TaskState(task_name=message)
        task.appendUserMessage(UserMessage.create(message))
        task.start()

        self.tasks.append(task)
        self.taskCreated.emit(task)

        return task
