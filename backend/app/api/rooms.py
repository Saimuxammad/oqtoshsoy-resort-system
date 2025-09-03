from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from ..database import get_db
from ..models.room import Room as RoomModel, RoomType
from ..models.booking import Booking as BookingModel
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

        # Фильтрация по типу комнаты
        if room_type:
            # Преобразуем строку в enum если нужно
            for rt in RoomType:
                if rt.value == room_type:
                    query = query.filter(RoomModel.room_type == rt)
                    break

        rooms = query.offset(skip).limit(limit).all()

        # Преобразуем в список словарей с полной информацией
        result = []
        for room in rooms:
            # Получаем текущее бронирование если есть
            current_booking = db.query(BookingModel).filter(
                BookingModel.room_id == room.id,
                BookingModel.start_date <= date.today(),
                BookingModel.end_date >= date.today()
            ).first()

            room_data = {
                "id": room.id,
                "room_number": room.room_number,
                "room_type": room.room_type.value if hasattr(room.room_type, 'value') else str(room.room_type),
                "capacity": room.capacity if room.capacity else 2,
                "price_per_night": float(room.price_per_night) if room.price_per_night else 500000,
                "description": room.description if room.description else "",
                "amenities": room.amenities if room.amenities else "",
                "created_at": room.created_at.isoformat() if room.created_at else "2024-01-01T00:00:00",
                "updated_at": room.updated_at.isoformat() if room.updated_at else "2024-01-01T00:00:00",
                "is_available": current_booking is None,
                "current_booking": {
                    "id": current_booking.id,
                    "start_date": str(current_booking.start_date),
                    "end_date": str(current_booking.end_date),
                    "guest_name": current_booking.guest_name
                } if current_booking else None
            }

            # Фильтрация по статусу
            if status:
                if status == "available" and not room_data["is_available"]:
                    continue
                elif status == "occupied" and room_data["is_available"]:
                    continue

            result.append(room_data)

        return result

    except Exception as e:
        print(f"Error in get_rooms: {str(e)}")
        import traceback
        traceback.print_exc()
        # Не возвращаем пустой массив, а пробрасываем ошибку
        raise HTTPException(status_code=500, detail=str(e))


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

        # Получаем текущее бронирование
        current_booking = db.query(BookingModel).filter(
            BookingModel.room_id == room.id,
            BookingModel.start_date <= date.today(),
            BookingModel.end_date >= date.today()
        ).first()

        return {
            "id": room.id,
            "room_number": room.room_number,
            "room_type": room.room_type.value if hasattr(room.room_type, 'value') else str(room.room_type),
            "capacity": room.capacity if room.capacity else 2,
            "price_per_night": float(room.price_per_night) if room.price_per_night else 500000,
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
    return {"message": "Room updated successfully", "room_id": room_id}


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
        "room_number": room.room_number,
        "start_date": start_date,
        "end_date": end_date,
        "is_available": is_available
    }