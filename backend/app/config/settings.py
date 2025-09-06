# file: backend/app/config/settings.py
from pydantic_settings import BaseSettings
from functools import lru_cache


# Этот класс автоматически найдёт ваш .env файл и загрузит из него переменные
class Settings(BaseSettings):
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


# Эта функция создаёт и возвращает объект с вашими настройками.
# Именно её ищут другие файлы при импорте.
@lru_cache
def get_settings() -> Settings:
    return Settings()