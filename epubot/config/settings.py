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
    deepseek_model: str = os.getenv("DEEPSEEK_MODEL", "deepseek-reasoner")
    mistral_api_key: str = os.getenv("MISTRAL_API_KEY", "YOUR_MISTRAL_API_KEY")
    mistral_model: str = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
    kimi_api_key: str = os.getenv("KIMI_API_KEY", "YOUR_KIMI_API_KEY")
    kimi_base_url: str = os.getenv("KIMI_BASE_URL", "https://api.moonshot.cn/v1")
    kimi_model: str = os.getenv("KIMI_MODEL", "moonshot-v1-auto")

    OUTPUT_DIR: str = "output"


settings = Settings()
