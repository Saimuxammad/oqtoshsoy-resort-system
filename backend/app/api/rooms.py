from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from ..database import get_db
from ..models.room import Room as RoomModel
from ..models.booking import Booking as BookingModel
from ..utils.dependencies import get_current_user

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
        # Начинаем запрос
        query = db.query(RoomModel)

        # Фильтр по типу комнаты если указан
        if room_type:
            query = query.filter(RoomModel.room_type == room_type)

        # Получаем все комнаты
        rooms = query.offset(skip).limit(limit).all()

        # Преобразуем в список словарей
        result = []
        for room in rooms:
            # Проверяем текущее бронирование
            current_booking = None
            if status:  # Только если нужен фильтр по статусу
                current_booking = db.query(BookingModel).filter(
                    BookingModel.room_id == room.id,
                    BookingModel.start_date <= date.today(),
                    BookingModel.end_date >= date.today()
                ).first()

                # Применяем фильтр по статусу
                if status == "available" and current_booking:
                    continue  # Пропускаем занятые комнаты
                elif status == "occupied" and not current_booking:
                    continue  # Пропускаем свободные комнаты

            # Формируем данные комнаты
            room_data = {
                "id": room.id,
                "room_number": room.room_number,
                "room_type": room.room_type,  # Теперь это просто строка
                "capacity": room.capacity if room.capacity else 2,
                "price_per_night": float(room.price_per_night) if room.price_per_night else 500000.0,
                "description": room.description or "",
                "amenities": room.amenities or "",
                "created_at": room.created_at.isoformat() if room.created_at else "2024-01-01T00:00:00",
                "updated_at": room.updated_at.isoformat() if room.updated_at else "2024-01-01T00:00:00",
                "is_available": current_booking is None if status else True,
                "current_booking": None  # Упрощаем для начала
            }

            result.append(room_data)

        return result

    except Exception as e:
        print(f"Error in get_rooms: {str(e)}")
        import traceback
        traceback.print_exc()
        # Возвращаем пустой массив при ошибке, чтобы frontend не падал
        return []


@router.get("/{room_id}")
async def get_room(
        room_id: int,
        db: Session = Depends(get_db)
):
    """Get specific room by ID"""
    try:
        room = db.query(RoomModel).filter(RoomModel.id == room_id).first()
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")

        # Проверяем текущее бронирование
        current_booking = db.query(BookingModel).filter(
            BookingModel.room_id == room.id,
            BookingModel.start_date <= date.today(),
            BookingModel.end_date >= date.today()
        ).first()

        return {
            "id": room.id,
            "room_number": room.room_number,
            "room_type": room.room_type,
            "capacity": room.capacity if room.capacity else 2,
            "price_per_night": float(room.price_per_night) if room.price_per_night else 500000.0,
            "description": room.description or "",
            "amenities": room.amenities or "",
            "created_at": room.created_at.isoformat() if room.created_at else None,
            "updated_at": room.updated_at.isoformat() if room.updated_at else None,
            "is_available": current_booking is None,
            "current_booking": {
                "id": current_booking.id,
                "start_date": str(current_booking.start_date),
                "end_date": str(current_booking.end_date),
                "guest_name": current_booking.guest_name
            } if current_booking else None
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_room: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{room_id}/availability")
async def check_room_availability(
        room_id: int,
        start_date: date = Query(...),
        end_date: date = Query(...),
        db: Session = Depends(get_db)
):
    """Check if room is available for specific dates"""
    room = db.query(RoomModel).filter(RoomModel.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # Проверяем пересечение с существующими бронированиями
    conflicting_bookings = db.query(BookingModel).filter(
        BookingModel.room_id == room_id,
        BookingModel.start_date <= end_date,
        BookingModel.end_date >= start_date
    ).count()

    is_available = conflicting_bookings == 0

    return {
        "room_id": room_id,
        "room_number": room.room_number,
        "start_date": start_date,
        "end_date": end_date,
        "is_available": is_available
    }