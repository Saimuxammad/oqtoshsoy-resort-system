# file: backend/app/api/auth.py
import hmac
import hashlib
import json
from urllib.parse import unquote
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from ..database import get_db
from ..models.user import User
# ✅ ИСПРАВЛЕННЫЙ ИМПОРТ
from ..config.settings import get_settings
from ..utils.dependencies import create_access_token
from ..schemas.user import TelegramAuthData

router = APIRouter()
settings = get_settings()


def verify_telegram_auth(init_data: str) -> dict:
    """Проверяет данные аутентификации от Telegram WebApp."""
    if not settings.telegram_bot_token:
        raise HTTPException(status_code=500, detail="Bot token not configured")

    try:
        unquoted_data = unquote(init_data)
        data_to_check = []
        hash_from_telegram = ''

        for pair in sorted(unquoted_data.split('&')):
            key, value = pair.split('=', 1)
            if key == 'hash':
                hash_from_telegram = value
            else:
                data_to_check.append(f"{key}={value}")

        data_check_string = "\n".join(data_to_check)

        secret_key = hmac.new("WebAppData".encode(), settings.telegram_bot_token.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        if calculated_hash != hash_from_telegram:
            raise ValueError("Invalid hash")

        user_data_str = dict(pair.split('=', 1) for pair in unquoted_data.split('&')).get('user', '{}')
        return json.loads(unquote(user_data_str))

    except Exception:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authentication data")


@router.post("/telegram", response_model=dict)
async def telegram_auth(auth_data: TelegramAuthData, db: Session = Depends(get_db)):
    """Аутентификация пользователя через Telegram WebApp."""

    user_data = verify_telegram_auth(auth_data.initData)
    telegram_id = user_data.get("id")

    if not telegram_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user data from Telegram")

    user = db.query(User).filter(User.telegram_id == telegram_id).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Доступ запрещен. Ваш Telegram ID ({telegram_id}) не зарегистрирован или заблокирован."
        )

    user.username = user_data.get("username", user.username)
    user.first_name = user_data.get("first_name", user.first_name)
    user.last_name = user_data.get("last_name", user.last_name)
    db.commit()

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"user_id": user.id},
        expires_delta=access_token_expires
    )

    return {
        "token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "first_name": user.first_name,
            "role": user.role.value
        }
    }