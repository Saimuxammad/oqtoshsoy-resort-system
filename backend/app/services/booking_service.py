from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from ..models.booking import Booking
from ..schemas.booking import BookingCreate, BookingUpdate


class BookingService:
    @staticmethod
    def create_booking(db: Session, booking: BookingCreate, user_id: int) -> Booking:
        db_booking = Booking(**booking.dict(), created_by=user_id)
        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)
        return db_booking

    @staticmethod
    def get_booking(db: Session, booking_id: int) -> Optional[Booking]:
        return db.query(Booking).filter(Booking.id == booking_id).first()

    @staticmethod
    def update_booking(db: Session, booking_id: int, booking_update: BookingUpdate) -> Optional[Booking]:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if booking:
            update_data = booking_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(booking, field, value)
            db.commit()
            db.refresh(booking)
        return booking

    @staticmethod
    def delete_booking(db: Session, booking_id: int) -> bool:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if booking:
            db.delete(booking)
            db.commit()
            return True
        return False

    @staticmethod
    def check_availability(
            db: Session,
            room_id: int,
            start_date: date,
            end_date: date,
            exclude_booking_id: Optional[int] = None
    ) -> bool:
        query = db.query(Booking).filter(
            Booking.room_id == room_id,
            Booking.start_date <= end_date,
            Booking.end_date >= start_date
        )

        if exclude_booking_id:
            query = query.filter(Booking.id != exclude_booking_id)

        return query.count() == 0