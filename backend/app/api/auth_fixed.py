from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
import hashlib
import hmac
import json
from urllib.parse import unquote
import os
import logging

from ..database import get_db
from ..models.user import User, UserRole
from ..config.admins import is_allowed_user, get_user_role
from ..utils.dependencies import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from ..schemas.user import TelegramAuthData

router = APIRouter()
logger = logging.getLogger(__name__)

# КРИТИЧЕСКИ ВАЖНО: Получаем токен бота
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")


def verify_telegram_auth(init_data: str) -> dict:
    """Verify Telegram WebApp authentication data"""

    # УБИРАЕМ ЛЮБЫЕ ОБХОДЫ - СТРОГАЯ ПРОВЕРКА
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not configured!")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error: Bot token missing"
        )

    try:
        # Parse init data
        parsed_data = {}
        for part in init_data.split('&'):
            if '=' in part:
                key, value = part.split('=', 1)
                parsed_data[key] = unquote(value)

        # Extract and verify hash
        received_hash = parsed_data.pop('hash', '')
        if not received_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication hash"
            )

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
            logger.warning(f"Invalid hash. Expected: {calculated_hash[:10]}..., Got: {received_hash[:10]}...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication data"
            )

        # Parse user data
        user_data = json.loads(parsed_data.get('user', '{}'))
        if not user_data or not user_data.get('id'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user data"
            )

        return {"user": user_data}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auth verification error: {e}")
        # НЕ ВОЗВРАЩАЕМ ТЕСТОВОГО ПОЛЬЗОВАТЕЛЯ!
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication verification failed"
        )


@router.post("/telegram", response_model=dict)
async def telegram_auth(
        auth_data: TelegramAuthData,
        db: Session = Depends(get_db)
):
    """Authenticate user via Telegram WebApp"""

    # Проверяем environment
    environment = os.getenv("ENVIRONMENT", "production")

    # В PRODUCTION ВСЕГДА СТРОГАЯ ПРОВЕРКА
    if environment == "production":
        strict_mode = True
    else:
        # Даже в development проверяем, если есть токен
        strict_mode = bool(TELEGRAM_BOT_TOKEN)

    try:
        # Verify Telegram auth data
        verified_data = verify_telegram_auth(auth_data.initData)
        user_data = verified_data.get("user", {})

        # Get telegram_id
        telegram_id = user_data.get("id")
        if not telegram_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user data: missing ID"
            )

        # ВСЕГДА ПРОВЕРЯЕМ WHITELIST
        logger.info(f"🔐 Checking access for Telegram ID: {telegram_id}")
        logger.info(f"   User: {user_data.get('first_name')} {user_data.get('last_name')}")
        logger.info(f"   Username: @{user_data.get('username', 'no_username')}")
        logger.info(f"   Environment: {environment}")
        logger.info(f"   Strict mode: {strict_mode}")

        # ПРОВЕРКА ДОСТУПА - БЕЗ ИСКЛЮЧЕНИЙ
        if not is_allowed_user(telegram_id):
            logger.warning(f"⛔ UNAUTHORIZED ACCESS ATTEMPT!")
            logger.warning(f"   Telegram ID: {telegram_id}")
            logger.warning(f"   Name: {user_data.get('first_name')} {user_data.get('last_name')}")
            logger.warning(f"   Username: @{user_data.get('username', 'no_username')}")

            # Возвращаем понятную ошибку на узбекском
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "KIRISH RAD ETILDI",
                    "message": f"Sizning Telegram ID ({telegram_id}) ruxsat berilmagan.",
                    "instruction": "Tizim administratori bilan bog'laning: @Oqtosh_Soy",
                    "telegram_id": telegram_id,
                    "username": user_data.get('username', 'no_username')
                }
            )

        logger.info(f"✅ Access granted for Telegram ID: {telegram_id}")

        # Далее создание/обновление пользователя как обычно...
        user = db.query(User).filter(User.telegram_id == telegram_id).first()

        if not user:
            # Create new user
            user_role_str = get_user_role(telegram_id)
            role_map = {
                "super_admin": UserRole.SUPER_ADMIN,
                "admin": UserRole.ADMIN,
                "manager": UserRole.MANAGER,
                "operator": UserRole.OPERATOR,
                "user": UserRole.USER
            }

            role = role_map.get(user_role_str, UserRole.USER)

            user = User(
                telegram_id=telegram_id,
                first_name=user_data.get("first_name", ""),
                last_name=user_data.get("last_name", ""),
                username=user_data.get("username", ""),
                role=role,
                is_admin=role in [UserRole.SUPER_ADMIN, UserRole.ADMIN],
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)

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
        logger.error(f"❌ Authentication error: {e}")
        # НЕ ДАЕМ ОБХОД!
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )