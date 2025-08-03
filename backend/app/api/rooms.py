from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from ..database import get_db
from ..schemas.room import Room, RoomUpdate, RoomStatus
from ..models.room import Room as RoomModel, RoomType
from ..services.room_service import RoomService
from ..utils.dependencies import get_current_user, require_admin

router = APIRouter()


@router.get("/", response_model=List[Room])
async def get_rooms(
        skip: int = 0,
        limit: int = 100,
        room_type: Optional[str] = None,
        status: Optional[str] = None,
        db: Session = Depends(get_db)
):
    """Get all rooms with optional filters"""
    query = db.query(RoomModel)

    if room_type:
        query = query.filter(RoomModel.room_type == room_type)

    if status:
        # Фильтруем по текущей занятости
        if status == "available":
            # Здесь нужна более сложная логика для проверки доступности
            pass
        elif status == "occupied":
            # Здесь нужна более сложная логика для проверки занятости
            pass

    rooms = query.offset(skip).limit(limit).all()

    # Добавляем информацию о текущем статусе для каждой комнаты
    for room in rooms:
        room.is_available = RoomService.is_room_available(db, room.id, date.today(), date.today())

    return rooms


@router.get("/{room_id}", response_model=Room)
async def get_room(
        room_id: int,
        db: Session = Depends(get_db)
):
    """Get specific room by ID"""
    room = RoomService.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # Добавляем информацию о текущем статусе
    room.is_available = RoomService.is_room_available(db, room.id, date.today(), date.today())

    return room


@router.patch("/{room_id}", response_model=Room)
async def update_room(
        room_id: int,
        room_update: RoomUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(require_admin)
):
    """Update room information (admin only)"""
    room = RoomService.update_room(db, room_id, room_update)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


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


@router.get("/{room_id}/bookings", response_model=List[dict])
async def get_room_bookings(
        room_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get bookings for a specific room"""
    room = RoomService.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    bookings = RoomService.get_room_bookings(db, room_id, start_date, end_date)

    return [
        {
            "id": booking.id,
            "start_date": booking.start_date,
            "end_date": booking.end_date,
            "guest_name": booking.guest_name,
            "created_by": booking.created_by
        }
        for booking in bookings
    ]