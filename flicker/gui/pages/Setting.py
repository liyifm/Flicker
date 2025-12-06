from pydantic import BaseModel, Field
from enum import Enum


class ModelProvider(Enum):
    pass


class ModelConfig(BaseModel):
    provider: ModelProvider


class Profile(BaseModel):
    nickname: str = "用户"
