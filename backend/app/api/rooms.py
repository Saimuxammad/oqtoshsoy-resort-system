from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..services.room_service import RoomService
from ..schemas.room import Room as RoomSchema  # Убедитесь, что у вас есть Pydantic-схема Room
from ..utils.dependencies import get_current_user
from ..models.user import User  # Импортируем модель User для current_user

# Создаем роутер
router = APIRouter()


# Этот эндпоинт будет отвечать на запросы /api/rooms и /api/rooms/
@router.get("", response_model=List[RoomSchema])
@router.get("/", response_model=List[RoomSchema])
async def get_all_rooms(
        room_type: Optional[str] = None,
        status: Optional[str] = None,
        db: Session = Depends(get_db),
        # Защищаем эндпоинт. Без валидного токена сюда попасть нельзя.
        current_user: User = Depends(get_current_user)
):
    """
    Получает список всех комнат с актуальным статусом (свободна/занята) и фильтрами.
    Вся сложная логика находится в RoomService.
    """
    try:
        # Вызываем метод из сервиса, который умеет фильтровать и определять статус
        rooms = RoomService.get_rooms_with_status(
            db=db,
            room_type_filter=room_type,
            status_filter=status
        )
        return rooms
    except Exception as e:
        # Если в сервисе произойдет ошибка, мы вернем корректный ответ 500
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


@router.get("/{room_id}", response_model=RoomSchema)
async def get_single_room(
        room_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Получает одну конкретную комнату по её ID.
    """
    # Вызываем метод из сервиса для получения одной комнаты
    room = RoomService.get_room_with_status(db, room_id=room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    return room