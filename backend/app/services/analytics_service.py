from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional
from ..models.room import Room, RoomType
from ..models.booking import Booking
from ..models.user import User


class AnalyticsService:
    @staticmethod
    def get_occupancy_stats(
            db: Session,
            start_date: Optional[date] = None,
            end_date: Optional[date] = None
    ) -> Dict:
        """Get occupancy statistics for a date range"""
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()

        total_rooms = db.query(Room).count()

        # Calculate daily occupancy
        date_range = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]
        daily_stats = []

        for check_date in date_range:
            occupied = db.query(Booking).filter(
                and_(
                    Booking.start_date <= check_date,
                    Booking.end_date >= check_date
                )
            ).count()

            daily_stats.append({
                "date": check_date.isoformat(),
                "occupied": occupied,
                "available": total_rooms - occupied,
                "occupancy_rate": (occupied / total_rooms * 100) if total_rooms > 0 else 0
            })

        # Calculate average occupancy
        avg_occupancy = sum(day["occupancy_rate"] for day in daily_stats) / len(daily_stats) if daily_stats else 0

        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_rooms": total_rooms,
            "average_occupancy": round(avg_occupancy, 2),
            "daily_stats": daily_stats
        }

    @staticmethod
    def get_room_type_stats(
            db: Session,
            start_date: Optional[date] = None,
            end_date: Optional[date] = None
    ) -> List[Dict]:
        """Get statistics by room type"""
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()

        stats = []

        for room_type in RoomType:
            rooms = db.query(Room).filter(Room.room_type == room_type).all()
            if not rooms:
                continue

            room_ids = [room.id for room in rooms]

            # Count bookings for this room type
            bookings_count = db.query(Booking).filter(
                and_(
                    Booking.room_id.in_(room_ids),
                    Booking.start_date <= end_date,
                    Booking.end_date >= start_date
                )
            ).count()

            # Calculate total booked days
            bookings = db.query(Booking).filter(
                and_(
                    Booking.room_id.in_(room_ids),
                    Booking.start_date <= end_date,
                    Booking.end_date >= start_date
                )
            ).all()

            total_days = 0
            for booking in bookings:
                booking_start = max(booking.start_date, start_date)
                booking_end = min(booking.end_date, end_date)
                total_days += (booking_end - booking_start).days + 1

            possible_days = len(rooms) * ((end_date - start_date).days + 1)
            occupancy_rate = (total_days / possible_days * 100) if possible_days > 0 else 0

            stats.append({
                "room_type": room_type.value,
                "total_rooms": len(rooms),
                "bookings_count": bookings_count,
                "total_booked_days": total_days,
                "occupancy_rate": round(occupancy_rate, 2)
            })

        return stats

    @staticmethod
    def get_booking_trends(db: Session, months: int = 6) -> List[Dict]:
        """Get booking trends by month"""
        end_date = date.today()
        start_date = end_date - timedelta(days=months * 30)

        # Use extract for cross-database compatibility
        bookings = db.query(
            extract('year', Booking.created_at).label('year'),
            extract('month', Booking.created_at).label('month'),
            func.count(Booking.id).label('count'),
            func.avg(
                extract('day', Booking.end_date) - extract('day', Booking.start_date) + 1
            ).label('avg_duration')
        ).filter(
            Booking.created_at >= start_date
        ).group_by(
            extract('year', Booking.created_at),
            extract('month', Booking.created_at)
        ).order_by(
            extract('year', Booking.created_at),
            extract('month', Booking.created_at)
        ).all()

        trends = []
        for booking in bookings:
            year = int(booking.year) if booking.year else datetime.now().year
            month = int(booking.month) if booking.month else 1
            trends.append({
                "month": f"{year}-{month:02d}",
                "bookings_count": booking.count,
                "average_duration": round(float(booking.avg_duration), 1) if booking.avg_duration else 0
            })

        return trends

    @staticmethod
    def get_user_activity_stats(db: Session) -> List[Dict]:
        """Get statistics about user activity"""
        users = db.query(
            User,
            func.count(Booking.id).label('bookings_count')
        ).outerjoin(
            Booking, User.id == Booking.created_by
        ).group_by(User.id).all()

        stats = []
        for user, bookings_count in users:
            last_booking = db.query(Booking).filter(
                Booking.created_by == user.id
            ).order_by(Booking.created_at.desc()).first()

            stats.append({
                "user_id": user.id,
                "name": f"{user.first_name} {user.last_name or ''}".strip(),
                "is_admin": user.is_admin,
                "bookings_count": bookings_count or 0,
                "last_activity": last_booking.created_at.isoformat() if last_booking else user.created_at.isoformat()
            })

        return sorted(stats, key=lambda x: x['bookings_count'], reverse=True)

    @staticmethod
    def get_revenue_forecast(
            db: Session,
            room_prices: Dict[str, float],
            days_ahead: int = 30
    ) -> Dict:
        """Get revenue forecast based on current bookings"""
        start_date = date.today()
        end_date = start_date + timedelta(days=days_ahead)

        bookings = db.query(Booking).join(Room).filter(
            and_(
                Booking.start_date <= end_date,
                Booking.end_date >= start_date
            )
        ).all()

        total_revenue = 0
        daily_revenue = {}

        for booking in bookings:
            room = booking.room
            price_per_night = room_prices.get(room.room_type.value, 0)

            booking_start = max(booking.start_date, start_date)
            booking_end = min(booking.end_date, end_date)
            nights = (booking_end - booking_start).days + 1

            booking_revenue = nights * price_per_night
            total_revenue += booking_revenue

            # Add to daily revenue
            current_date = booking_start
            while current_date <= booking_end:
                date_str = current_date.isoformat()
                daily_revenue[date_str] = daily_revenue.get(date_str, 0) + price_per_night
                current_date += timedelta(days=1)

        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_expected_revenue": total_revenue,
            "daily_revenue": [
                {"date": date_str, "revenue": revenue}
                for date_str, revenue in sorted(daily_revenue.items())
            ]
        }