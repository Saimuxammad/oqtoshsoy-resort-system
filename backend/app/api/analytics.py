from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime
from ..database import get_db
from ..services.analytics_service import AnalyticsService
from ..utils.dependencies import require_admin

router = APIRouter()


@router.get("/occupancy")
async def get_occupancy_stats(
        start_date: Optional[date] = Query(None),
        end_date: Optional[date] = Query(None),
        db: Session = Depends(get_db),
        current_user=Depends(require_admin)
):
    """Get occupancy statistics"""
    return AnalyticsService.get_occupancy_stats(db, start_date, end_date)


@router.get("/room-types")
async def get_room_type_stats(
        start_date: Optional[date] = Query(None),
        end_date: Optional[date] = Query(None),
        db: Session = Depends(get_db),
        current_user=Depends(require_admin)
):
    """Get statistics by room type"""
    return AnalyticsService.get_room_type_stats(db, start_date, end_date)


@router.get("/trends")
async def get_booking_trends(
        months: int = Query(6, ge=1, le=24),
        db: Session = Depends(get_db),
        current_user=Depends(require_admin)
):
    """Get booking trends"""
    return AnalyticsService.get_booking_trends(db, months)


@router.get("/users")
async def get_user_activity_stats(
        db: Session = Depends(get_db),
        current_user=Depends(require_admin)
):
    """Get user activity statistics"""
    return AnalyticsService.get_user_activity_stats(db)


@router.get("/revenue-forecast")
async def get_revenue_forecast(
        days_ahead: int = Query(30, ge=1, le=365),
        db: Session = Depends(get_db),
        current_user=Depends(require_admin)
):
    """Get revenue forecast"""
    # Default room prices (can be moved to config or database)
    room_prices = {
        "2 o'rinli standart": 500000,
        "4 o'rinli standart": 700000,
        "2 o'rinli lyuks": 800000,
        "4 o'rinli kichik VIP": 1000000,
        "4 o'rinli katta VIP": 1200000,
        "4 o'rinli apartament": 1500000,
        "Kottedj (6 kishi uchun)": 2000000,
        "Prezident apartamenti (8 kishi uchun)": 3000000
    }

    return AnalyticsService.get_revenue_forecast(db, room_prices, days_ahead)