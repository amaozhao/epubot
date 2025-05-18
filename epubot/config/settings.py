import os
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings managed by pydantic-settings.
    Settings can be loaded from environment variables or a .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore"
    )  # Load from .env, ignore unknown fields

    PROJECT_NAME: str = "Epubot"

    # 日志设置
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "ERROR"
    LOG_FORMAT: Literal["json", "console"] = "json"
    LOG_FILE: str = "logs/epubot.log"
    LOG_RENDER_JSON_LOGS: bool = True

    # LLM API Keys
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "YOUR_DEEPSEEK_API_KEY")
    mistral_api_key: str = os.getenv("MISTRAL_API_KEY", "YOUR_MISTRAL_API_KEY")

    OUTPUT_DIR: str = "output"


settings = Settings()
