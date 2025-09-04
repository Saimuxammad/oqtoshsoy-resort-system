from fastapi import FastAPI, HTTPException, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import uvicorn
from datetime import datetime, date
import logging
import os
from typing import Optional, List
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import io
import pandas as pd

from .database import engine, get_db

# ВАЖНО: Импортируем систему авторизации
from .api import auth
from .utils.dependencies import get_current_user
from .models.user import User

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
from .models import room, booking, user, history

room.Base.metadata.create_all(bind=engine)
booking.Base.metadata.create_all(bind=engine)
user.Base.metadata.create_all(bind=engine)
history.Base.metadata.create_all(bind=engine)


# Pydantic модели
class BookingCreate(BaseModel):
    room_id: int
    start_date: date
    end_date: date
    guest_name: Optional[str] = ""
    notes: Optional[str] = ""


class BookingUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    guest_name: Optional[str] = None
    notes: Optional[str] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Oqtoshsoy Resort Management API",
    version="2.0.0",
    description="Advanced hotel management system",
    lifespan=lifespan,
    redirect_slashes=False
)

# CORS настройка
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# КРИТИЧЕСКИ ВАЖНО: Регистрируем роутер авторизации
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

# Создаем роутеры для API
rooms_router = APIRouter(prefix="/api/rooms", tags=["rooms"])
bookings_router = APIRouter(prefix="/api/bookings", tags=["bookings"])


@rooms_router.get("")
@rooms_router.get("/")
async def get_rooms(
        room_type: Optional[str] = None,
        status: Optional[str] = None,
        db: Session = Depends(get_db),

):
    """Получить все комнаты с фильтрами"""
    try:
        from sqlalchemy import text

        logger.info(f"User {current_user.telegram_id} requesting rooms list")

        # Получаем все комнаты
        base_query = """
                     SELECT r.id,
                            r.room_number,
                            r.room_type,
                            COALESCE(r.capacity, 2)             as capacity,
                            COALESCE(r.price_per_night, 500000) as price_per_night,
                            COALESCE(r.description, '')         as description,
                            COALESCE(r.amenities, '')           as amenities,
                            r.created_at,
                            r.updated_at
                     FROM rooms r \
                     """

        conditions = []
        params = {}

        if room_type:
            conditions.append("r.room_type = :room_type")
            params['room_type'] = room_type

        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)

        base_query += " ORDER BY r.id"

        result = db.execute(text(base_query), params)
        all_rooms = result.fetchall()

        type_map = {
            'STANDARD_2': "2 o'rinli standart",
            'STANDARD_4': "4 o'rinli standart",
            'LUX_2': "2 o'rinli lyuks",
            'VIP_SMALL_4': "4 o'rinli kichik VIP",
            'VIP_BIG_4': "4 o'rinli katta VIP",
            'APARTMENT_4': "4 o'rinli apartament",
            'COTTAGE_6': "Kottedj (6 kishi uchun)",
            'PRESIDENT_8': "Prezident apartamenti (8 kishi uchun)"
        }

        # Получаем текущую дату
        today = date.today()
        logger.info(f"Checking room availability for date: {today}")

        # Получаем активные бронирования на сегодня
        current_bookings_query = """
                                 SELECT b.room_id, b.id as booking_id, b.guest_name, b.start_date, b.end_date
                                 FROM bookings b
                                 WHERE b.start_date <= :today \
                                   AND b.end_date > :today \
                                 """

        current_bookings_result = db.execute(text(current_bookings_query), {"today": today})

        # Создаем SET из room_id которые заняты
        occupied_room_ids = set()
        bookings_dict = {}

        for booking in current_bookings_result:
            room_id = booking.room_id
            occupied_room_ids.add(room_id)
            bookings_dict[room_id] = {
                "id": booking.booking_id,
                "guest_name": booking.guest_name,
                "start_date": str(booking.start_date),
                "end_date": str(booking.end_date)
            }

        logger.info(f"Total occupied rooms: {len(occupied_room_ids)}")

        # Формируем результат
        rooms = []
        for row in all_rooms:
            room_id = row.id
            room_type_display = type_map.get(row.room_type, row.room_type)

            # Проверяем доступность КОНКРЕТНОЙ комнаты по её ID
            is_available = room_id not in occupied_room_ids
            current_booking = bookings_dict.get(room_id, None)

            # Применяем фильтр по статусу если нужно
            if status:
                if status == "available" and not is_available:
                    continue
                elif status == "occupied" and is_available:
                    continue

            rooms.append({
                "id": room_id,
                "room_number": row.room_number,
                "room_type": room_type_display,
                "capacity": row.capacity,
                "price_per_night": float(row.price_per_night),
                "description": row.description,
                "amenities": row.amenities,
                "created_at": row.created_at.isoformat() if row.created_at else "2024-01-01T00:00:00",
                "updated_at": row.updated_at.isoformat() if row.updated_at else "2024-01-01T00:00:00",
                "is_available": is_available,
                "current_booking": current_booking
            })

        logger.info(f"Returning {len(rooms)} rooms to user {current_user.telegram_id}")
        return rooms

    except Exception as e:
        logger.error(f"Error in get_rooms: {e}")
        import traceback
        traceback.print_exc()
        return []


