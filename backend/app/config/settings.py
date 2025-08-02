import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./oqtoshsoy_resort.db"
    )

    # Security
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "your-secret-key-here-change-in-production"
    )

    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_WEB_APP_SECRET: str = os.getenv("TELEGRAM_WEB_APP_SECRET", "WebAppData")
    ALLOWED_TELEGRAM_IDS: List[int] = [
        int(id.strip()) for id in os.getenv("ALLOWED_TELEGRAM_IDS", "").split(",")
        if id.strip()
    ]

    # Frontend
    FRONTEND_URL: str = os.getenv(
        "FRONTEND_URL",
        "https://oqtoshsoy-resort-system-production-ef7c.up.railway.app"
    )

    # Redis (optional)
    REDIS_URL: str = os.getenv("REDIS_URL", "")

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")

    class Config:
        case_sensitive = True


settings = Settings()