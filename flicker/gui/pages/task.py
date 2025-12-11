from PySide6.QtWidgets import QTextBrowser, QVBoxLayout, QFrame, QScrollArea, QWidget, QSizePolicy, QGraphicsDropShadowEffect, QLabel
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QResizeEvent, QColor
from PySide6.QtWebEngineWidgets import QWebEngineView

from flicker.utils.image import ImageUtils
from flicker.gui.pages.base import FlickerPage
from flicker.gui.states.task import TaskState
from flicker.gui.widgets.input import AIChatInput
from flicker.services.llm.types import ChatContext, UserMessage, AssistantMessage, ChatMessageUnion, TextPart, ImagePart

from loguru import logger

import mistune


USER_MESSAGE_STYLE = """
QFrame {
    background-color: #F46537;
    border-radius: 18px;
    color: white;
}
"""

ASSISTANT_MESSAGE_STYLE = """
QFrame {
    background-color: #FEFEFE;
    border-radius: 18px;
    color: black;
}
"""

HTML_TEMPLATE = """
<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
  </head>
  <style>
    body {{
      background-color: transparent;
      height: fit-content;
    }}
  </style>
  <body>{body}</body>
</html>
"""


class TextPartView(QWebEngineView):

    def __init__(self, text_part: TextPart) -> None:
        super().__init__()
        self.text_part = text_part
        self.page().loadFinished.connect(self.updateHeight)
        self.setFixedHeight(0)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)

    def reload(self) -> None:
        html = HTML_TEMPLATE.format(body=mistune.html(self.text_part.text))
        page = self.page()
        page.setBackgroundColor(Qt.GlobalColor.transparent)
        page.setHtml(html)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(50, self.updateHeight)

    def updateHeight(self) -> None:
        js_code = """
        (function() {
            // 移除滚动条
            document.body.style.overflow = 'hidden';
            document.documentElement.style.overflow = 'hidden';

            // 获取内容的实际大小
            var content = document.body;
            var rect = content.getBoundingClientRect();

            var height = Math.max(
                content.scrollHeight,
                content.offsetHeight
            );

            return Math.ceil(height);
        })();
        """

        self.page().runJavaScript(js_code, self.setHeight)

    def setHeight(self, height: int) -> None:
        current_height = self.height()
        if current_height - 5 <= height <= current_height + 5:  # 5px tolerance
            return

        self.setFixedHeight(height + 5)

        parent = self.parentWidget()
        if parent:
            QTimer.singleShot(0, parent.adjustSize)

    def sizeHint(self):
        return QSize(self.width(), self.height())


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
        self.main_layout.setContentsMargins(8, 3, 8, 3)
        self.setLayout(self.main_layout)
        self.widget_parts: list[TextPartView | ImagePartView] = []

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)

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

        if len(self.widget_parts) > 0 and isinstance(self.widget_parts[-1], TextPartView):
            # only reload the last part if it is a text part
            # other parts do not involve streaming hence has no need to reload
            self.widget_parts[-1].reload()

    def adjustSize(self):
        super().adjustSize()
        self.setFixedHeight(self.main_layout.sizeHint().height() + 5)
        parent = self.parentWidget()
        if parent is not None:
            QTimer.singleShot(0, parent.adjustSize)

    def sizeHint(self):
        return self.main_layout.sizeHint()


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
        main_layout.setContentsMargins(20, 20, 20, 20)
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
