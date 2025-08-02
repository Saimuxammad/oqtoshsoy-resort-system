import os
from typing import List, Optional
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

    # Allowed Telegram IDs (comma-separated list in env)
    ALLOWED_TELEGRAM_IDS: Optional[str] = os.getenv("ALLOWED_TELEGRAM_IDS", "")

    # Frontend
    FRONTEND_URL: str = os.getenv(
        "FRONTEND_URL",
        "https://oqtoshsoy-resort-system-production-ef7c.up.railway.app"
    )

    # Redis (optional)
    REDIS_URL: str = os.getenv("REDIS_URL", "")

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")

    @property
    def allowed_telegram_ids_list(self) -> List[int]:
        """Convert comma-separated string to list of integers"""
        if not self.ALLOWED_TELEGRAM_IDS:
            return []
        try:
            return [int(id.strip()) for id in self.ALLOWED_TELEGRAM_IDS.split(",") if id.strip()]
        except ValueError:
            return []

    class Config:
        case_sensitive = True


settings = Settings()