from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from ..models.room import Room, RoomType
from ..models.booking import Booking
from ..schemas.room import RoomCreate, RoomUpdate


class RoomService:
    @staticmethod
    def create_room(db: Session, room: RoomCreate) -> Room:
        db_room = Room(**room.dict())
        db.add(db_room)
        db.commit()
        db.refresh(db_room)
        return db_room

    @staticmethod
    def get_rooms(db: Session, skip: int = 0, limit: int = 100) -> List[Room]:
        return db.query(Room).offset(skip).limit(limit).all()

    @staticmethod
    def get_room(db: Session, room_id: int) -> Optional[Room]:
        return db.query(Room).filter(Room.id == room_id).first()

    @staticmethod
    def get_room_by_number(db: Session, room_number: str) -> Optional[Room]:
        return db.query(Room).filter(Room.room_number == room_number).first()

    @staticmethod
    def update_room(db: Session, room_id: int, room_update: RoomUpdate) -> Optional[Room]:
        room = db.query(Room).filter(Room.id == room_id).first()
        if room:
            update_data = room_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(room, field, value)
            db.commit()
            db.refresh(room)
        return room

    @staticmethod
    def get_room_availability(db: Session, room_id: int, check_date: date) -> bool:
        bookings = db.query(Booking).filter(
            Booking.room_id == room_id,
            Booking.start_date <= check_date,
            Booking.end_date >= check_date
        ).count()
        return bookings == 0

    @staticmethod
    def initialize_rooms(db: Session):
        """Initialize all rooms in the database"""
        rooms_data = [
            # 2 o'rinli standart
            {"room_number": "21", "room_type": RoomType.STANDARD_2},
            {"room_number": "22", "room_type": RoomType.STANDARD_2},
            {"room_number": "23", "room_type": RoomType.STANDARD_2},
            {"room_number": "24", "room_type": RoomType.STANDARD_2},
            {"room_number": "25", "room_type": RoomType.STANDARD_2},
            {"room_number": "26", "room_type": RoomType.STANDARD_2},
            {"room_number": "27", "room_type": RoomType.STANDARD_2},
            {"room_number": "28", "room_type": RoomType.STANDARD_2},

            # 4 o'rinli standart
            {"room_number": "29", "room_type": RoomType.STANDARD_4},

            # 2 o'rinli lyuks
            {"room_number": "101", "room_type": RoomType.LUX_2},
            {"room_number": "202", "room_type": RoomType.LUX_2},
            {"room_number": "302", "room_type": RoomType.LUX_2},
            {"room_number": "401", "room_type": RoomType.LUX_2},
            {"room_number": "402", "room_type": RoomType.LUX_2},
            {"room_number": "503", "room_type": RoomType.LUX_2},
            {"room_number": "703", "room_type": RoomType.LUX_2},
            {"room_number": "704", "room_type": RoomType.LUX_2},
            {"room_number": "705", "room_type": RoomType.LUX_2},
            {"room_number": "706", "room_type": RoomType.LUX_2},

            # 4 o'rinli kichik VIP
            {"room_number": "502", "room_type": RoomType.VIP_SMALL_4},
            {"room_number": "702", "room_type": RoomType.VIP_SMALL_4},

            # 4 o'rinli katta VIP
            {"room_number": "102", "room_type": RoomType.VIP_BIG_4},
            {"room_number": "103", "room_type": RoomType.VIP_BIG_4},
            {"room_number": "701", "room_type": RoomType.VIP_BIG_4},

            # 4 o'rinli apartament
            {"room_number": "201", "room_type": RoomType.APARTMENT_4},
            {"room_number": "301", "room_type": RoomType.APARTMENT_4},
            {"room_number": "504", "room_type": RoomType.APARTMENT_4},  # Изменил с 503 на 504
            {"room_number": "601", "room_type": RoomType.APARTMENT_4},
            {"room_number": "602", "room_type": RoomType.APARTMENT_4},

            # Kottedj
            {"room_number": "Kottedj", "room_type": RoomType.COTTAGE_6},

            # Prezident apartamenti
            {"room_number": "707", "room_type": RoomType.PRESIDENT_8},
        ]

        for room_data in rooms_data:
            existing = db.query(Room).filter(Room.room_number == room_data["room_number"]).first()
            if not existing:
                new_room = Room(**room_data)
                db.add(new_room)

        db.commit()