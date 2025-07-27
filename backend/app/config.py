from pydantic_settings import BaseSettings
from typing import List, Union
from functools import cached_property


class Settings(BaseSettings):
    database_url: str
    telegram_bot_token: str
    telegram_web_app_secret: str
    secret_key: str
    redis_url: str = "redis://default:AbPQAAIjcDEzMTRiYzM1NDZhZjQ0MGM4YmQ5NDFlYWRjYTliZjE3OHAxMA@desired-sheepdog-46032.upstash.io:6379"
    environment: str = "development"
    allowed_telegram_ids: str = "5488749868"  # Изменено на str
    web_app_url: str = "http://localhost:5173"  # Добавлено

    class Config:
        env_file = ".env"
        extra = "allow"  # Разрешаем дополнительные поля

    @cached_property
    def parse_allowed_ids(self) -> List[int]:
        """Parse allowed Telegram IDs from string"""
        if not self.allowed_telegram_ids:
            return []
        try:
            return [int(id.strip()) for id in self.allowed_telegram_ids.split(",") if id.strip()]
        except ValueError:
            return []


settings = Settings()