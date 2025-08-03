import os
from typing import Optional

# Database
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "sqlite:///./oqtoshsoy_resort.db"  # По умолчанию SQLite для разработки
)

# Если используется PostgreSQL от Railway, нужно заменить postgres:// на postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Telegram Bot
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_WEB_APP_SECRET: str = os.getenv("TELEGRAM_WEB_APP_SECRET", "WebAppData")

# Security
SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

# Redis (optional)
REDIS_URL: Optional[str] = os.getenv("REDIS_URL", None)

# Environment
ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
DEBUG: bool = ENVIRONMENT == "development"

# CORS
FRONTEND_URL: str = os.getenv(
    "FRONTEND_URL",
    "https://oqtoshsoy-resort-system-production-ef7c.up.railway.app"
)

# Application
APP_NAME: str = "Oqtoshsoy Resort Management System"
APP_VERSION: str = "2.0.0"

# Telegram IDs списки
ALLOWED_TELEGRAM_IDS: list = os.getenv("ALLOWED_TELEGRAM_IDS", "").split(",") if os.getenv("ALLOWED_TELEGRAM_IDS") else []

# WebSocket
WEB_APP_URL: str = os.getenv("WEB_APP_URL", FRONTEND_URL)