from PySide6.QtCore import QObject, QThread, Signal
from openai import OpenAI
from openai.types.chat import ChatCompletionChunk
from openai.types.chat.chat_completion_chunk import ChoiceDelta
from pydantic import BaseModel

from flicker.utils.settings import ModelRef
from flicker.services.llm.types import ChatContext, AssistantMessage, TextPart

from loguru import logger
from typing import Optional, Callable, Literal
from uuid import UUID, uuid4

import os
import traceback


ChatFinishReason = Literal['stop']


class StreamCompletionChunk(BaseModel):
    delta: AssistantMessage
    finish_reason: Optional[ChatFinishReason] = None

    @classmethod
    def parseAssistantMessage(cls, message: ChoiceDelta) -> AssistantMessage:
        return AssistantMessage(content=[TextPart(text=message.content or '')])

    @classmethod
    def fromOpenAIChunk(cls, openai_chunk: ChatCompletionChunk) -> "StreamCompletionChunk":
        choice = openai_chunk.choices[0]
        delta = cls.parseAssistantMessage(choice.delta)
        chunk = StreamCompletionChunk(delta=delta)
        if choice.finish_reason == 'stop':
            chunk.finish_reason = 'stop'
        elif choice.finish_reason is not None:
            raise ValueError(f"unsupported finish reason {choice.finish_reason}")

        return chunk


StreamCompletionCallback = Callable[[StreamCompletionChunk], None]


class ChatCompletionInstance(QObject):
    chunkReceived = Signal(StreamCompletionChunk)
    completionStopped = Signal()

    def __init__(self, model: ModelRef, ctx: ChatContext) -> None:
        super().__init__()
        self.instance_id = uuid4()
        self.model = model
        self.ctx = ctx
        self.worker_thread = QThread()
        self.callback: Optional[StreamCompletionCallback] = None

    def start(self) -> None:
        logger.info(f"completion instance {self.instance_id} started")
        client = OpenAI(api_key=self.model.api_key, base_url=self.model.base_url)
        messages = [msg.model_dump() for msg in self.ctx.messages]
        if self.ctx.system_prompt is not None:
            messages.insert(0, self.ctx.system_prompt.model_dump())

        try:
            stream_response = client.chat.completions.create(
                model=self.model.model_name,
                messages=messages,  # type: ignore
                stream=True
            )
            for chunk in stream_response:
                # logger.info(chunk)
                self.chunkReceived.emit(StreamCompletionChunk.fromOpenAIChunk(chunk))  # type: ignore
        except Exception as e:
            logger.error(f'chat completion failed: {e}')
            logger.info(traceback.format_exc())

        self.completionStopped.emit()


class ChatCompletionService:
    instances: dict[UUID, ChatCompletionInstance] = dict()

    @classmethod
    def streamComplete(cls, model: ModelRef, ctx: ChatContext, callback: StreamCompletionCallback) -> None:
        instance = ChatCompletionInstance(model, ctx)
        cls.instances[instance.instance_id] = instance

        def finalize() -> None:
            logger.info(f'completion instance {instance.instance_id} finished')
            del cls.instances[instance.instance_id]

        instance.chunkReceived.connect(callback)
        instance.completionStopped.connect(instance.worker_thread.quit)
        instance.moveToThread(instance.worker_thread)
        instance.worker_thread.started.connect(instance.start)
        instance.worker_thread.finished.connect(finalize)
        instance.worker_thread.start()
