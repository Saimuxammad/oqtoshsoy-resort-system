from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from ..database import get_db
from ..schemas.booking import Booking, BookingCreate, BookingUpdate
from ..models.booking import Booking as BookingModel
from ..models.room import Room
from ..services.booking_service import BookingService
from ..services.history_service import HistoryService
from ..services.notification_service import notification_service
from ..websocket.manager import manager
from ..utils.dependencies import get_current_user, require_admin

router = APIRouter()


@router.get("/", response_model=List[Booking])
async def get_bookings(
        skip: int = 0,
        limit: int = 100,
        room_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get all bookings with optional filters"""
    query = db.query(BookingModel)

    if room_id:
        query = query.filter(BookingModel.room_id == room_id)

    if start_date:
        query = query.filter(BookingModel.end_date >= start_date)

    if end_date:
        query = query.filter(BookingModel.start_date <= end_date)

    bookings = query.order_by(BookingModel.start_date).offset(skip).limit(limit).all()
    return bookings


@router.get("/{booking_id}", response_model=Booking)
async def get_booking(
        booking_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get specific booking by ID"""
    booking = BookingService.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@router.post("/", response_model=Booking)
async def create_booking(
        booking: BookingCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Create new booking"""
    # Check if room exists
    room = db.query(Room).filter(Room.id == booking.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # Check availability
    if not BookingService.check_availability(db, booking.room_id, booking.start_date, booking.end_date):
        raise HTTPException(status_code=400, detail="Room is not available for selected dates")

    # Create booking
    new_booking = BookingService.create_booking(db, booking, current_user.id)

    # Log history
    HistoryService.log_action(
        db=db,
        user_id=current_user.id,
        entity_type="booking",
        entity_id=new_booking.id,
        action="create",
        description=f"Created booking for room №{room.room_number} from {booking.start_date} to {booking.end_date}"
    )

    # Send notification
    await notification_service.send_booking_created(db, new_booking, room, current_user)

    # Broadcast via WebSocket
    await manager.broadcast_booking_update(new_booking.id, "create", {
        "room_id": room.id,
        "start_date": str(booking.start_date),
        "end_date": str(booking.end_date)
    })

    return new_booking


# Общая функция для обновления бронирования
async def _update_booking_handler(
        booking_id: int,
        booking_update: BookingUpdate,
        db: Session,
        current_user
):
    """Common handler for updating booking"""
    booking = BookingService.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Check if user can update (admin or creator)
    if not current_user.is_admin and booking.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this booking")

    # Store old values for history
    old_values = {
        "start_date": str(booking.start_date),
        "end_date": str(booking.end_date),
        "guest_name": booking.guest_name,
        "notes": booking.notes
    }

    # If dates are being updated, check availability
    if booking_update.start_date or booking_update.end_date:
        start = booking_update.start_date or booking.start_date
        end = booking_update.end_date or booking.end_date

        if not BookingService.check_availability(db, booking.room_id, start, end, exclude_booking_id=booking_id):
            raise HTTPException(status_code=400, detail="Room is not available for selected dates")

    # Update booking
    updated_booking = BookingService.update_booking(db, booking_id, booking_update)

    # Log history
    new_values = {}
    update_dict = booking_update.dict(exclude_unset=True)
    for key, value in update_dict.items():
        new_values[key] = str(value) if value is not None else None

    HistoryService.log_action(
        db=db,
        user_id=current_user.id,
        entity_type="booking",
        entity_id=booking_id,
        action="update",
        changes={"old": old_values, "new": new_values},
        description=f"Updated booking for room №{booking.room.room_number}"
    )

    # Broadcast via WebSocket
    await manager.broadcast_booking_update(booking_id, "update", update_dict)

    return updated_booking


@router.patch("/{booking_id}", response_model=Booking)
async def update_booking_patch(
        booking_id: int,
        booking_update: BookingUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Update booking using PATCH method"""
    return await _update_booking_handler(booking_id, booking_update, db, current_user)


@router.put("/{booking_id}", response_model=Booking)
async def update_booking_put(
        booking_id: int,
        booking_update: BookingUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Update booking using PUT method"""
    return await _update_booking_handler(booking_id, booking_update, db, current_user)


@router.delete("/{booking_id}")
async def delete_booking(
        booking_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)  # Изменено: теперь не требует админа
):
    """Delete booking"""
    booking = BookingService.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Проверяем права: админ может удалять любые брони, обычный пользователь - только свои
    if not current_user.is_admin and booking.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this booking")

    room = booking.room

    # Log history before deletion
    HistoryService.log_action(
        db=db,
        user_id=current_user.id,
        entity_type="booking",
        entity_id=booking_id,
        action="delete",
        description=f"Deleted booking for room №{room.room_number} from {booking.start_date} to {booking.end_date}"
    )

    # Delete booking
    if not BookingService.delete_booking(db, booking_id):
        raise HTTPException(status_code=404, detail="Booking not found")

    # Send notification
    await notification_service.send_booking_cancelled(db, booking, room, current_user)

    # Broadcast via WebSocket
    await manager.broadcast_booking_update(booking_id, "delete", {"room_id": room.id})

    return {"message": "Booking deleted successfully"}


@router.get("/check-availability/", response_model=dict)
async def check_availability(
        room_id: int = Query(...),
        start_date: date = Query(...),
        end_date: date = Query(...),
        exclude_booking_id: Optional[int] = Query(None),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Check if room is available for given dates"""
    is_available = BookingService.check_availability(
        db, room_id, start_date, end_date, exclude_booking_id
    )

    return {
        "available": is_available,
        "room_id": room_id,
        "start_date": str(start_date),
        "end_date": str(end_date)
    }