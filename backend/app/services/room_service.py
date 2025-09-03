from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from ..models.room import Room
from ..models.booking import Booking


class RoomService:
    @staticmethod
    def initialize_rooms(db: Session):
        """Initialize rooms with default data if empty"""
        if db.query(Room).count() > 0:
            return

        # Используем строковые значения вместо enum
        rooms_data = [
            # 2 o'rinli standart
            {"room_number": "101", "room_type": "2 o'rinli standart", "capacity": 2, "price_per_night": 500000},
            {"room_number": "102", "room_type": "2 o'rinli standart", "capacity": 2, "price_per_night": 500000},
            {"room_number": "103", "room_type": "2 o'rinli standart", "capacity": 2, "price_per_night": 500000},
            {"room_number": "104", "room_type": "2 o'rinli standart", "capacity": 2, "price_per_night": 500000},
            {"room_number": "105", "room_type": "2 o'rinli standart", "capacity": 2, "price_per_night": 500000},
            {"room_number": "106", "room_type": "2 o'rinli standart", "capacity": 2, "price_per_night": 500000},
            {"room_number": "107", "room_type": "2 o'rinli standart", "capacity": 2, "price_per_night": 500000},
            {"room_number": "108", "room_type": "2 o'rinli standart", "capacity": 2, "price_per_night": 500000},
            {"room_number": "109", "room_type": "2 o'rinli standart", "capacity": 2, "price_per_night": 500000},
            {"room_number": "110", "room_type": "2 o'rinli standart", "capacity": 2, "price_per_night": 500000},

            # 4 o'rinli standart
            {"room_number": "201", "room_type": "4 o'rinli standart", "capacity": 4, "price_per_night": 700000},
            {"room_number": "202", "room_type": "4 o'rinli standart", "capacity": 4, "price_per_night": 700000},
            {"room_number": "203", "room_type": "4 o'rinli standart", "capacity": 4, "price_per_night": 700000},
            {"room_number": "204", "room_type": "4 o'rinli standart", "capacity": 4, "price_per_night": 700000},
            {"room_number": "205", "room_type": "4 o'rinli standart", "capacity": 4, "price_per_night": 700000},
            {"room_number": "206", "room_type": "4 o'rinli standart", "capacity": 4, "price_per_night": 700000},

            # 2 o'rinli lyuks
            {"room_number": "301", "room_type": "2 o'rinli lyuks", "capacity": 2, "price_per_night": 800000},
            {"room_number": "302", "room_type": "2 o'rinli lyuks", "capacity": 2, "price_per_night": 800000},
            {"room_number": "303", "room_type": "2 o'rinli lyuks", "capacity": 2, "price_per_night": 800000},
            {"room_number": "304", "room_type": "2 o'rinli lyuks", "capacity": 2, "price_per_night": 800000},
            {"room_number": "305", "room_type": "2 o'rinli lyuks", "capacity": 2, "price_per_night": 800000},

            # 4 o'rinli kichik VIP
            {"room_number": "401", "room_type": "4 o'rinli kichik VIP", "capacity": 4, "price_per_night": 1000000},
            {"room_number": "402", "room_type": "4 o'rinli kichik VIP", "capacity": 4, "price_per_night": 1000000},
            {"room_number": "403", "room_type": "4 o'rinli kichik VIP", "capacity": 4, "price_per_night": 1000000},
            {"room_number": "404", "room_type": "4 o'rinli kichik VIP", "capacity": 4, "price_per_night": 1000000},

            # 4 o'rinli katta VIP
            {"room_number": "501", "room_type": "4 o'rinli katta VIP", "capacity": 4, "price_per_night": 1200000},
            {"room_number": "502", "room_type": "4 o'rinli katta VIP", "capacity": 4, "price_per_night": 1200000},
            {"room_number": "503", "room_type": "4 o'rinli katta VIP", "capacity": 4, "price_per_night": 1200000},

            # 4 o'rinli apartament
            {"room_number": "601", "room_type": "4 o'rinli apartament", "capacity": 4, "price_per_night": 1500000},
            {"room_number": "602", "room_type": "4 o'rinli apartament", "capacity": 4, "price_per_night": 1500000},

            # Kottedj
            {"room_number": "701", "room_type": "Kottedj (6 kishi uchun)", "capacity": 6, "price_per_night": 2000000},

            # Prezident apartamenti
            {"room_number": "801", "room_type": "Prezident apartamenti (8 kishi uchun)", "capacity": 8, "price_per_night": 3000000},
        ]

        for room_data in rooms_data:
            room = Room(**room_data)
            db.add(room)

        db.commit()
        print(f"Initialized {len(rooms_data)} rooms")

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
            for key, value in room_update.items():
                if hasattr(room, key):
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