from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta, date
from typing import Dict, List, Any
from ..models.room import Room  # Убираем импорт RoomType
from ..models.booking import Booking
from ..models.user import User


class AnalyticsService:
    @staticmethod
    def get_dashboard_stats(db: Session) -> Dict[str, Any]:
        """Get general dashboard statistics"""
        today = date.today()

        # Total rooms
        total_rooms = db.query(Room).count()

        # Occupied rooms today
        occupied_rooms = db.query(Booking).filter(
            Booking.start_date <= today,
            Booking.end_date >= today
        ).count()

        # Occupancy rate
        occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0

        # Total bookings this month
        current_month_start = date(today.year, today.month, 1)
        monthly_bookings = db.query(Booking).filter(
            Booking.created_at >= current_month_start
        ).count()

        # Revenue this month (примерный расчет)
        monthly_revenue = db.query(
            func.sum(
                func.coalesce(Room.price_per_night, 0) *
                (func.julianday(Booking.end_date) - func.julianday(Booking.start_date))
            )
        ).join(Room).filter(
            Booking.created_at >= current_month_start
        ).scalar() or 0

        return {
            "total_rooms": total_rooms,
            "occupied_rooms": occupied_rooms,
            "occupancy_rate": round(occupancy_rate, 1),
            "monthly_bookings": monthly_bookings,
            "monthly_revenue": float(monthly_revenue),
            "available_rooms": total_rooms - occupied_rooms
        }

    @staticmethod
    def get_room_type_stats(db: Session) -> List[Dict[str, Any]]:
        """Get statistics by room type"""
        # Получаем статистику по типам комнат
        room_stats = db.query(
            Room.room_type,
            func.count(Room.id).label('total'),
            func.avg(Room.price_per_night).label('avg_price')
        ).group_by(Room.room_type).all()

        result = []
        for stat in room_stats:
            # Считаем занятость для каждого типа
            occupied = db.query(Booking).join(Room).filter(
                Room.room_type == stat.room_type,
                Booking.start_date <= date.today(),
                Booking.end_date >= date.today()
            ).count()

            result.append({
                "room_type": stat.room_type,
                "total_rooms": stat.total,
                "occupied": occupied,
                "available": stat.total - occupied,
                "avg_price": float(stat.avg_price) if stat.avg_price else 0,
                "occupancy_rate": round((occupied / stat.total * 100) if stat.total > 0 else 0, 1)
            })

        return result

    @staticmethod
    def get_booking_trends(db: Session, days: int = 30) -> Dict[str, Any]:
        """Get booking trends for the last N days"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        # Получаем бронирования за период
        bookings = db.query(
            func.date(Booking.created_at).label('date'),
            func.count(Booking.id).label('count')
        ).filter(
            Booking.created_at >= start_date
        ).group_by(
            func.date(Booking.created_at)
        ).all()

        # Формируем результат
        trend_data = {
            "labels": [],
            "data": []
        }

        for booking in bookings:
            trend_data["labels"].append(str(booking.date))
            trend_data["data"].append(booking.count)

        return trend_data

    @staticmethod
    def get_revenue_stats(db: Session, year: int = None) -> Dict[str, Any]:
        """Get revenue statistics by month"""
        if not year:
            year = datetime.now().year

        # Получаем помесячную выручку
        monthly_revenue = db.query(
            extract('month', Booking.created_at).label('month'),
            func.sum(
                Room.price_per_night *
                (func.julianday(Booking.end_date) - func.julianday(Booking.start_date))
            ).label('revenue')
        ).join(Room).filter(
            extract('year', Booking.created_at) == year
        ).group_by(
            extract('month', Booking.created_at)
        ).all()

        # Формируем результат
        months = ['Yanvar', 'Fevral', 'Mart', 'Aprel', 'May', 'Iyun',
                  'Iyul', 'Avgust', 'Sentabr', 'Oktabr', 'Noyabr', 'Dekabr']

        revenue_data = {
            "labels": months,
            "data": [0] * 12
        }

        for item in monthly_revenue:
            month_idx = int(item.month) - 1
            revenue_data["data"][month_idx] = float(item.revenue) if item.revenue else 0

        return revenue_data

    @staticmethod
    def get_top_rooms(db: Session, limit: int = 5) -> List[Dict[str, Any]]:
        """Get most booked rooms"""
        top_rooms = db.query(
            Room.room_number,
            Room.room_type,
            func.count(Booking.id).label('booking_count')
        ).join(Booking).group_by(
            Room.id, Room.room_number, Room.room_type
        ).order_by(
            func.count(Booking.id).desc()
        ).limit(limit).all()

        result = []
        for room in top_rooms:
            result.append({
                "room_number": room.room_number,
                "room_type": room.room_type,
                "booking_count": room.booking_count
            })

        return result

    @staticmethod
    def get_occupancy_forecast(db: Session, days: int = 7) -> List[Dict[str, Any]]:
        """Get occupancy forecast for next N days"""
        forecast = []
        total_rooms = db.query(Room).count()

        for i in range(days):
            target_date = date.today() + timedelta(days=i)

            # Считаем занятые комнаты на эту дату
            occupied = db.query(Booking).filter(
                Booking.start_date <= target_date,
                Booking.end_date >= target_date
            ).count()

            forecast.append({
                "date": str(target_date),
                "occupied": occupied,
                "available": total_rooms - occupied,
                "occupancy_rate": round((occupied / total_rooms * 100) if total_rooms > 0 else 0, 1)
            })

        return forecast