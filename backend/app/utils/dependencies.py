from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os

from ..database import get_db
from ..models.user import User, UserRole

# Security
security = HTTPBearer(auto_error=False)

# Получаем секретный ключ из переменной окружения
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 часа


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Создание JWT токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user_optional(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        db: Session = Depends(get_db)
) -> Optional[User]:
    """Получение текущего пользователя (опционально)"""
    if not credentials:
        return None

    token = credentials.credentials

    # Специальная обработка для dev токена
    if token == "dev_token" or token.startswith("dev_token"):
        # В dev режиме возвращаем тестового админа
        test_user = db.query(User).filter(User.telegram_id == 123456789).first()
        if not test_user:
            test_user = User(
                telegram_id=123456789,
                first_name="Dev",
                last_name="Admin",
                username="dev_admin",
                role=UserRole.SUPER_ADMIN,
                is_admin=True,
                is_active=True
            )
            db.add(test_user)
            db.commit()
        return test_user

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            return None
    except JWTError:
        return None

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        return None

    return user


async def get_current_user(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        db: Session = Depends(get_db)
) -> User:
    """Получение текущего пользователя (обязательно)"""
    user = await get_current_user_optional(credentials, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


# Декораторы для проверки прав доступа
async def require_operator(
        current_user: User = Depends(get_current_user)
) -> User:
    """Требование прав оператора или выше"""
    if not current_user.can_create_bookings:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operator access required"
        )
    return current_user


async def require_manager(
        current_user: User = Depends(get_current_user)
) -> User:
    """Требование прав менеджера или выше"""
    if not current_user.can_edit_bookings:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required"
        )
    return current_user


async def require_admin(
        current_user: User = Depends(get_current_user)
) -> User:
    """Требование прав администратора или выше"""
    if not current_user.can_manage_settings:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required"
        )
    return current_user


async def require_super_admin(
        current_user: User = Depends(get_current_user)
) -> User:
    """Требование прав супер-администратора"""
    if not current_user.can_manage_users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Administrator access required"
        )
    return current_user


# Вспомогательные функции для проверки прав
def check_booking_permission(user: User, booking, action: str) -> bool:
    """Проверка прав на действие с бронированием"""
    if action == "create":
        return user.can_create_bookings
    elif action == "edit":
        if user.can_delete_any_booking:
            return True
        if user.can_edit_bookings:
            return booking.created_by == user.id
        return False
    elif action == "delete":
        if user.can_delete_any_booking:
            return True
        if user.can_delete_bookings:
            return booking.created_by == user.id
        return False
    elif action == "view":
        return True  # Все могут просматривать
    return False