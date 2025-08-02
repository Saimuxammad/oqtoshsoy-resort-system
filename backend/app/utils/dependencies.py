from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
from ..database import get_db
from ..models.user import User

# JWT настройки
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 дней

security = HTTPBearer(auto_error=False)


def get_current_user(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        db: Session = Depends(get_db)
) -> User:
    """Get current user from token"""
    # Для разработки - создаем/получаем тестового пользователя

    # Проверяем, есть ли токен
    if not credentials:
        # Создаем гостевого пользователя для разработки
        guest_user = db.query(User).filter(User.telegram_id == 123456789).first()
        if not guest_user:
            guest_user = User(
                telegram_id=123456789,
                first_name="Guest",
                last_name="User",
                username="guest_user",
                is_admin=False
            )
            db.add(guest_user)
            db.commit()
            db.refresh(guest_user)
        return guest_user

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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin privileges"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user