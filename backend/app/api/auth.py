from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
import hashlib
import hmac
import json
from urllib.parse import unquote
import os

from ..database import get_db
from ..models.user import User, UserRole
from ..config.admins import is_super_admin, is_admin, is_allowed_user, get_user_role
from ..utils.dependencies import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from ..schemas.user import UserResponse, TelegramAuthData

router = APIRouter()

# Telegram bot token from environment
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")


def verify_telegram_auth(init_data: str) -> dict:
    """Verify Telegram WebApp authentication data"""
    if not TELEGRAM_BOT_TOKEN:
        # В dev режиме пропускаем проверку
        return {"user": {"id": 123456789, "first_name": "Dev", "last_name": "User"}}

    try:
        # Parse init data
        parsed_data = {}
        for part in init_data.split('&'):
            key, value = part.split('=')
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
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication data"
            )

        # Parse user data
        user_data = json.loads(parsed_data.get('user', '{}'))
        return {"user": user_data}

    except Exception as e:
        # В случае ошибки в dev режиме возвращаем тестового пользователя
        if os.getenv("ENVIRONMENT", "development") == "development":
            return {"user": {"id": 123456789, "first_name": "Dev", "last_name": "User"}}
        raise


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

        # Get or create user
        telegram_id = user_data.get("id")
        if not telegram_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user data"
            )

        # ВКЛЮЧАЕМ проверку доступа для продакшена
        if os.getenv("ENVIRONMENT", "development") == "production":
            if not is_allowed_user(telegram_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied. You are not authorized to use this system. Please contact administrator."
                )

        user = db.query(User).filter(User.telegram_id == telegram_id).first()

        if not user:
            # Create new user
            # Определяем роль на основе конфигурации
            user_role_str = get_user_role(telegram_id)

            # Преобразуем строковую роль в enum
            role_map = {
                "super_admin": UserRole.SUPER_ADMIN,
                "admin": UserRole.ADMIN,
                "manager": UserRole.MANAGER,
                "operator": UserRole.OPERATOR,
                "user": UserRole.USER
            }

            role = role_map.get(user_role_str, UserRole.USER)
            is_admin_flag = role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]

            user = User(
                telegram_id=telegram_id,
                first_name=user_data.get("first_name", ""),
                last_name=user_data.get("last_name", ""),
                username=user_data.get("username", ""),
                is_admin=is_admin_flag,
                role=role,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # Update existing user info
            user.first_name = user_data.get("first_name", user.first_name)
            user.last_name = user_data.get("last_name", user.last_name)
            user.username = user_data.get("username", user.username)

            # Обновляем роль, если пользователь добавлен в админы
            user_role_str = get_user_role(telegram_id)
            role_map = {
                "super_admin": UserRole.SUPER_ADMIN,
                "admin": UserRole.ADMIN,
                "manager": UserRole.MANAGER,
                "operator": UserRole.OPERATOR,
                "user": UserRole.USER
            }

            new_role = role_map.get(user_role_str, UserRole.USER)
            if new_role != user.role:
                user.role = new_role
                user.is_admin = new_role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]

            db.commit()

        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
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
                "last_name": user.last_name,
                "username": user.username,
                "is_admin": user.is_admin,
                "role": user.role.value
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        # В dev режиме возвращаем тестовый токен
        if os.getenv("ENVIRONMENT", "development") == "development":
            return {
                "token": "dev_token_123456",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "telegram_id": 123456789,
                    "first_name": "Dev",
                    "last_name": "User",
                    "username": "dev_user",
                    "is_admin": True,
                    "role": "admin"
                }
            }
        raise


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
        current_user: User = Depends(get_current_user)
):
    """Get current user info"""
    return current_user