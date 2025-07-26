from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import Optional
import io
from ..database import get_db
from ..services.export_service import ExportService
from ..utils.dependencies import get_current_user

router = APIRouter()


@router.get("/rooms")
async def export_rooms(
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Export all rooms to Excel"""
    excel_data = ExportService.export_rooms_to_excel(db)

    filename = f"xonalar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    return StreamingResponse(
        io.BytesIO(excel_data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/bookings")
async def export_bookings(
        start_date: Optional[date] = Query(None),
        end_date: Optional[date] = Query(None),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Export bookings to Excel"""
    excel_data = ExportService.export_bookings_to_excel(db, start_date, end_date)

    filename = f"bronlar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    return StreamingResponse(
        io.BytesIO(excel_data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/analytics")
async def export_analytics(
        start_date: date = Query(...),
        end_date: date = Query(...),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Export analytics report to Excel"""
    excel_data = ExportService.export_analytics_to_excel(db, start_date, end_date)

    filename = f"hisobot_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.xlsx"

    return StreamingResponse(
        io.BytesIO(excel_data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )