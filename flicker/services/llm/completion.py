from PySide6.QtCore import QObject, QThread, Signal
from openai import OpenAI
from openai.types.completion_usage import CompletionUsage
from openai.types.chat import ChatCompletionMessage, ChatCompletionChunk
from openai.types.chat.chat_completion_chunk import ChoiceDelta
from pydantic import BaseModel

from flicker.utils.settings import ModelInstance
from flicker.services.llm.types import ChatContext, AssistantMessage, TextPart, ImagePart, Usage

from loguru import logger
from typing import Optional, Callable, Literal, Iterable, cast
from uuid import UUID, uuid4

import os
import traceback


ChatFinishReason = Literal['stop', 'content_filter']


class StreamCompletionChunk(BaseModel):
    delta: AssistantMessage
    finish_reason: Optional[ChatFinishReason] = None

    @classmethod
    def parseAssistantMessage(cls, message: ChoiceDelta | ChatCompletionMessage) -> AssistantMessage:
        parsed_message = AssistantMessage()
        if message.content is not None:
            parsed_message.appendText(message.content)
        if hasattr(message, 'images'):
            for img in message.images:
                image_part = ImagePart.model_validate(img)
                parsed_message.appendImagePart(image_part)

        return parsed_message

    @classmethod
    def fromOpenAIChunk(cls, openai_chunk: ChatCompletionChunk) -> "StreamCompletionChunk":
        choice = openai_chunk.choices[0]
        delta = cls.parseAssistantMessage(choice.delta)
        chunk = StreamCompletionChunk(delta=delta)
        if choice.finish_reason == 'stop':
            chunk.finish_reason = 'stop'
        elif choice.finish_reason == 'content_filter':
            chunk.finish_reason = 'content_filter'
            chunk.delta.appendText("\n**🚫生成内容因为内容审查被拒绝**")
        elif choice.finish_reason is not None:
            raise ValueError(f"unsupported finish reason {choice.finish_reason}")

        return chunk


StreamCompletionCallback = Callable[[StreamCompletionChunk], None]


class ChatCompletionInstance(QObject):
    chunkReceived = Signal(StreamCompletionChunk)
    completionStopped = Signal()

    def __init__(self, model: ModelInstance, ctx: ChatContext, streaming: bool = True) -> None:
        super().__init__()
        self.instance_id = uuid4()
        self.model = model
        self.ctx = ctx
        self.worker_thread = QThread()
        self.streaming = streaming
        self.final_result: Optional[AssistantMessage] = None
        self.callback: Optional[StreamCompletionCallback] = None

    @staticmethod
    def parseUsage(usage: CompletionUsage) -> Usage:
        return Usage(
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
            cost=getattr(usage, 'cost', 0.0)  # not all apis return cost information
        )

    def start(self) -> None:
        logger.info(f"completion instance {self.instance_id} started")
        client = OpenAI(api_key=self.model.api_key, base_url=self.model.base_url)
        messages = [msg.model_dump() for msg in self.ctx.messages]
        if self.ctx.system_prompt is not None:
            messages.insert(0, self.ctx.system_prompt.model_dump())

        try:
            if self.streaming:
                stream_response: Iterable[ChatCompletionChunk] = client.chat.completions.create(
                    model=self.model.model_name,
                    messages=messages,  # type: ignore
                    stream=True
                )
                for chunk in stream_response:
                    chunk = cast(ChatCompletionChunk, chunk)
                    self.chunkReceived.emit(StreamCompletionChunk.fromOpenAIChunk(chunk))
                    if chunk.usage is not None:
                        self.ctx.usage += ChatCompletionInstance.parseUsage(chunk.usage)
            else:
                response = client.chat.completions.create(
                    model=self.model.model_name,
                    messages=messages,  # type: ignore
                )
                self.final_result = StreamCompletionChunk.parseAssistantMessage(response.choices[0].message)
        except Exception as e:
            logger.error(f'chat completion failed: {e}')
            logger.info(traceback.format_exc())

        logger.info(f"completion cost: {self.ctx.usage}")
        self.completionStopped.emit()


class ChatCompletionService:
    instances: dict[UUID, ChatCompletionInstance] = dict()

    @classmethod
    def syncComplete(cls, model: ModelInstance, ctx: ChatContext) -> AssistantMessage:
        instance = ChatCompletionInstance(model, ctx, streaming=False)
        instance.start()
        if instance.final_result is not None:
            return instance.final_result
        else:
            raise RuntimeError("Failed to get completion result")

    @classmethod
    def streamComplete(cls, model: ModelInstance, ctx: ChatContext, callback: StreamCompletionCallback) -> None:
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
