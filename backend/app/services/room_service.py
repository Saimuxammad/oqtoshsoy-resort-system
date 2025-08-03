from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from ..models.room import Room, RoomType
from ..models.booking import Booking


class RoomService:
    @staticmethod
    def initialize_rooms(db: Session):
        """Initialize rooms with default data if empty"""
        if db.query(Room).count() > 0:
            return

        rooms_data = [
            # 2 o'rinli standart
            {"room_number": "101", "room_type": RoomType.STANDARD_DOUBLE, "capacity": 2, "price_per_night": 500000},
            {"room_number": "102", "room_type": RoomType.STANDARD_DOUBLE, "capacity": 2, "price_per_night": 500000},
            {"room_number": "103", "room_type": RoomType.STANDARD_DOUBLE, "capacity": 2, "price_per_night": 500000},
            {"room_number": "104", "room_type": RoomType.STANDARD_DOUBLE, "capacity": 2, "price_per_night": 500000},

            # 4 o'rinli standart
            {"room_number": "201", "room_type": RoomType.STANDARD_QUAD, "capacity": 4, "price_per_night": 700000},
            {"room_number": "202", "room_type": RoomType.STANDARD_QUAD, "capacity": 4, "price_per_night": 700000},
            {"room_number": "203", "room_type": RoomType.STANDARD_QUAD, "capacity": 4, "price_per_night": 700000},

            # 2 o'rinli lyuks
            {"room_number": "301", "room_type": RoomType.LUX_DOUBLE, "capacity": 2, "price_per_night": 800000},
            {"room_number": "302", "room_type": RoomType.LUX_DOUBLE, "capacity": 2, "price_per_night": 800000},

            # 4 o'rinli kichik VIP
            {"room_number": "401", "room_type": RoomType.VIP_SMALL, "capacity": 4, "price_per_night": 1000000},
            {"room_number": "402", "room_type": RoomType.VIP_SMALL, "capacity": 4, "price_per_night": 1000000},

            # 4 o'rinli katta VIP
            {"room_number": "501", "room_type": RoomType.VIP_LARGE, "capacity": 4, "price_per_night": 1200000},

            # 4 o'rinli apartament
            {"room_number": "601", "room_type": RoomType.APARTMENT, "capacity": 4, "price_per_night": 1500000},

            # Kottedj
            {"room_number": "701", "room_type": RoomType.COTTAGE, "capacity": 6, "price_per_night": 2000000},

            # Prezident apartamenti
            {"room_number": "801", "room_type": RoomType.PRESIDENT, "capacity": 8, "price_per_night": 3000000},
        ]

        for room_data in rooms_data:
            room = Room(**room_data)
            db.add(room)

        db.commit()

    @staticmethod
    def get_room(db: Session, room_id: int) -> Optional[Room]:
        return db.query(Room).filter(Room.id == room_id).first()

    @staticmethod
    def get_rooms(db: Session, skip: int = 0, limit: int = 100) -> List[Room]:
        return db.query(Room).offset(skip).limit(limit).all()

    @staticmethod
    def update_room(db: Session, room_id: int, room_update: dict) -> Optional[Room]:
        room = db.query(Room).filter(Room.id == room_id).first()
        if room:
            for key, value in room_update.dict(exclude_unset=True).items():
                setattr(room, key, value)
            db.commit()
            db.refresh(room)
        return room

    @staticmethod
    def is_room_available(db: Session, room_id: int, start_date: date, end_date: date) -> bool:
        bookings = db.query(Booking).filter(
            Booking.room_id == room_id,
            Booking.start_date <= end_date,
            Booking.end_date >= start_date
        ).count()
        return bookings == 0

    @staticmethod
    def get_room_bookings(db: Session, room_id: int, start_date: Optional[date] = None,
                          end_date: Optional[date] = None) -> List[Booking]:
        query = db.query(Booking).filter(Booking.room_id == room_id)

        if start_date:
            query = query.filter(Booking.end_date >= start_date)

        if end_date:
            query = query.filter(Booking.start_date <= end_date)

        return query.order_by(Booking.start_date).all()