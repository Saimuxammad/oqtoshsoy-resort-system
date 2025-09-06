# file: backend/app/utils/dependencies.py
from fastapi import Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

from ..database import get_db
from ..models.user import User, UserRole
from ..config.settings import get_settings

settings = get_settings()
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создание JWT токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
) -> User:
    """Получает пользователя из HTTP Bearer токена."""
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user


# ✅ ВОТ НЕДОСТАЮЩАЯ ФУНКЦИЯ, КОТОРУЮ МЫ ВОЗВРАЩАЕМ
async def get_current_user_ws(
        token: str = Query(...),
        db: Session = Depends(get_db)
) -> User:
    """Получает пользователя для WebSocket соединения из токена в query параметрах."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise JWTError()
    except JWTError:
        # В WebSocket мы не можем выбросить HTTPException, поэтому просто вернем None,
        # а вызывающий код обработает это.
        return None

    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        return None

    return user


# ✅ КОНЕЦ НОВОЙ ФУНКЦИИ


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Требует роль админа или выше"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


async def require_super_admin(current_user: User = Depends(get_current_user)) -> User:
    """Требует роль только супер-администратора"""
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Super Admin access required")
    return current_user