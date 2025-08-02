import os
import httpx
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ..models.user import User
from ..models.booking import Booking
from ..models.room import Room


class NotificationService:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    async def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML"):
        """Send message via Telegram Bot API"""
        if not self.bot_token:
            print("Telegram bot token not configured")
            return

        url = f"{self.base_url}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data)
                if response.status_code != 200:
                    print(f"Failed to send message: {response.text}")
        except Exception as e:
            print(f"Error sending message: {e}")

    async def send_booking_created(self, db: Session, booking: Booking, room: Room, user: User):
        """Send notification about new booking"""
        # Format dates
        start_date = booking.start_date.strftime("%d.%m.%Y")
        end_date = booking.end_date.strftime("%d.%m.%Y")

        message = (
            f"🆕 <b>Yangi bron yaratildi</b>\n\n"
            f"🏠 Xona: №{room.room_number} ({room.room_type})\n"
            f"📅 Sanalar: {start_date} - {end_date}\n"
            f"👤 Mehmon: {booking.guest_name or 'Ko`rsatilmagan'}\n"
            f"👤 Bron qildi: {user.full_name}\n"
            f"🕐 Vaqt: {datetime.now().strftime('%H:%M')}"
        )

        # Send to all admins
        admins = db.query(User).filter(User.is_admin == True).all()
        for admin in admins:
            if admin.telegram_id and admin.telegram_id != user.telegram_id:
                await self.send_message(admin.telegram_id, message)

    async def send_booking_cancelled(self, db: Session, booking: Booking, room: Room, user: User):
        """Send notification about cancelled booking"""
        # Format dates
        start_date = booking.start_date.strftime("%d.%m.%Y")
        end_date = booking.end_date.strftime("%d.%m.%Y")

        message = (
            f"❌ <b>Bron bekor qilindi</b>\n\n"
            f"🏠 Xona: №{room.room_number} ({room.room_type})\n"
            f"📅 Sanalar: {start_date} - {end_date}\n"
            f"👤 Mehmon: {booking.guest_name or 'Ko`rsatilmagan'}\n"
            f"👤 Bekor qildi: {user.full_name}\n"
            f"🕐 Vaqt: {datetime.now().strftime('%H:%M')}"
        )

        # Send to all admins
        admins = db.query(User).filter(User.is_admin == True).all()
        for admin in admins:
            if admin.telegram_id:
                await self.send_message(admin.telegram_id, message)

    async def send_daily_report(self, db: Session):
        """Send daily report to admins"""
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)

        # Get today's bookings
        todays_bookings = db.query(Booking).filter(
            Booking.start_date <= today,
            Booking.end_date >= today
        ).all()

        # Get tomorrow's check-ins
        tomorrows_checkins = db.query(Booking).filter(
            Booking.start_date == tomorrow
        ).all()

        # Get tomorrow's check-outs
        tomorrows_checkouts = db.query(Booking).filter(
            Booking.end_date == tomorrow
        ).all()

        # Create report
        report_lines = ["📊 <b>Kunlik hisobot</b>", ""]
        report_lines.append(f"📅 Sana: {today.strftime('%d.%m.%Y')}")
        report_lines.append("")

        report_lines.append(f"🏠 Bugun band xonalar: {len(todays_bookings)}")
        for booking in todays_bookings:
            report_lines.append(f"  • №{booking.room.room_number} - {booking.guest_name or 'Mehmon'}")

        report_lines.append("")
        report_lines.append(f"➡️ Ertaga kirish: {len(tomorrows_checkins)}")
        for booking in tomorrows_checkins:
            report_lines.append(f"  • №{booking.room.room_number} - {booking.guest_name or 'Mehmon'}")

        report_lines.append("")
        report_lines.append(f"⬅️ Ertaga chiqish: {len(tomorrows_checkouts)}")
        for booking in tomorrows_checkouts:
            report_lines.append(f"  • №{booking.room.room_number} - {booking.guest_name or 'Mehmon'}")

        message = "\n".join(report_lines)

        # Send to all admins
        admins = db.query(User).filter(User.is_admin == True).all()
        for admin in admins:
            if admin.telegram_id:
                await self.send_message(admin.telegram_id, message)


notification_service = NotificationService()