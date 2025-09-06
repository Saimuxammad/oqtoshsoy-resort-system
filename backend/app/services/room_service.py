from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from ..models.room import Room
from ..models.booking import Booking


class RoomService:
    @staticmethod
    def get_rooms_with_status(
            db: Session,
            room_type_filter: Optional[str] = None,
            status_filter: Optional[str] = None
    ) -> List[dict]:
        """
        Получает список комнат с их текущим статусом бронирования и применяет фильтры.
        Это основной метод, который будет использовать API.
        """
        # Начинаем базовый запрос для всех комнат
        query = db.query(Room)

        # Применяем фильтр по типу комнаты, если он указан
        if room_type_filter:
            query = query.filter(Room.room_type == room_type_filter)

        all_rooms = query.order_by(Room.id).all()

        # Получаем ID всех комнат, которые заняты СЕГОДНЯ
        today = date.today()
        occupied_room_ids_query = db.query(Booking.room_id).filter(
            Booking.start_date <= today,
            Booking.end_date > today  # > чтобы не считать день выезда
        ).distinct()

        # Преобразуем в set для быстрой проверки (например, `if room_id in occupied_ids`)
        occupied_ids = {room_id for (room_id,) in occupied_room_ids_query}

        result_rooms = []
        for room in all_rooms:
            is_occupied = room.id in occupied_ids

            # Применяем фильтр по статусу, если он указан
            if status_filter:
                if status_filter == "available" and is_occupied:
                    continue  # Пропускаем занятые, если нужен "свободен"
                elif status_filter == "occupied" and not is_occupied:
                    continue  # Пропускаем свободные, если нужен "занят"

            # Добавляем в результат. Pydantic-схема сама преобразует это в нужный JSON.
            # Мы добавляем поле is_available "на лету".
            room.is_available = not is_occupied
            result_rooms.append(room)

        return result_rooms

    @staticmethod
    def get_room_with_status(db: Session, room_id: int) -> Optional[Room]:
        """
        Получает одну комнату по ID и добавляет её текущий статус.
        """
        room = db.query(Room).filter(Room.id == room_id).first()
        if not room:
            return None

        today = date.today()
        # Проверяем, занята ли конкретно эта комната
        is_occupied = db.query(Booking).filter(
            Booking.room_id == room_id,
            Booking.start_date <= today,
            Booking.end_date > today
        ).first() is not None

        room.is_available = not is_occupied
        return room

    # --- Остальные ваши методы остаются без изменений ---

    @staticmethod
    def initialize_rooms(db: Session):
        """Initialize rooms with default data if empty"""
        if db.query(Room).count() > 0:
            return

        rooms_data = [
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
            {"room_number": "201", "room_type": "4 o'rinli standart", "capacity": 4, "price_per_night": 700000},
            {"room_number": "202", "room_type": "4 o'rinli standart", "capacity": 4, "price_per_night": 700000},
            {"room_number": "203", "room_type": "4 o'rinli standart", "capacity": 4, "price_per_night": 700000},
            {"room_number": "204", "room_type": "4 o'rinli standart", "capacity": 4, "price_per_night": 700000},
            {"room_number": "205", "room_type": "4 o'rinli standart", "capacity": 4, "price_per_night": 700000},
            {"room_number": "206", "room_type": "4 o'rinli standart", "capacity": 4, "price_per_night": 700000},
            {"room_number": "301", "room_type": "2 o'rinli lyuks", "capacity": 2, "price_per_night": 800000},
            {"room_number": "302", "room_type": "2 o'rinli lyuks", "capacity": 2, "price_per_night": 800000},
            {"room_number": "303", "room_type": "2 o'rinli lyuks", "capacity": 2, "price_per_night": 800000},
            {"room_number": "304", "room_type": "2 o'rinli lyuks", "capacity": 2, "price_per_night": 800000},
            {"room_number": "305", "room_type": "2 o'rinli lyuks", "capacity": 2, "price_per_night": 800000},
            {"room_number": "401", "room_type": "4 o'rinli kichik VIP", "capacity": 4, "price_per_night": 1000000},
            {"room_number": "402", "room_type": "4 o'rinli kichik VIP", "capacity": 4, "price_per_night": 1000000},
            {"room_number": "403", "room_type": "4 o'rinli kichik VIP", "capacity": 4, "price_per_night": 1000000},
            {"room_number": "404", "room_type": "4 o'rinli kichik VIP", "capacity": 4, "price_per_night": 1000000},
            {"room_number": "501", "room_type": "4 o'rinli katta VIP", "capacity": 4, "price_per_night": 1200000},
            {"room_number": "502", "room_type": "4 o'rinli katta VIP", "capacity": 4, "price_per_night": 1200000},
            {"room_number": "503", "room_type": "4 o'rinli katta VIP", "capacity": 4, "price_per_night": 1200000},
            {"room_number": "601", "room_type": "4 o'rinli apartament", "capacity": 4, "price_per_night": 1500000},
            {"room_number": "602", "room_type": "4 o'rinli apartament", "capacity": 4, "price_per_night": 1500000},
            {"room_number": "701", "room_type": "Kottedj (6 kishi uchun)", "capacity": 6, "price_per_night": 2000000},
            {"room_number": "801", "room_type": "Prezident apartamenti (8 kishi uchun)", "capacity": 8,
             "price_per_night": 3000000},
        ]
        for room_data in rooms_data:
            db.add(Room(**room_data))
        db.commit()

    @staticmethod
    def get_room(db: Session, room_id: int) -> Optional[Room]:
        return db.query(Room).filter(Room.id == room_id).first()