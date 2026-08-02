from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env."""

    app_name: str = Field(default="LMKT Landing Page Backend")
    environment: str = Field(default="development")
    debug: bool = Field(default=False)
    cors_origins: str = Field(default="http://localhost:3000")
    mongodb_uri: str = Field(default="mongodb://localhost:27017")
    mongodb_db_name: str = Field(default="lmkt_db")
    gemini_api_key: str = Field(default="")
    gemini_model: str = Field(default="")
    log_level: str = Field(default="INFO")
    max_message_length: int = Field(default=500)
    vercel: bool = Field(default=False)

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings instance for dependency injection."""
    return Settings()
