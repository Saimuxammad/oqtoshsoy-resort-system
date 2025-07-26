import io
from datetime import date, datetime
from typing import Optional, List, Dict
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from sqlalchemy.orm import Session
from ..models.room import Room
from ..models.booking import Booking
from ..models.user import User


class ExportService:
    @staticmethod
    def export_rooms_to_excel(db: Session) -> bytes:
        """Export all rooms to Excel file"""
        rooms = db.query(Room).all()

        # Create workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Xonalar"

        # Headers
        headers = ["№", "Xona raqami", "Xona turi", "Holati", "Yaratilgan sana"]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            cell.font = Font(color="FFFFFF", bold=True)
            cell.alignment = Alignment(horizontal="center")

        # Data
        for idx, room in enumerate(rooms, 2):
            ws.cell(row=idx, column=1, value=idx - 1)
            ws.cell(row=idx, column=2, value=f"№{room.room_number}")
            ws.cell(row=idx, column=3, value=room.room_type.value)
            ws.cell(row=idx, column=4, value="Bo'sh" if room.is_available else "Band")
            ws.cell(row=idx, column=5, value=room.created_at.strftime("%d.%m.%Y"))

            # Color coding for status
            status_cell = ws.cell(row=idx, column=4)
            if room.is_available:
                status_cell.fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
            else:
                status_cell.fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")

        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column_letter].width = adjusted_width

        # Save to bytes
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output.getvalue()

    @staticmethod
    def export_bookings_to_excel(
            db: Session,
            start_date: Optional[date] = None,
            end_date: Optional[date] = None
    ) -> bytes:
        """Export bookings to Excel file"""
        query = db.query(Booking).join(Room)

        if start_date:
            query = query.filter(Booking.start_date >= start_date)
        if end_date:
            query = query.filter(Booking.end_date <= end_date)

        bookings = query.order_by(Booking.start_date).all()

        # Create workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Bronlar"

        # Headers
        headers = [
            "№", "Xona", "Xona turi", "Kirish sanasi", "Chiqish sanasi",
            "Kunlar", "Mehmon", "Izohlar", "Yaratuvchi", "Yaratilgan sana"
        ]

        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            cell.font = Font(color="FFFFFF", bold=True)
            cell.alignment = Alignment(horizontal="center")

        # Data
        for idx, booking in enumerate(bookings, 2):
            nights = (booking.end_date - booking.start_date).days + 1
            creator = db.query(User).filter(User.id == booking.created_by).first()

            ws.cell(row=idx, column=1, value=idx - 1)
            ws.cell(row=idx, column=2, value=f"№{booking.room.room_number}")
            ws.cell(row=idx, column=3, value=booking.room.room_type.value)
            ws.cell(row=idx, column=4, value=booking.start_date.strftime("%d.%m.%Y"))
            ws.cell(row=idx, column=5, value=booking.end_date.strftime("%d.%m.%Y"))
            ws.cell(row=idx, column=6, value=nights)
            ws.cell(row=idx, column=7, value=booking.guest_name or "-")
            ws.cell(row=idx, column=8, value=booking.notes or "-")
            ws.cell(row=idx, column=9, value=f"{creator.first_name} {creator.last_name or ''}" if creator else "-")
            ws.cell(row=idx, column=10, value=booking.created_at.strftime("%d.%m.%Y %H:%M"))

        # Summary sheet
        ws2 = wb.create_sheet("Xulosa")

        # Summary headers
        ws2.cell(row=1, column=1, value="Umumiy ma'lumotlar")
        ws2.cell(row=1, column=1).font = Font(bold=True, size=14)

        ws2.cell(row=3, column=1, value="Jami bronlar:")
        ws2.cell(row=3, column=2, value=len(bookings))

        ws2.cell(row=4, column=1, value="Davr:")
        if start_date and end_date:
            ws2.cell(row=4, column=2, value=f"{start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}")
        else:
            ws2.cell(row=4, column=2, value="Barcha vaqt")

        # Room type summary
        ws2.cell(row=6, column=1, value="Xona turlari bo'yicha:")
        ws2.cell(row=6, column=1).font = Font(bold=True)

        room_type_counts = {}
        for booking in bookings:
            room_type = booking.room.room_type.value
            room_type_counts[room_type] = room_type_counts.get(room_type, 0) + 1

        row = 7
        for room_type, count in room_type_counts.items():
            ws2.cell(row=row, column=1, value=room_type)
            ws2.cell(row=row, column=2, value=count)
            row += 1

        # Auto-adjust column widths
        for ws in [wb.active, ws2]:
            for column in ws.columns:
                max_length = 0
                column_letter = get_column_letter(column[0].column)
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                ws.column_dimensions[column_letter].width = adjusted_width

        # Save to bytes
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output.getvalue()

    @staticmethod
    def export_analytics_to_excel(
            db: Session,
            start_date: date,
            end_date: date
    ) -> bytes:
        """Export analytics report to Excel"""
        from ..services.analytics_service import AnalyticsService

        wb = Workbook()

        # Occupancy sheet
        ws1 = wb.active
        ws1.title = "Bandlik statistikasi"

        occupancy_stats = AnalyticsService.get_occupancy_stats(db, start_date, end_date)

        # Headers
        ws1.cell(row=1, column=1, value="Bandlik statistikasi")
        ws1.cell(row=1, column=1).font = Font(bold=True, size=14)

        ws1.cell(row=3, column=1, value="Davr:")
        ws1.cell(row=3, column=2, value=f"{start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}")

        ws1.cell(row=4, column=1, value="O'rtacha bandlik:")
        ws1.cell(row=4, column=2, value=f"{occupancy_stats['average_occupancy']}%")

        # Daily stats
        ws1.cell(row=6, column=1, value="Sana")
        ws1.cell(row=6, column=2, value="Band")
        ws1.cell(row=6, column=3, value="Bo'sh")
        ws1.cell(row=6, column=4, value="Bandlik %")

        for idx, day_stat in enumerate(occupancy_stats['daily_stats'], 7):
            ws1.cell(row=idx, column=1, value=datetime.fromisoformat(day_stat['date']).strftime('%d.%m.%Y'))
            ws1.cell(row=idx, column=2, value=day_stat['occupied'])
            ws1.cell(row=idx, column=3, value=day_stat['available'])
            ws1.cell(row=idx, column=4, value=f"{day_stat['occupancy_rate']:.1f}%")

        # Room type stats sheet
        ws2 = wb.create_sheet("Xona turlari")
        room_type_stats = AnalyticsService.get_room_type_stats(db, start_date, end_date)

        ws2.cell(row=1, column=1, value="Xona turlari bo'yicha statistika")
        ws2.cell(row=1, column=1).font = Font(bold=True, size=14)

        headers = ["Xona turi", "Jami xonalar", "Bronlar soni", "Band kunlar", "Bandlik %"]
        for col, header in enumerate(headers, 1):
            ws2.cell(row=3, column=col, value=header)
            ws2.cell(row=3, column=col).font = Font(bold=True)

        for idx, stat in enumerate(room_type_stats, 4):
            ws2.cell(row=idx, column=1, value=stat['room_type'])
            ws2.cell(row=idx, column=2, value=stat['total_rooms'])
            ws2.cell(row=idx, column=3, value=stat['bookings_count'])
            ws2.cell(row=idx, column=4, value=stat['total_booked_days'])
            ws2.cell(row=idx, column=5, value=f"{stat['occupancy_rate']}%")

        # Format all sheets
        for ws in wb.worksheets:
            for column in ws.columns:
                max_length = 0
                column_letter = get_column_letter(column[0].column)
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                ws.column_dimensions[column_letter].width = adjusted_width

        # Save to bytes
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output.getvalue()