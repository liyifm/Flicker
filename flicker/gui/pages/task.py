from PySide6.QtWidgets import QTextBrowser, QVBoxLayout, QFrame, QScrollArea, QWidget, QSizePolicy, QGraphicsDropShadowEffect, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QResizeEvent, QColor

from flicker.utils.image import ImageUtils
from flicker.gui.pages.base import FlickerPage
from flicker.gui.states.task import TaskState
from flicker.gui.widgets.input import AIChatInput
from flicker.services.llm.types import ChatContext, UserMessage, AssistantMessage, ChatMessageUnion, TextPart, ImagePart

from loguru import logger


USER_MESSAGE_STYLE = """
QFrame {
    background-color: #2BA245;
    border-radius: 15px;
    color: white;
}
"""

ASSISTANT_MESSAGE_STYLE = """
QFrame {
    background-color: #FEFEFE;
    border-radius: 15px;
    color: black;
}
"""


class TextPartView(QTextBrowser):

    def __init__(self, text_part: TextPart) -> None:
        super().__init__()
        self.text_part = text_part
        self.setLineWrapMode(QTextBrowser.LineWrapMode.WidgetWidth)

    def reload(self) -> None:
        self.setMarkdown(self.text_part.text)
        self.adjustHeight()

    def adjustHeight(self) -> None:
        document_height = self.document().size().height()
        margins = self.contentsMargins()
        self.setFixedHeight(int(document_height) + margins.top() + margins.bottom() + 2)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self.adjustHeight()

    def wheelEvent(self, event):
        super().wheelEvent(event)
        self.adjustHeight()


class ImagePartView(QLabel):
    def __init__(self, image_part: ImagePart) -> None:
        super().__init__()
        self.image_part = image_part
        self.setPixmap(ImageUtils.base64ToPixmap(self.image_part.image_url.url))


class ChatMessageView(QFrame):

    def __init__(self, message: ChatMessageUnion, parent=None):
        super().__init__(parent)
        self.message = message
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.widget_parts: list[TextPartView | ImagePartView] = []

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        if isinstance(message, UserMessage):
            self.setStyleSheet(USER_MESSAGE_STYLE)
        elif isinstance(message, AssistantMessage):
            self.setStyleSheet(ASSISTANT_MESSAGE_STYLE)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(5)  # 模糊半径
        shadow.setXOffset(0)  # X 偏移
        shadow.setYOffset(0)  # Y 偏移
        shadow.setColor(QColor("#AAAAAA"))  # 阴影颜色和透明度
        self.setGraphicsEffect(shadow)

        self.reload()

    def reload(self) -> None:
        for i, part in enumerate(self.message.content):
            if len(self.widget_parts) <= i:
                if isinstance(part, TextPart):
                    widget_text = TextPartView(part)
                    self.widget_parts.append(widget_text)
                    self.main_layout.addWidget(widget_text)
                elif isinstance(part, ImagePart):
                    widget_image = ImagePartView(part)
                    self.widget_parts.append(widget_image)
                    self.main_layout.addWidget(widget_image)
                else:
                    raise NotImplementedError

        if len(self.widget_parts) > 0 and \
                isinstance(self.widget_parts[-1], TextPartView):
            self.widget_parts[-1].reload()

        self.adjustHeight()

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.adjustHeight()

    def adjustHeight(self) -> None:
        self.setFixedHeight(self.main_layout.sizeHint().height() + 20)


class ChatContextView(QScrollArea):

    def __init__(self, chat_context: ChatContext) -> None:
        super().__init__()
        self.chat_context = chat_context
        self.widget_messages: list[ChatMessageView] = []
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.content_layout)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.content_layout.setSpacing(10)

        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet("QScrollArea { border: none; background-color: #00000000; }")

        content_widget = QWidget(self)
        content_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        content_widget.setLayout(self.content_layout)

        self.setWidget(content_widget)

    def reload(self) -> None:
        for i, message in enumerate(self.chat_context.messages):
            if len(self.widget_messages) <= i:
                widget_message = ChatMessageView(message)
                self.widget_messages.append(widget_message)
                self.content_layout.addWidget(widget_message)

        if len(self.chat_context.messages) > 0:
            self.widget_messages[-1].reload()

        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())


class TaskPage(FlickerPage):

    def __init__(self, task_state: TaskState) -> None:
        super().__init__()
        self.task_state = task_state
        self.widget_context: ChatContextView = ChatContextView(self.task_state.task_context)
        self.widget_input: AIChatInput = AIChatInput()
        self.widget_input.messageSubmitted.connect(self.submitUserMessage)
        self.__setUpLayout()
        self.__setUpSignals()

        # update task content for initialization
        self.updateTaskContent()
        self.setStyleSheet("QWidget { background-color: #FFFFFF; }")

    def __setUpLayout(self) -> None:
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.widget_context, 1)
        main_layout.addWidget(self.widget_input)
        self.setLayout(main_layout)

    def __setUpSignals(self) -> None:
        self.task_state.taskStatusUpdated.connect(self.updateTaskContent)

    def getPageId(self) -> str:
        return f"#task-{self.task_state.task_id}"

    def getPageName(self) -> str:
        return self.task_state.task_name

    def updateTaskContent(self) -> None:
        self.widget_context.reload()

    def submitUserMessage(self, message: str) -> None:
        self.task_state.appendUserMessage(UserMessage.create(message))
        self.task_state.start()
