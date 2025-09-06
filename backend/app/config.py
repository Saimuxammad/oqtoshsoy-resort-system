# file: backend/app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Загружаем переменные из .env файла
    database_url: str
    telegram_bot_token: str
    secret_key: str
    environment: str = "development"

    # Настройки для JWT токенов
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 дней

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


# Используем lru_cache для создания синглтона настроек,
# чтобы файл .env читался только один раз.
@lru_cache
def get_settings() -> Settings:
    return Settings()