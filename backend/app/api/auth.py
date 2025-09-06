from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import hashlib
import hmac
import json
from urllib.parse import unquote
import os
import logging

from ..database import get_db
from ..models.user import User, UserRole
from ..config.admins import is_allowed_user, get_user_role, ALLOWED_USERS
from ..utils.dependencies import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from ..schemas.user import UserResponse, TelegramAuthData

router = APIRouter()
logger = logging.getLogger(__name__)

# КРИТИЧЕСКИ ВАЖНО: Устанавливаем production по умолчанию
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Логируем настройки при запуске
logger.info(f"🔐 Security Configuration:")
logger.info(f"   Environment: {ENVIRONMENT}")
logger.info(f"   Bot Token: {'SET' if TELEGRAM_BOT_TOKEN else 'NOT SET'}")
logger.info(f"   Allowed Users Count: {len(ALLOWED_USERS)}")
logger.info(f"   Allowed IDs: {ALLOWED_USERS}")


def verify_telegram_auth(init_data: str) -> dict:
    """
    Строгая проверка подписи от Telegram.
    БЕЗ ОБХОДОВ, БЕЗ ИСКЛЮЧЕНИЙ!
    """
    # Шаг 1: Проверяем наличие токена бота
    if not TELEGRAM_BOT_TOKEN:
        logger.error("❌ CRITICAL: TELEGRAM_BOT_TOKEN not configured!")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Server configuration error. Contact administrator."
        )

    # Шаг 2: Проверяем, что init_data не пустая
    if not init_data or init_data == "undefined" or init_data == "null":
        logger.error("❌ Empty or invalid init_data received")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid authentication data"
        )

    try:
        # Шаг 3: Парсим данные
        parsed_data = {}
        for part in init_data.split('&'):
            if '=' not in part:
                continue
            key, value = part.split('=', 1)
            parsed_data[key] = unquote(value)

        # Шаг 4: Извлекаем и проверяем хеш
        received_hash = parsed_data.pop('hash', '')
        if not received_hash:
            logger.error("❌ No hash in init_data")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication hash"
            )

        # Шаг 5: Создаем строку для проверки
        data_check_string = '\n'.join([
            f"{k}={v}" for k, v in sorted(parsed_data.items())
        ])

        # Шаг 6: Вычисляем правильный хеш
        secret_key = hmac.new(
            b"WebAppData",
            TELEGRAM_BOT_TOKEN.encode(),
            hashlib.sha256
        ).digest()

        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()

        # Шаг 7: Сравниваем хеши
        if calculated_hash != received_hash:
            logger.error(f"❌ Hash mismatch!")
            logger.error(f"   Expected: {calculated_hash[:20]}...")
            logger.error(f"   Received: {received_hash[:20]}...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication signature"
            )

        # Шаг 8: Парсим данные пользователя
        user_json = parsed_data.get('user', '{}')
        user_data = json.loads(user_json)

        if not user_data or not user_data.get('id'):
            logger.error("❌ No user data in init_data")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User data not found"
            )

        logger.info(f"✅ Signature verified for user ID: {user_data.get('id')}")
        return {"user": user_data}

    except HTTPException:
        # Пробрасываем HTTP исключения
        raise
    except Exception as e:
        # Любые другие ошибки - это критическая ошибка
        logger.error(f"❌ Critical error in verify_telegram_auth: {e}")
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

    # Добавьте эти логи в начало функции
    print("=" * 60)
    print("[AUTH] New authentication attempt")
    print(f"[AUTH] Received initData length: {len(auth_data.initData) if auth_data.initData else 0}")

    try:
        # Verify Telegram auth data
        verified_data = verify_telegram_auth(auth_data.initData)
        user_data = verified_data.get("user", {})

        telegram_id = user_data.get("id")
        print(f"[AUTH] Extracted Telegram ID: {telegram_id} (type: {type(telegram_id)})")

        # Преобразуем в int если это строка
        if isinstance(telegram_id, str):
            telegram_id = int(telegram_id)
            print(f"[AUTH] Converted to int: {telegram_id}")

        # КРИТИЧЕСКАЯ ПРОВЕРКА
        print(f"[AUTH] Checking access for ID: {telegram_id}")
        print(f"[AUTH] Current ALLOWED_USERS: {ALLOWED_USERS}")

        if not is_allowed_user(telegram_id):
            print(f"[AUTH] ❌ ACCESS DENIED - ID {telegram_id} not in whitelist")
            print("=" * 60)

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied for Telegram ID {telegram_id}"
            )

        print(f"[AUTH] ✅ ACCESS GRANTED for ID {telegram_id}")
        print("=" * 60)

        # ... остальной код
