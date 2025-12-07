from PySide6.QtGui import QPixmap
from pydantic import BaseModel, Field
from typing import Literal, Union, Annotated, List, Optional

from flicker.utils.image import ImageUtils


class TextPart(BaseModel):
    type: Literal["text"] = Field(default="text", frozen=True)
    text: str


class ImageUrl(BaseModel):
    url: str


class ImagePart(BaseModel):
    type: Literal["image_url"] = Field(default="image_url", frozen=True)
    image_url: ImageUrl

    @classmethod
    def create(cls, image: QPixmap) -> "ImagePart":
        url = ImageUtils.pixmapToBase64(image, 'png', 80)
        return ImagePart(image_url=ImageUrl(url=url))


MessagePartUnion = Annotated[
    Union[TextPart, ImagePart],
    Field(discriminator='type')
]


class SystemMessage(BaseModel):
    role: Literal['system'] = 'system'
    content: str


class UserMessage(BaseModel):
    role: Literal['user'] = 'user'
    content: list[MessagePartUnion] = []

    @classmethod
    def create(cls, *items: Union[str, QPixmap]) -> 'UserMessage':
        msg = UserMessage()
        for item in items:
            msg.appendItem(item)

        return msg

    def appendItem(self, item: Union[str, QPixmap]) -> None:
        if isinstance(item, str):
            if len(self.content) > 0 and isinstance(self.content[-1], TextPart):
                self.content[-1].text += item
            else:
                self.content.append(TextPart(text=item))
        elif isinstance(item, QPixmap):
            if isinstance(self.content, str):
                self.content = [TextPart(text=self.content)]

            self.content.append(ImagePart.create(item))


class AssistantMessage(BaseModel):
    role: Literal['assistant'] = 'assistant'
    content: List[MessagePartUnion] = []

    def appendChunk(self, chunk: 'AssistantMessage') -> None:
        for part in chunk.content:
            if isinstance(part, TextPart):
                self.appendTextPart(part)
            elif isinstance(part, ImagePart):
                raise NotImplementedError

    def appendTextPart(self, part: 'TextPart') -> None:
        if len(self.content) > 0 and isinstance(self.content[-1], TextPart):
            self.content[-1].text += part.text
        else:
            self.content.append(part)


ChatMessageUnion = Annotated[
    Union[UserMessage, AssistantMessage],
    Field(discriminator='role')
]


class ChatContext(BaseModel):
    system_prompt: Optional[SystemMessage] = None
    messages: list[ChatMessageUnion] = Field(default_factory=list)

    def appendMessage(self, msg: ChatMessageUnion) -> None:
        self.messages.append(msg)
