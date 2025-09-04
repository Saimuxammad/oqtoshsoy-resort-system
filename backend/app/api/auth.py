from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
import hashlib
import hmac
import json
from urllib.parse import unquote
import os
import logging

from ..database import get_db
from ..models.user import User, UserRole
from ..utils.dependencies import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from ..schemas.user import UserResponse, TelegramAuthData

router = APIRouter()
logger = logging.getLogger(__name__)

# Telegram bot token from environment
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# СПИСОК РАЗРЕШЕННЫХ ПОЛЬЗОВАТЕЛЕЙ - ТОЛЬКО ЭТИ ID МОГУТ СОЗДАВАТЬ/ИЗМЕНЯТЬ/УДАЛЯТЬ
ADMIN_TELEGRAM_IDS = [
    5488749868,  # Ваш ID (super admin)
    # Добавьте сюда ID доверенных лиц:
    # 123456789,  # Имя пользователя 2
    # 987654321,  # Имя пользователя 3
]


def verify_telegram_auth(init_data: str) -> dict:
    """Verify Telegram WebApp authentication data"""
    if not TELEGRAM_BOT_TOKEN:
        # В dev режиме возвращаем тестового пользователя
        if os.getenv("ENVIRONMENT", "development") == "development":
            return {"user": {"id": 5488749868, "first_name": "Dev", "last_name": "User"}}
        raise HTTPException(status_code=500, detail="Telegram bot token not configured")

    try:
        # Parse init data
        parsed_data = {}
        for part in init_data.split('&'):
            if '=' in part:
                key, value = part.split('=', 1)
                parsed_data[key] = unquote(value)

        # Extract hash
        received_hash = parsed_data.pop('hash', '')

        # Create data check string
        data_check_string = '\n'.join([f"{k}={v}" for k, v in sorted(parsed_data.items())])

        # Create secret key
        secret_key = hmac.new(
            b"WebAppData",
            TELEGRAM_BOT_TOKEN.encode(),
            hashlib.sha256
        ).digest()

        # Calculate hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()

        # Verify hash
        if calculated_hash != received_hash:
            # В dev режиме разрешаем вход
            if os.getenv("ENVIRONMENT", "development") == "development":
                return {"user": {"id": 5488749868, "first_name": "Dev", "last_name": "User"}}
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication data"
            )

        # Parse user data
        user_data = json.loads(parsed_data.get('user', '{}'))
        return {"user": user_data}

    except Exception as e:
        # В dev режиме возвращаем тестового пользователя
        if os.getenv("ENVIRONMENT", "development") == "development":
            return {"user": {"id": 5488749868, "first_name": "Dev", "last_name": "User"}}
        logger.error(f"Auth verification error: {e}")
        raise HTTPException(status_code=500, detail="Authentication failed")


@router.post("/telegram", response_model=dict)
async def telegram_auth(
        auth_data: TelegramAuthData,
        db: Session = Depends(get_db)
):
    """Authenticate user via Telegram WebApp"""
    try:
        # Verify Telegram auth data
        verified_data = verify_telegram_auth(auth_data.initData)
        user_data = verified_data.get("user", {})

        # Get telegram_id
        telegram_id = user_data.get("id")
        if not telegram_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user data"
            )

        # Определяем роль пользователя на основе его ID
        if telegram_id in ADMIN_TELEGRAM_IDS:
            # Админ - полные права
            user_role = UserRole.ADMIN
            is_admin_flag = True
            can_modify = True
            logger.info(f"✅ Admin access granted for Telegram ID: {telegram_id}")
        else:
            # Обычный пользователь - только просмотр
            user_role = UserRole.USER
            is_admin_flag = False
            can_modify = False
            logger.info(f"👁️ View-only access granted for Telegram ID: {telegram_id}")

        # Проверяем существующего пользователя
        user = db.query(User).filter(User.telegram_id == telegram_id).first()

        if not user:
            # Создаем нового пользователя
            user = User(
                telegram_id=telegram_id,
                first_name=user_data.get("first_name", ""),
                last_name=user_data.get("last_name", ""),
                username=user_data.get("username", ""),
                is_admin=is_admin_flag,
                role=user_role,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"New user created: {telegram_id} with role {user_role.value}")
        else:
            # Обновляем существующего пользователя
            user.first_name = user_data.get("first_name", user.first_name)
            user.last_name = user_data.get("last_name", user.last_name)
            user.username = user_data.get("username", user.username)

            # Обновляем роль если пользователь добавлен в админы
            if telegram_id in ADMIN_TELEGRAM_IDS:
                user.role = UserRole.ADMIN
                user.is_admin = True

            db.commit()

        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"user_id": user.id},
            expires_delta=access_token_expires
        )

        logger.info(f"User {telegram_id} successfully logged in with role: {user.role.value}")

        return {
            "token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "is_admin": user.is_admin,
                "role": user.role.value,
                "can_modify": can_modify  # Флаг для фронтенда
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
        current_user: User = Depends(get_current_user)
):
    """Get current user info"""
    return current_user


@router.get("/check-access")
async def check_access(telegram_id: int):
    """Проверка прав доступа для отладки"""
    is_admin = telegram_id in ADMIN_TELEGRAM_IDS
    return {
        "telegram_id": telegram_id,
        "is_admin": is_admin,
        "can_modify": is_admin,
        "role": "admin" if is_admin else "viewer",
        "allowed_admin_ids": ADMIN_TELEGRAM_IDS
    }