@router.post("/telegram", response_model=dict)
async def telegram_auth(
        auth_data: TelegramAuthData,
        db: Session = Depends(get_db)
):
    """
    Аутентификация через Telegram WebApp.
    СТРОГАЯ ПРОВЕРКА WHITELIST!
    """
    logger.info("=" * 50)
    logger.info("🔐 New authentication attempt")
    logger.info(f"   Environment: {ENVIRONMENT}")
    logger.info(f"   Whitelist size: {len(ALLOWED_USERS)}")

    try:
        # Шаг 1: Проверяем подпись Telegram
        logger.info("Step 1: Verifying Telegram signature...")
        verified_data = verify_telegram_auth(auth_data.initData)
        user_data = verified_data.get("user", {})

        # Шаг 2: Получаем Telegram ID
        telegram_id = user_data.get("id")
        if not telegram_id:
            logger.error("❌ No telegram_id in user data")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user data: missing Telegram ID"
            )

        # Преобразуем в int если это строка
        try:
            telegram_id = int(telegram_id)
        except (ValueError, TypeError):
            logger.error(f"❌ Invalid telegram_id format: {telegram_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Telegram ID format"
            )

        # Шаг 3: КРИТИЧЕСКАЯ ПРОВЕРКА - WHITELIST
        logger.info(f"Step 2: Checking whitelist for ID: {telegram_id}")
        logger.info(f"   User: {user_data.get('first_name')} {user_data.get('last_name')}")
        logger.info(f"   Username: @{user_data.get('username', 'no_username')}")
        logger.info(f"   Allowed IDs: {ALLOWED_USERS}")

        # ЖЕСТКАЯ ПРОВЕРКА БЕЗ ОБХОДОВ
        is_allowed = telegram_id in ALLOWED_USERS

        if not is_allowed:
            # Записываем попытку несанкционированного доступа
            logger.warning("=" * 50)
            logger.warning("⛔ UNAUTHORIZED ACCESS ATTEMPT!")
            logger.warning(f"   Telegram ID: {telegram_id}")
            logger.warning(f"   Name: {user_data.get('first_name')} {user_data.get('last_name')}")
            logger.warning(f"   Username: @{user_data.get('username', 'no_username')}")
            logger.warning(f"   Time: {datetime.now()}")
            logger.warning(f"   This ID is NOT in whitelist: {ALLOWED_USERS}")
            logger.warning("=" * 50)

            # Отправляем четкую ошибку
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "ACCESS_DENIED",
                    "message": "Sizning Telegram ID ruxsat berilmagan",
                    "telegram_id": telegram_id,
                    "username": user_data.get('username'),
                    "instruction": "Administrator bilan bog'laning: @Oqtosh_Soy"
                }
            )

        # Шаг 4: Доступ разрешен - создаем/обновляем пользователя
        logger.info(f"✅ Access GRANTED for Telegram ID: {telegram_id}")

        # Проверяем существующего пользователя
        user = db.query(User).filter(User.telegram_id == telegram_id).first()

        if not user:
            # Создаем нового пользователя
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
            logger.info(f"Created new user with role: {role.value}")
        else:
            # Обновляем существующего
            user.first_name = user_data.get("first_name", user.first_name)
            user.last_name = user_data.get("last_name", user.last_name)
            user.username = user_data.get("username", user.username)
            db.commit()
            logger.info(f"Updated existing user with role: {user.role.value}")

        # Создаем токен
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"user_id": user.id},
            expires_delta=access_token_expires
        )

        logger.info(f"✅ Authentication successful for {user.username}")
        logger.info("=" * 50)

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
        # HTTP ошибки пробрасываем как есть
        raise
    except Exception as e:
        # Любые другие ошибки логируем и блокируем
        logger.error(f"❌ Critical authentication error: {e}")
        logger.error("=" * 50)

        # НЕ ДАЕМ НИКАКИХ ОБХОДОВ!
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed. Contact administrator."
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
        current_user: User = Depends(get_current_user)
):
    """Get current user info"""
    return current_user
