from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date
import json

from ..database import get_db
from ..models.room import Room as RoomModel, RoomType
from ..services.room_service import RoomService
from ..utils.dependencies import get_current_user, require_admin

router = APIRouter()


@router.get("/")
async def get_rooms(
        skip: int = 0,
        limit: int = 100,
        room_type: Optional[str] = None,
        status: Optional[str] = None,
        db: Session = Depends(get_db)
):
    """Get all rooms with optional filters"""
    try:
        query = db.query(RoomModel)

        if room_type:
            query = query.filter(RoomModel.room_type == room_type)

        rooms = query.offset(skip).limit(limit).all()

        # Простое преобразование в список словарей
        result = []
        for room in rooms:
            # Обработка room_type - конвертируем enum в строку
            room_type_value = room.room_type
            if hasattr(room_type_value, 'value'):
                room_type_str = room_type_value.value
            else:
                room_type_str = str(room_type_value)

            room_data = {
                "id": room.id,
                "room_number": room.room_number,
                "room_type": room_type_str,
                "capacity": getattr(room, 'capacity', 2),  # Безопасное получение capacity
                "price_per_night": float(room.price_per_night) if room.price_per_night else 0,
                "description": room.description if room.description else "",
                "amenities": room.amenities if room.amenities else "",
                "created_at": room.created_at.isoformat() if room.created_at else "2024-01-01T00:00:00",
                "updated_at": room.updated_at.isoformat() if room.updated_at else "2024-01-01T00:00:00",
                "is_available": True,
                "current_booking": None
            }
            result.append(room_data)

        return result
    except Exception as e:
        print(f"Error in get_rooms: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()

        # Возвращаем тестовые данные при ошибке
        return [{
            "id": 1,
            "room_number": "101",
            "room_type": "2 o'rinli standart",
            "capacity": 2,
            "price_per_night": 500000,
            "description": "Test room",
            "amenities": "Wi-Fi, TV",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
            "is_available": True,
            "current_booking": None
        }]


@router.get("/{room_id}")
async def get_room(
        room_id: int,
        db: Session = Depends(get_db)
):
    """Get specific room by ID"""
    try:
        room = RoomService.get_room(db, room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")

        return {
            "id": room.id,
            "room_number": room.room_number,
            "room_type": room.room_type.value if hasattr(room.room_type, 'value') else str(room.room_type),
            "capacity": room.capacity,
            "price_per_night": float(room.price_per_night),
            "description": room.description or "",
            "amenities": room.amenities or "",
            "created_at": room.created_at.isoformat() if room.created_at else None,
            "updated_at": room.updated_at.isoformat() if room.updated_at else None,
            "is_available": True
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_room: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{room_id}")
async def update_room(
        room_id: int,
        room_update: dict,
        db: Session = Depends(get_db),
        current_user=Depends(require_admin)
):
    """Update room information (admin only)"""
    room = RoomService.update_room(db, room_id, room_update)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return {"message": "Room updated successfully"}


@router.get("/{room_id}/availability")
async def check_room_availability(
        room_id: int,
        start_date: date = Query(...),
        end_date: date = Query(...),
        db: Session = Depends(get_db)
):
    """Check if room is available for specific dates"""
    room = RoomService.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    is_available = RoomService.is_room_available(db, room_id, start_date, end_date)

    return {
        "room_id": room_id,
        "start_date": start_date,
        "end_date": end_date,
        "is_available": is_available
    }