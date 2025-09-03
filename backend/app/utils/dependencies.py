from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

from ..database import get_db
from ..models.user import User, UserRole

# JWT settings
SECRET_KEY = "your-secret-key-here"  # В production используйте переменную окружения
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создание JWT токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
) -> User:
    """Получение текущего пользователя из токена"""
    token = credentials.credentials

    # Для dev режима
    if token == "dev_token" or token == "dev_token_123456":
        # Возвращаем тестового админа
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
            db.refresh(test_user)
        return test_user

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    return user


def require_permission(permission: str):
    """Декоратор для проверки разрешений"""

    async def permission_checker(current_user: User = Depends(get_current_user)):
        if not current_user.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You don't have permission to {permission}"
            )
        return current_user

    return permission_checker


# Готовые проверки для разных ролей
async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Требует роль админа или выше"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def require_manager(current_user: User = Depends(get_current_user)) -> User:
    """Требует роль менеджера или выше"""
    if current_user.role not in [UserRole.MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required"
        )
    return current_user


async def require_operator(current_user: User = Depends(get_current_user)) -> User:
    """Требует роль оператора или выше"""
    if current_user.role == UserRole.USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operator access required"
        )
    return current_user