from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import hashlib
import hmac
import json
from urllib.parse import unquote
import os

from ..models.user import User
from ..database import get_db

# Настройки для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Настройки JWT берем из dependencies
from ..utils.dependencies import SECRET_KEY, ALGORITHM, create_access_token


def verify_password(plain_password, hashed_password):
    """Проверка пароля"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Хеширование пароля"""
    return pwd_context.hash(password)


def verify_telegram_auth(bot_token: str, auth_data: dict) -> bool:
    """Проверка данных авторизации от Telegram"""
    check_hash = auth_data.get('hash')
    if not check_hash:
        return False

    # Создаем строку для проверки
    auth_data_copy = auth_data.copy()
    del auth_data_copy['hash']

    data_check_arr = []
    for key in sorted(auth_data_copy.keys()):
        data_check_arr.append(f"{key}={auth_data_copy[key]}")

    data_check_string = '\n'.join(data_check_arr)

    # Вычисляем хеш
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    hash_check = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    return hash_check == check_hash


def get_or_create_user(db: Session, telegram_data: dict) -> User:
    """Получить или создать пользователя по данным Telegram"""
    telegram_id = telegram_data.get('id')

    # Ищем существующего пользователя
    user = db.query(User).filter(User.telegram_id == telegram_id).first()

    if not user:
        # Создаем нового пользователя
        user = User(
            telegram_id=telegram_id,
            username=telegram_data.get('username'),
            first_name=telegram_data.get('first_name', 'User'),
            last_name=telegram_data.get('last_name'),
            is_admin=False  # По умолчанию не админ
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user