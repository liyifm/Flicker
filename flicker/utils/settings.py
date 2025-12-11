from flicker.services.memory import DataSourceUnion

from pydantic import BaseModel, Field
from loguru import logger
from typing import Optional, OrderedDict, Literal
from pathlib import Path

import sys
import os


SupportedProviderType = Literal


class ModelInstance(BaseModel):
    """ Model instance is not a configuration item, but a internal
    item returned when finding models """
    base_url: str
    model_name: str
    api_key: str


class ModelProvider(BaseModel):
    provider_name: str = ""
    base_url: str = ""
    api_key: str = ""


class ModelRef(BaseModel):
    alias: str = ""
    provider_name: str = "openrouter"
    model_name: str = "Pro/deepseek-ai/DeepSeek-V3.2"


class UserProfile(BaseModel):
    name: str = "用户"
    description: str = "一个普通人"


class GUIConfig(BaseModel):
    font_size: int = 12


class Settings(BaseModel):
    default_model_alias: str = ""
    default_multimodal_model_alias: str = ""
    default_embed_model_alias: str = ""
    default_user: UserProfile = Field(default_factory=UserProfile)
    gui_config: GUIConfig = Field(default_factory=GUIConfig)
    memory_data_sources: list[DataSourceUnion] = Field(default_factory=list)
    model_providers: list[ModelProvider] = Field(default_factory=list)
    model_refs: list[ModelRef] = Field(default_factory=list)

    def getProvider(self, provider_name: str) -> ModelProvider:
        for provider in self.model_providers:
            if provider.provider_name == provider_name:
                return provider

        raise KeyError(f'cannot find provider {provider_name}')

    def getModelInstance(self, alias: str) -> ModelInstance:
        for ref in self.model_refs:
            if ref.alias == alias:
                provider = self.getProvider(ref.provider_name)
                return ModelInstance(
                    base_url=provider.base_url,
                    api_key=provider.api_key,
                    model_name=ref.model_name
                )

        raise KeyError(f'cannot find model alias {alias}')

    @staticmethod
    def getSettingsDirectory() -> Path:
        if sys.platform == "win32":
            appdata = os.environ.get("APPDATA", "")
            if appdata == "":
                raise ValueError("%APPDATA% is not set")

            settings_dir = Path(appdata) / "flicker"
            if not settings_dir.exists():
                settings_dir.mkdir()
        else:
            raise NotImplementedError(sys.platform)

        logger.info(f"getSettingsDirectory: {settings_dir}")
        return settings_dir

    def getDefaultEmbeddingModel(self) -> ModelInstance:
        return self.getModelInstance(self.default_embed_model_alias)

    @classmethod
    def loadDefault(cls) -> 'Settings':
        from flicker.gui.application import FlickerApp

        settings_dir = Settings.getSettingsDirectory()
        setting_file = settings_dir / "settings.json"

        setting: Optional[Settings] = None
        if not setting_file.exists():
            FlickerApp.sendErrorMessage("缺少配置", "需要正确设置后才能使用Flicker")
            setting = Settings()
        else:
            try:
                with open(setting_file, 'r') as f:
                    setting = Settings.model_validate_json(f.read())
            except Exception as ex:
                FlickerApp.sendErrorMessage("配置错误", "无法解析默认配置")
                setting = Settings()

        return setting

    def saveAsDefault(self) -> None:
        settings_dir = Settings.getSettingsDirectory()
        setting_file = settings_dir / "settings.json"

        try:
            with open(setting_file, "w+") as f:
                f.write(self.model_dump_json(indent=4, ensure_ascii=False))
        except Exception as ex:
            logger.error(f'failed to save default setting: {ex}')
            raise ex
