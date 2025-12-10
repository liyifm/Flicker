from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, QByteArray, QBuffer, QIODevice, QThread, Signal
from PySide6.QtGui import QPixmap, QImage

from flicker.services.proactive.intent_parser.intent import IntentRegistry
from flicker.utils.notification import NotificationManager
from flicker.services.llm.completion import ChatCompletionService
from flicker.services.llm.types import ChatContext, UserMessage, AssistantMessage
from openai import OpenAI
from pydantic import BaseModel, Field
from loguru import logger

from os import environ
from typing import Callable, List
from pprint import pprint

import json
import traceback


INTENT_PARSING_PROMPT = """
你是一个熟悉手机和电脑操作的，善解人意的智能体，总是用中文回答用户的问题。

你需要通过用户给定的设备截图，来猜测用户接下来可能需要你帮忙执行的任务（我们称之为意图）。
当前所有支持的意图在下面列出：

## 当前系统中已经支持的可以执行的意图

{intents}

## 返回格式

你的返回格式应该为JSON格式的数组，表示所有可能的意图。这些意图需要按照可能性由大到小排序，
数组中的每个元素应当符合下面的格式:

    {{
        "name": <意图的名称>,
        "reasoning": <简短描述该意图与当前屏幕内容相关的原因，使用自然轻快的语气>,
        "confidence": <该意图的置信度，也就是可能性评分，范围从0到1>,
        "params": <意图的参数，需要与该意图的输入参数Schema匹配>
    }}

"""


class IntentInstance(BaseModel):
    name: str
    reasoning: str
    confidence: float
    params: dict


class IntentParsingResult(BaseModel):
    ok: bool
    message: str = Field(default="")
    intents: List[IntentInstance] = Field(default_factory=list)


class IntentParserInstance(QObject):

    finished = Signal(IntentParsingResult)

    def __init__(self, screenshot: QPixmap) -> None:
        super().__init__()
        self.screenshot = screenshot

    def parse(self) -> IntentParsingResult:
        from flicker.utils.settings import Settings

        setting = Settings.loadDefault()
        model = setting.getModelInstance(setting.default_multimodal_model_alias)

        intents = ""
        for intent in IntentRegistry.getInstance().getIntents():
            intents += f"- 意图名称 {intent.name}\n"
            intents += f"  * 意图描述: {intent.description}\n"
            intents += f"  * 意图的输入参数Schema: " + json.dumps(intent.parameterSchema.model_json_schema(), ensure_ascii=False) + "\n"

        ctx = ChatContext()
        ctx.appendMessage(UserMessage().appendItem(
            INTENT_PARSING_PROMPT.format(intents=intents),
            self.screenshot,
        ))

        content = ChatCompletionService.syncComplete(model, ctx).getPlainText()
        print(content)
        startPos = content.find('```json')
        if startPos == -1:
            raise ValueError("Failed to find JSON code block in the response")

        endPos = content.find('```', startPos + 7)
        if endPos == -1:
            raise ValueError("Failed to find the end of JSON code block in the response")

        jsonStr = content[startPos + 7:endPos].strip()
        try:
            jsonObj = json.loads(jsonStr)
        except json.JSONDecodeError as ex:
            logger.error(f'Failed to parse JSON: {ex}')
            logger.info(f'JSON string: {jsonStr}')
            raise ValueError(f"Failed to parse JSON: {ex}")

        if not isinstance(jsonObj, list):
            raise ValueError("Parsed intents is not a list")

        parsedIntents = []
        for item in jsonObj:
            parsedIntent = IntentInstance.model_validate(item)
            parsedIntents.append(parsedIntent)

        return IntentParsingResult(ok=True, intents=parsedIntents)

    def start(self) -> None:
        try:
            result = self.parse()
            self.finished.emit(result)
        except Exception as ex:
            logger.error(f'Intent parsing failed: {ex}')
            logger.info(traceback.format_exc())
            result = IntentParsingResult(ok=False, message=str(ex))
            self.finished.emit(result)


class IntentParser:

    current_thread: QThread | None = None
    current_instance: IntentParserInstance | None = None
    current_result: IntentParsingResult | None = None

    current_callback: Callable[[IntentParsingResult], None] | None = None

    @classmethod
    def isParsing(cls) -> bool:
        return cls.current_thread is not None

    @classmethod
    def startParseScreen(cls, screenshot: QPixmap, callback: Callable[[IntentParsingResult], None] | None = None) -> None:
        if cls.current_thread is not None:
            raise RuntimeError("Another intent parsing task is still running")

        thread = QThread()
        instance = IntentParserInstance(screenshot)

        cls.current_thread = thread
        cls.current_instance = instance
        cls.current_result = None
        cls.current_callback = callback

        instance.finished.connect(cls.parsingFinished)
        instance.finished.connect(thread.quit)
        instance.moveToThread(thread)
        thread.started.connect(instance.start)
        thread.finished.connect(cls.cleanParsingTask)
        thread.start()

    @classmethod
    def parsingFinished(cls, result: IntentParsingResult) -> None:
        cls.current_result = result

    @classmethod
    def cleanParsingTask(cls) -> None:
        logger.info("intent parsing task finished")
        cls.current_thread = None
        cls.current_instance = None
        if cls.current_result is not None and cls.current_callback is not None:
            cls.current_callback(cls.current_result)
