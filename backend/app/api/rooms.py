from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime

from ..database import get_db
from ..schemas.room import Room, RoomCreate, RoomUpdate
from ..models.room import Room as RoomModel
from ..models.booking import Booking
from ..services.room_service import RoomService
from ..utils.dependencies import get_current_user, require_admin

router = APIRouter()


@router.get("/list", response_model=List[Room])
async def get_rooms(
    skip: int = 0,
    limit: int = 100,
    room_type: Optional[str] = None,
    is_available: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get all rooms with optional filters"""
    try:
        print(f"[API] Filters: type={room_type}, available={is_available}")
        query = db.query(RoomModel)

        if room_type:
            query = query.filter(RoomModel.room_type == room_type)

        if is_available is not None:
            today = date.today()
            booked_room_ids = db.query(Booking.room_id).filter(
                Booking.start_date <= today,
                Booking.end_date >= today
            ).scalar_subquery()

            if is_available:
                query = query.filter(~RoomModel.id.in_(booked_room_ids))
            else:
                query = query.filter(RoomModel.id.in_(booked_room_ids))

        rooms = query.offset(skip).limit(limit).all()
        print(f"[API] Rooms found: {len(rooms)}")

        result = []
        today = date.today()
        for room in rooms:
            room_data = Room.from_orm(room)

            # Current booking
            current_booking = db.query(Booking).filter(
                Booking.room_id == room.id,
                Booking.start_date <= today,
                Booking.end_date >= today
            ).first()

            if current_booking:
                room_data.current_booking = {
                    "id": current_booking.id,
                    "start_date": current_booking.start_date,
                    "end_date": current_booking.end_date,
                    "guest_name": current_booking.guest_name
                }
                room_data.is_available = False
            else:
                room_data.is_available = True

            # Upcoming bookings
            upcoming = db.query(Booking).filter(
                Booking.room_id == room.id,
                Booking.start_date > today
            ).order_by(Booking.start_date).limit(5).all()

            room_data.upcoming_bookings = [
                {
                    "id": b.id,
                    "start_date": b.start_date,
                    "end_date": b.end_date,
                    "guest_name": b.guest_name
                } for b in upcoming
            ]

            result.append(room_data)

        return result

    except Exception as e:
        print(f"[API] /rooms/list error: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@router.get("/{room_id}", response_model=Room)
async def get_room(
        room_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get specific room by ID"""
    room = RoomService.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    room_data = Room.from_orm(room)

    # Get current booking
    today = date.today()
    current_booking = db.query(Booking).filter(
        Booking.room_id == room.id,
        Booking.start_date <= today,
        Booking.end_date >= today
    ).first()

    if current_booking:
        room_data.current_booking = {
            "id": current_booking.id,
            "start_date": current_booking.start_date,
            "end_date": current_booking.end_date,
            "guest_name": current_booking.guest_name
        }
        room_data.is_available = False

    return room_data


@router.post("/", response_model=Room)
async def create_room(
        room: RoomCreate,
        db: Session = Depends(get_db),
        current_user=Depends(require_admin)
):
    """Create new room (admin only)"""
    # Check if room number already exists
    existing = RoomService.get_room_by_number(db, room.room_number)
    if existing:
        raise HTTPException(status_code=400, detail="Room number already exists")

    return RoomService.create_room(db, room)


@router.patch("/{room_id}", response_model=Room)
async def update_room(
        room_id: int,
        room_update: RoomUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(require_admin)
):
    """Update room (admin only)"""
    room = RoomService.update_room(db, room_id, room_update)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.get("/{room_id}/availability")
async def check_room_availability(
        room_id: int,
        start_date: date = Query(...),
        end_date: date = Query(...),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Check room availability for date range"""
    room = RoomService.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # Check for overlapping bookings
    overlapping = db.query(Booking).filter(
        Booking.room_id == room_id,
        Booking.start_date <= end_date,
        Booking.end_date >= start_date
    ).count()

    return {
        "room_id": room_id,
        "start_date": start_date,
        "end_date": end_date,
        "is_available": overlapping == 0
    }