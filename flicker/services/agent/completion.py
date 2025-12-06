from PySide6.QtCore import QThread, QObject
from pydantic import BaseModel
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from typing import Any, List


class ChatContext(BaseModel):
    messages: List[Any]


class CompletionInstance(QObject):
    pass


class CompletionService:
    pass
