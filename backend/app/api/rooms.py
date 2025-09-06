# file: backend/app/api/rooms.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from ..database import get_db
from ..services.room_service import RoomService
from ..schemas.room import Room as RoomSchema # Предполагаем, что у вас есть Pydantic схема
from ..utils.dependencies import get_current_user

router = APIRouter()

@router.get("/", response_model=List[RoomSchema])
async def get_all_rooms_with_status(
    room_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    # ✅ Защищаем эндпоинт. Без валидного токена сюда не попасть.
    current_user = Depends(get_current_user)
):
    """Получить все комнаты, используя сервис."""
    try:
        # ✅ Вся сложная логика спрятана в сервисе
        rooms = RoomService.get_rooms_with_status(db, room_type_filter=room_type, status_filter=status)
        return rooms
    except Exception as e:
        # Логирование ошибки можно добавить здесь
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{room_id}", response_model=RoomSchema)
async def get_single_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить одну комнату по ID."""
    room = RoomService.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room