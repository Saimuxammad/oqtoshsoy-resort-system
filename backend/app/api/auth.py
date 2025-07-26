from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict

from ..database import get_db
from ..schemas.user import User, TelegramAuthData
from ..models.user import User as UserModel
from ..utils.telegram import verify_telegram_auth, is_admin_user
from ..utils.dependencies import create_access_token
from ..config import settings

router = APIRouter()


@router.post("/telegram")
async def telegram_auth(auth_data: TelegramAuthData, db: Session = Depends(get_db)):
    """Authenticate user via Telegram Web App"""

    # В development режиме упрощенная проверка
    if settings.environment == "development":
        user = db.query(UserModel).filter(UserModel.telegram_id == auth_data.id).first()

        if not user:
            user = UserModel(
                telegram_id=auth_data.id,
                first_name=auth_data.first_name,
                last_name=auth_data.last_name,
                username=auth_data.username,
                is_admin=is_admin_user(auth_data.id)
            )
            db.add(user)
        else:
            user.last_login = datetime.utcnow()

        db.commit()
        db.refresh(user)

        # Создаем токен
        access_token = create_access_token(data={"sub": str(user.telegram_id)})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "is_admin": user.is_admin
            }
        }

    # Production режим с полной проверкой
    if not verify_telegram_auth(auth_data.dict()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication data"
        )

    # Создаем или обновляем пользовател