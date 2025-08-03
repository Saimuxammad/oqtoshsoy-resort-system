from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
from ..database import get_db
from ..models.user import User, UserRole

# JWT настройки
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 дней

security = HTTPBearer(auto_error=False)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_current_user(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        db: Session = Depends(get_db)
) -> User:
    """Get current user from token"""
    # Для разработки и тестирования - создаем/получаем тестового пользователя

    # Если нет credentials или это браузер без Telegram
    if not credentials or not credentials.credentials:
        # Создаем тестового админа для разработки
        test_user = db.query(User).filter(User.telegram_id == 123456789).first()
        if not test_user:
            test_user = User(
                telegram_id=123456789,
                first_name="Test",
                last_name="Admin",
                username="test_admin",
                is_admin=True,
                role=UserRole.ADMIN if hasattr(User, 'role') else None
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
        return test_user

    token = credentials.credentials

    # Для development токенов
    if token.startswith("dev_") or token.startswith("fallback_"):
        admin_user = db.query(User).filter(User.is_admin == True).first()
        if not admin_user:
            admin_user = User(
                telegram_id=987654321,
                first_name="Admin",
                last_name="User",
                username="admin_user",
                is_admin=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
        return admin_user

    # Проверяем JWT токен
    payload = verify_token(token)
    if not payload:
        # В случае невалидного токена возвращаем тестового пользователя
        return get_current_user(None, db)

    user_id = payload.get("user_id")
    if not user_id:
        return get_current_user(None, db)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return get_current_user(None, db)

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin privileges"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


async def get_current_user_ws(
        token: str,
        db: Session
) -> Optional[User]:
    """Get current user for WebSocket connections"""
    if not token:
        return None

    # Для development токенов
    if token.startswith("dev_") or token.startswith("fallback_"):
        admin_user = db.query(User).filter(User.is_admin == True).first()
        if not admin_user:
            admin_user = User(
                telegram_id=987654321,
                first_name="Admin",
                last_name="User",
                username="admin_user",
                is_admin=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
        return admin_user

    # Проверяем JWT токен
    payload = verify_token(token)
    if not payload:
        return None

    user_id = payload.get("user_id")
    if not user_id:
        return None

    user = db.query(User).filter(User.id == user_id).first()
    return user