from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, OrderedDict


class ProviderType(Enum):
    OpenRouter = "OpenRouter"
    SiliconFlow = "SiliconFlow"
    Custom = "Custom"


class ProviderConfig(BaseModel):
    provider_name: str
    type: ProviderType = ProviderType.Custom
    base_url: Optional[str] = None
    api_key: Optional[str] = None


class ModelConfig(BaseModel):
    name: str
    provider_name: str


class UserProfile(BaseModel):
    name: str = "用户"


class Settings(BaseModel):
    provider_configs: OrderedDict[str, ProviderConfig] = Field(default_factory=OrderedDict)
    user_profiles: OrderedDict[str, UserProfile] = Field(default_factory=OrderedDict)
