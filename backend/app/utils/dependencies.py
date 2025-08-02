from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models.user import User

security = HTTPBearer(auto_error=False)


def get_current_user(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        db: Session = Depends(get_db)
) -> User:
    """Get current user from token (simplified for development)"""
    # Для разработки - создаем/получаем тестового пользователя
    # В production здесь должна быть проверка JWT токена

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

    # Для development токенов
    if credentials.credentials.startswith("dev_") or credentials.credentials.startswith("fallback_"):
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

    # В production здесь должна быть проверка реального токена
    # Пока возвращаем тестового пользователя
    test_user = db.query(User).first()
    if not test_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return test_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin privileges"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user