@rooms_router.get("/{room_id}")
async def get_room(
        room_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)  # Требуем авторизацию
):
    """Получить комнату по ID"""
    try:
        from sqlalchemy import text

        result = db.execute(text("""
                                 SELECT *
                                 FROM rooms
                                 WHERE id = :id
                                 """), {"id": room_id})

        room = result.fetchone()
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")

        type_map = {
            'STANDARD_2': "2 o'rinli standart",
            'STANDARD_4': "4 o'rinli standart",
            'LUX_2': "2 o'rinli lyuks",
            'VIP_SMALL_4': "4 o'rinli kichik VIP",
            'VIP_BIG_4': "4 o'rinli katta VIP",
            'APARTMENT_4': "4 o'rinli apartament",
            'COTTAGE_6': "Kottedj (6 kishi uchun)",
            'PRESIDENT_8': "Prezident apartamenti (8 kishi uchun)"
        }

        # Проверяем текущую занятость
        today = date.today()
        booking_check = db.execute(text("""
                                        SELECT COUNT(*)
                                        FROM bookings
                                        WHERE room_id = :room_id
                                          AND start_date <= :today
                                          AND end_date > :today
                                        """), {"room_id": room_id, "today": today})

        is_available = booking_check.scalar() == 0

        return {
            "id": room.id,
            "room_number": room.room_number,
            "room_type": type_map.get(room.room_type, room.room_type),
            "capacity": room.capacity or 2,
            "price_per_night": float(room.price_per_night) if room.price_per_night else 500000,
            "description": room.description or "",
            "amenities": room.amenities or "",
            "is_available": is_available
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_room: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@bookings_router.get("")
@bookings_router.get("/")
async def get_bookings(
        room_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        db: Session = Depends(get_db),

):
    """Получить все бронирования с возможностью фильтрации"""
    try:
        from sqlalchemy import text

        logger.info(f"User {current_user.telegram_id} requesting bookings")

        # Базовый запрос
        query = """
                SELECT b.id,
                       b.room_id,
                       b.start_date,
                       b.end_date,
                       b.guest_name,
                       b.notes,
                       b.created_by,
                       b.created_at,
                       b.updated_at,
                       r.room_number,
                       r.room_type
                FROM bookings b
                         LEFT JOIN rooms r ON b.room_id = r.id \
                """

        # Добавляем условия фильтрации
        conditions = []
        params = {}

        # Фильтрация по room_id
        if room_id:
            conditions.append("b.room_id = :room_id")
            params['room_id'] = room_id

        # Фильтрация по датам
        if start_date:
            conditions.append("b.end_date >= :start_date")
            params['start_date'] = start_date

        if end_date:
            conditions.append("b.start_date <= :end_date")
            params['end_date'] = end_date

        # Добавляем WHERE если есть условия
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY b.start_date DESC"

        # Выполняем запрос
        result = db.execute(text(query), params)

        type_map = {
            'STANDARD_2': "2 o'rinli standart",
            'STANDARD_4': "4 o'rinli standart",
            'LUX_2': "2 o'rinli lyuks",
            'VIP_SMALL_4': "4 o'rinli kichik VIP",
            'VIP_BIG_4': "4 o'rinli katta VIP",
            'APARTMENT_4': "4 o'rinli apartament",
            'COTTAGE_6': "Kottedj (6 kishi uchun)",
            'PRESIDENT_8': "Prezident apartamenti (8 kishi uchun)"
        }

        bookings = []
        for row in result:
            bookings.append({
                "id": row.id,
                "room_id": row.room_id,
                "start_date": str(row.start_date) if row.start_date else None,
                "end_date": str(row.end_date) if row.end_date else None,
                "guest_name": row.guest_name or "",
                "notes": row.notes or "",
                "created_by": row.created_by or 1,
                "created_at": row.created_at.isoformat() if row.created_at else "2024-01-01T00:00:00",
                "updated_at": row.updated_at.isoformat() if row.updated_at else "2024-01-01T00:00:00",
                "room": {
                    "id": row.room_id,
                    "room_number": row.room_number,
                    "room_type": type_map.get(row.room_type, row.room_type)
                } if row.room_number else None
            })

        logger.info(f"Returning {len(bookings)} bookings")
        return bookings

    except Exception as e:
        logger.error(f"Error in get_bookings: {e}")
        return []


@bookings_router.post("/v2")
@bookings_router.post("")
@bookings_router.post("/")
async def create_booking(
        booking_data: BookingCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)  # ОБЯЗАТЕЛЬНО: Требуем авторизацию
):
    """Создать новое бронирование"""
    try:
        from sqlalchemy import text

        logger.info(f"User {current_user.telegram_id} ({current_user.first_name} {current_user.last_name}) "
                    f"creating booking for room {booking_data.room_id} "
                    f"from {booking_data.start_date} to {booking_data.end_date}")

        # Проверяем существование комнаты
        room_check = db.execute(text("""
                                     SELECT id, room_number
                                     FROM rooms
                                     WHERE id = :room_id
                                     """), {"room_id": booking_data.room_id})

        room = room_check.fetchone()
        if not room:
            raise HTTPException(status_code=404, detail=f"Room with ID {booking_data.room_id} not found")

        # Проверяем конфликты ТОЛЬКО для ЭТОЙ комнаты
        conflicts = db.execute(text("""
                                    SELECT id, start_date, end_date, guest_name
                                    FROM bookings
                                    WHERE room_id = :room_id
                                      AND start_date < :end_date
                                      AND end_date > :start_date
                                    """), {
                                   "room_id": booking_data.room_id,
                                   "start_date": booking_data.start_date,
                                   "end_date": booking_data.end_date
                               })

        conflict_list = conflicts.fetchall()
        if conflict_list:
            conflict_details = []
            for c in conflict_list:
                conflict_details.append(f"{c.start_date} - {c.end_date} (Guest: {c.guest_name or 'N/A'})")

            error_message = f"Room #{room.room_number} is not available. Conflicts: {'; '.join(conflict_details)}"
            logger.warning(error_message)
            raise HTTPException(status_code=400, detail=error_message)

        # Создаем бронирование с ID текущего пользователя
        result = db.execute(text("""
                                 INSERT INTO bookings (room_id, start_date, end_date, guest_name, notes, created_by,
                                                       created_at, updated_at)
                                 VALUES (:room_id, :start_date, :end_date, :guest_name, :notes, :created_by, NOW(),
                                         NOW()) RETURNING id
                                 """), {
                                "room_id": booking_data.room_id,
                                "start_date": booking_data.start_date,
                                "end_date": booking_data.end_date,
                                "guest_name": booking_data.guest_name,
                                "notes": booking_data.notes,
                                "created_by": current_user.id  # Используем ID авторизованного пользователя
                            })

        booking_id = result.scalar()
        db.commit()

        logger.info(
            f"User {current_user.telegram_id} successfully created booking #{booking_id} for room #{room.room_number}")

        # Возвращаем созданное бронирование
        booking = db.execute(text("""
                                  SELECT b.*, r.room_number, r.room_type
                                  FROM bookings b
                                           LEFT JOIN rooms r ON b.room_id = r.id
                                  WHERE b.id = :id
                                  """), {"id": booking_id}).fetchone()

        type_map = {
            'STANDARD_2': "2 o'rinli standart",
            'STANDARD_4': "4 o'rinli standart",
            'LUX_2': "2 o'rinli lyuks",
            'VIP_SMALL_4': "4 o'rinli kichik VIP",
            'VIP_BIG_4': "4 o'rinli katta VIP",
            'APARTMENT_4': "4 o'rinli apartament",
            'COTTAGE_6': "Kottedj (6 kishi uchun)",
            'PRESIDENT_8': "Prezident apartamenti (8 kishi uchun)"
        }

        return {
            "id": booking.id,
            "room_id": booking.room_id,
            "start_date": str(booking.start_date),
            "end_date": str(booking.end_date),
            "guest_name": booking.guest_name,
            "notes": booking.notes,
            "created_by": booking.created_by,
            "created_at": booking.created_at.isoformat() if booking.created_at else None,
            "updated_at": booking.updated_at.isoformat() if booking.updated_at else None,
            "room": {
                "id": booking.room_id,
                "room_number": booking.room_number,
                "room_type": type_map.get(booking.room_type, booking.room_type)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@bookings_router.delete("/{booking_id}")
async def delete_booking(
        booking_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)  # ОБЯЗАТЕЛЬНО: Требуем авторизацию
):
    """Удалить бронирование"""
    try:
        from sqlalchemy import text

        logger.info(f"User {current_user.telegram_id} attempting to delete booking #{booking_id}")

        # Проверяем существование и получаем информацию о создателе
        check = db.execute(text("""
                                SELECT id, room_id, created_by
                                FROM bookings
                                WHERE id = :id
                                """), {"id": booking_id})

        booking = check.fetchone()
        if not booking:
            logger.warning(f"Booking {booking_id} not found")
            raise HTTPException(status_code=404, detail="Booking not found")

        # Проверяем права: админы могут удалять любые, остальные - только свои
        if not current_user.is_admin and booking.created_by != current_user.id:
            logger.warning(f"User {current_user.telegram_id} tried to delete booking #{booking_id} "
                           f"created by user {booking.created_by}")
            raise HTTPException(status_code=403,
                                detail="Siz faqat o'zingiz yaratgan bronlarni o'chira olasiz")

        db.execute(text("DELETE FROM bookings WHERE id = :id"), {"id": booking_id})
        db.commit()

        logger.info(f"User {current_user.telegram_id} successfully deleted booking #{booking_id}")
        return {"message": "Booking deleted successfully", "id": booking_id}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting booking {booking_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 4. Добавьте этот эндпоинт для проверки авторизации:
@app.get("/api/auth/check")
async def check_auth():
    """Проверка доступности API без авторизации"""
    return {"status": "ok", "auth_required": False}

# 5. Измените auth placeholder на рабочий:
@app.get("/api/auth/login")
async def auth_placeholder():
    """Временный токен для разработки"""
    return {
        "token": "dev_token_123",
        "user": {
            "id": 1,
            "name": "Test User",
            "telegram_id": 123456789,
            "is_admin": False
        }
    }
@bookings_router.put("/{booking_id}")
@bookings_router.patch("/{booking_id}")
async def update_booking(
        booking_id: int,
        booking_data: BookingUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)  # Требуем авторизацию
):
    """Обновить бронирование"""
    try:
        from sqlalchemy import text

        # Проверяем существование и права
        check = db.execute(text("""
                                SELECT *
                                FROM bookings
                                WHERE id = :id
                                """), {"id": booking_id})

        existing = check.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Booking not found")

        # Проверяем права: админы могут редактировать любые, остальные - только свои
        if not current_user.is_admin and existing.created_by != current_user.id:
            raise HTTPException(status_code=403,
                                detail="Siz faqat o'zingiz yaratgan bronlarni tahrirlashingiz mumkin")

        # Если обновляются даты, проверяем конфликты
        check_start = booking_data.start_date if booking_data.start_date else existing.start_date
        check_end = booking_data.end_date if booking_data.end_date else existing.end_date

        if booking_data.start_date or booking_data.end_date:
            conflicts = db.execute(text("""
                                        SELECT COUNT(*)
                                        FROM bookings
                                        WHERE room_id = :room_id
                                          AND id != :booking_id
                  AND start_date < :end_date
                  AND end_date > :start_date
                                        """), {
                                       "room_id": existing.room_id,
                                       "booking_id": booking_id,
                                       "start_date": check_start,
                                       "end_date": check_end
                                   })

            if conflicts.scalar() > 0:
                raise HTTPException(status_code=400, detail="Room is not available for selected dates")

        updates = []
        params = {"id": booking_id}

        if booking_data.start_date is not None:
            updates.append("start_date = :start_date")
            params["start_date"] = booking_data.start_date

        if booking_data.end_date is not None:
            updates.append("end_date = :end_date")
            params["end_date"] = booking_data.end_date

        if booking_data.guest_name is not None:
            updates.append("guest_name = :guest_name")
            params["guest_name"] = booking_data.guest_name

        if booking_data.notes is not None:
            updates.append("notes = :notes")
            params["notes"] = booking_data.notes

        if updates:
            updates.append("updated_at = NOW()")
            query = f"UPDATE bookings SET {', '.join(updates)} WHERE id = :id"
            db.execute(text(query), params)
            db.commit()

        logger.info(f"User {current_user.telegram_id} updated booking #{booking_id}")

        booking = db.execute(text("""
                                  SELECT b.*, r.room_number, r.room_type
                                  FROM bookings b
                                           LEFT JOIN rooms r ON b.room_id = r.id
                                  WHERE b.id = :id
                                  """), {"id": booking_id}).fetchone()

        type_map = {
            'STANDARD_2': "2 o'rinli standart",
            'STANDARD_4': "4 o'rinli standart",
            'LUX_2': "2 o'rinli lyuks",
            'VIP_SMALL_4': "4 o'rinli kichik VIP",
            'VIP_BIG_4': "4 o'rinli katta VIP",
            'APARTMENT_4': "4 o'rinli apartament",
            'COTTAGE_6': "Kottedj (6 kishi uchun)",
            'PRESIDENT_8': "Prezident apartamenti (8 kishi uchun)"
        }

        return {
            "id": booking.id,
            "room_id": booking.room_id,
            "start_date": str(booking.start_date),
            "end_date": str(booking.end_date),
            "guest_name": booking.guest_name,
            "notes": booking.notes,
            "created_by": booking.created_by,
            "created_at": booking.created_at.isoformat() if booking.created_at else None,
            "updated_at": booking.updated_at.isoformat() if booking.updated_at else None,
            "room": {
                "id": booking.room_id,
                "room_number": booking.room_number,
                "room_type": type_map.get(booking.room_type, booking.room_type)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Эндпоинты экспорта в Excel
@app.get("/api/export/bookings")
async def export_bookings_to_excel(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)  # Требуем авторизацию
):
    """Экспорт всех бронирований в Excel файл"""
    try:
        from sqlalchemy import text

        # Базовый запрос
        query = """
                SELECT b.id          as "Bron ID", \
                       r.room_number as "Xona raqami", \
                       r.room_type   as "Xona turi", \
                       b.guest_name  as "Mehmon ismi", \
                       b.start_date  as "Kirish sanasi", \
                       b.end_date    as "Chiqish sanasi", \
                       b.notes       as "Izohlar", \
                       b.created_at  as "Yaratilgan vaqt", \
                       CASE \
                           WHEN b.start_date <= CURRENT_DATE AND b.end_date > CURRENT_DATE \
                               THEN 'Band' \
                           WHEN b.end_date < CURRENT_DATE \
                               THEN 'Tugagan' \
                           ELSE 'Kutilmoqda' \
                           END       as "Status"
                FROM bookings b
                         LEFT JOIN rooms r ON b.room_id = r.id \
                """

        conditions = []
        params = {}

        if start_date:
            conditions.append("b.start_date >= :start_date")
            params['start_date'] = start_date

        if end_date:
            conditions.append("b.end_date <= :end_date")
            params['end_date'] = end_date

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY b.created_at DESC"

        result = db.execute(text(query), params)
        df = pd.DataFrame(result.fetchall())

        if df.empty:
            df = pd.DataFrame(columns=[
                "Bron ID", "Xona raqami", "Xona turi", "Mehmon ismi",
                "Kirish sanasi", "Chiqish sanasi", "Izohlar",
                "Yaratilgan vaqt", "Status"
            ])

        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Bronlar', index=False)

            workbook = writer.book
            worksheet = writer.sheets['Bronlar']

            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#4472C4',
                'font_color': 'white',
                'border': 1
            })

            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)

            worksheet.set_column('A:A', 10)
            worksheet.set_column('B:B', 15)
            worksheet.set_column('C:C', 25)
            worksheet.set_column('D:D', 30)
            worksheet.set_column('E:F', 15)
            worksheet.set_column('G:G', 40)
            worksheet.set_column('H:H', 20)
            worksheet.set_column('I:I', 15)

        output.seek(0)
        filename = f"bronlar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        return StreamingResponse(
            io.BytesIO(output.getvalue()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        logger.error(f"Error exporting bookings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/export/rooms")
async def export_rooms_to_excel(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)  # Требуем авторизацию
):
    """Экспорт информации о комнатах в Excel файл"""
    try:
        from sqlalchemy import text

        today = date.today()

        query = """
                SELECT r.id              as "ID", \
                       r.room_number     as "Xona raqami", \
                       r.room_type       as "Xona turi", \
                       r.capacity        as "Sig'im", \
                       r.price_per_night as "Kunlik narx", \
                       CASE \
                           WHEN EXISTS (SELECT 1 \
                                        FROM bookings b \
                                        WHERE b.room_id = r.id \
                                          AND b.start_date <= :today \
                                          AND b.end_date > :today) THEN 'Band' \
                           ELSE 'Bo''sh' \
                           END           as "Holati", \
                       r.description     as "Tavsif", \
                       r.amenities       as "Qulayliklar"
                FROM rooms r
                ORDER BY r.id \
                """

        result = db.execute(text(query), {"today": today})
        df = pd.DataFrame(result.fetchall())

        if df.empty:
            df = pd.DataFrame(columns=[
                "ID", "Xona raqami", "Xona turi", "Sig'im",
                "Kunlik narx", "Holati", "Tavsif", "Qulayliklar"
            ])

        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Xonalar', index=False)

            workbook = writer.book
            worksheet = writer.sheets['Xonalar']

            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#4472C4',
                'font_color': 'white',
                'border': 1
            })

            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)

            worksheet.set_column('A:A', 8)
            worksheet.set_column('B:B', 15)
            worksheet.set_column('C:C', 25)
            worksheet.set_column('D:D', 10)
            worksheet.set_column('E:E', 15)
            worksheet.set_column('F:F', 10)
            worksheet.set_column('G:H', 30)

        output.seek(0)
        filename = f"xonalar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        return StreamingResponse(
            io.BytesIO(output.getvalue()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        logger.error(f"Error exporting rooms: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Регистрируем роутеры
app.include_router(rooms_router)
app.include_router(bookings_router)


# Дополнительные эндпоинты
@app.get("/api/analytics")
async def analytics_placeholder(current_user: User = Depends(get_current_user)):
    return {"message": "Analytics module is under development"}


@app.get("/api/history")
async def history_placeholder(current_user: User = Depends(get_current_user)):
    return {"message": "History module is under development"}


@app.get("/")
async def root():
    return {
        "message": "Oqtoshsoy Resort Management System API",
        "version": "2.0.0",
        "status": "active"
    }


@app.get("/api")
async def api_root():
    return {"message": "API is running", "version": "2.0.0"}


# Отладочные эндпоинты (только для админов)
@app.get("/api/debug/room-status")
async def debug_room_status(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Отладочный эндпоинт для проверки статуса комнат"""

    # Только админы могут использовать отладочные эндпоинты
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        from sqlalchemy import text

        rooms = db.execute(text("SELECT id, room_number, room_type FROM rooms ORDER BY id")).fetchall()

        today = date.today()
        active_bookings = db.execute(text("""
                                          SELECT room_id, id as booking_id, guest_name, start_date, end_date
                                          FROM bookings
                                          WHERE start_date <= :today
                                            AND end_date > :today
                                          """), {"today": today}).fetchall()

        occupied = {}
        for booking in active_bookings:
            occupied[booking.room_id] = {
                "booking_id": booking.booking_id,
                "guest": booking.guest_name,
                "dates": f"{booking.start_date} to {booking.end_date}"
            }

        result = []
        for room in rooms:
            result.append({
                "room_id": room.id,
                "room_number": room.room_number,
                "room_type": room.room_type,
                "is_available": room.id not in occupied,
                "booking": occupied.get(room.id)
            })

        return {
            "date": str(today),
            "total_rooms": len(rooms),
            "occupied_rooms": len(occupied),
            "available_rooms": len(rooms) - len(occupied),
            "rooms": result
        }

    except Exception as e:
        logger.error(f"Error in debug_room_status: {e}")
        return {"error": str(e)}


@app.get("/api/debug/access-check")
async def debug_access_check(telegram_id: Optional[int] = None):
    """Проверка настроек контроля доступа (публичный эндпоинт для тестирования)"""
    from backend.config.admins import (
        SUPER_ADMINS, ADMINS, MANAGERS, OPERATORS,
        ALLOWED_USERS, is_allowed_user
    )

    environment = os.getenv("ENVIRONMENT", "not_set")
    access_control = os.getenv("ACCESS_CONTROL", "not_set")

    result = {
        "environment_variables": {
            "ENVIRONMENT": environment,
            "ACCESS_CONTROL": access_control
        },
        "allowed_users": {
            "SUPER_ADMINS": SUPER_ADMINS,
            "ADMINS": ADMINS,
            "MANAGERS": MANAGERS,
            "OPERATORS": OPERATORS,
            "TOTAL_ALLOWED": ALLOWED_USERS
        },
        "total_allowed_count": len(ALLOWED_USERS)
    }

    if telegram_id:
        is_allowed = is_allowed_user(telegram_id)
        result["test_user"] = {
            "telegram_id": telegram_id,
            "is_allowed": is_allowed,
            "reason": "User in ALLOWED_USERS list" if is_allowed else "User NOT in ALLOWED_USERS list"
        }

    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)