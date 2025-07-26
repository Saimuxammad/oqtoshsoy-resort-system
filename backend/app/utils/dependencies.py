from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models.user import User
from ..config import settings

security = HTTPBearer(auto_error=False)


async def get_current_user(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        db: Session = Depends(get_db)
) -> User:
    # Режим разработки - возвращаем тестового пользователя
    if settings.environment == "development":
        # Проверяем есть ли тестовый пользователь в БД
        test_user = db.query(User).filter(User.telegram_id == 123456789).first()
        if not test_user:
            # Создаем тестового пользователя
            test_user = User(
                telegram_id=123456789,
                first_name="Test",
                last_name="User",
                username="testuser",
                is_admin=True,
                is_active=True
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
        return test_user

    # Production код
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Здесь должна быть проверка JWT токена
    # Для разработки просто возвращаем тестового пользователя
    user = db.query(User).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


async def get_current_user_ws(token: str, db: Session) -> Optional[User]:
    # Для разработки возвращаем тестового пользователя
    if settings.environment == "development":
        return db.query(User).filter(User.telegram_id == 123456789).first()
    return None


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

from jose import JWTError, jwt
from datetime import datetime, timedelta

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)  # 7 дней для dev
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt