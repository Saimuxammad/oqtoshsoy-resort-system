from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from jose import JWTError, jwt
from datetime import datetime, timedelta

from ..database import get_db
from ..models.user import User
from ..config import settings

security = HTTPBearer(auto_error=False)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt


async def get_current_user(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        db: Session = Depends(get_db)
) -> User:
    # Для development режима без токена
    if settings.environment == "development" and not credentials:
        user = db.query(User).filter(User.telegram_id == 123456789).first()
        if user:
            return user

        # Создаем тестового пользователя
        user = User(
            telegram_id=123456789,
            first_name="Test",
            last_name="User",
            username="testuser",
            is_admin=True,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    # Production режим - проверяем токен
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=["HS256"])
        telegram_id: int = int(payload.get("sub"))
        if telegram_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def get_current_user_ws(token: str, db: Session) -> Optional[User]:
    """Get current user for WebSocket connection"""
    # В режиме разработки/тестирования возвращаем тестового пользователя
    if settings.environment == "development":
        return db.query(User).filter(User.telegram_id == 123456789).first()

    # В production проверяем токен
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        telegram_id: int = payload.get("sub")
        if telegram_id is None:
            return None
    except JWTError:
        return None

    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    return user