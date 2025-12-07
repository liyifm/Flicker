from pydantic import BaseModel, Field
from loguru import logger
from typing import Optional, OrderedDict
from pathlib import Path

import sys
import os


class ModelRef(BaseModel):
    model_name: str = "Pro/deepseek-ai/DeepSeek-V3.2"
    base_url: str = "https://api.siliconflow.cn/v1"
    api_key: str = ""


class UserProfile(BaseModel):
    name: str = "用户"
    description: str = "一个普通人"


class Settings(BaseModel):
    default_model: ModelRef = Field(default_factory=ModelRef)
    default_user: UserProfile = Field(default_factory=UserProfile)

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
