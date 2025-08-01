import React from 'react';
import { Card, CardContent } from '../UI/Card';
import { Button } from '../UI/Button';
import { RoomStatusBadge } from './RoomStatusBadge';
import { CalendarDaysIcon, PencilIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { useMutation, useQueryClient } from 'react-query';
import { bookingService } from '../../services/bookingService';
import toast from 'react-hot-toast';
import { useTelegram } from '../../hooks/useTelegram';

export function RoomCard({ room, onEdit, onViewCalendar }) {
  const queryClient = useQueryClient();
  const { showConfirm } = useTelegram();

  const cancelBookingMutation = useMutation(
    (bookingId) => {
      console.log('[RoomCard] Cancelling booking:', bookingId);
      return bookingService.deleteBooking(bookingId);
    },
    {
      onSuccess: () => {
        console.log('[RoomCard] Booking cancelled successfully');
        queryClient.invalidateQueries('rooms');
        queryClient.invalidateQueries('bookings');
        toast.success('Bron bekor qilindi');
      },
      onError: (error) => {
        console.error('[RoomCard] Cancel booking error:', error);
        toast.error(error.response?.data?.detail || 'Xatolik yuz berdi');
      }
    }
  );

  const handleCancelBooking = () => {
    if (room.current_booking?.id) {
      console.log('[RoomCard] Current booking:', room.current_booking);
      console.log('[RoomCard] Booking ID to delete:', room.current_booking.id);
      console.log('[RoomCard] Current URL:', window.location.href);

      // Проверяем, какой URL будет использован
      const testUrl = `https://oqtoshsoy-resort-system-production.up.railway.app/api/bookings/${room.current_booking.id}`;
      console.log('[RoomCard] Will send DELETE to:', testUrl);

      // Используем стандартный confirm, если Telegram метод недоступен
      if (showConfirm && window.Telegram?.WebApp) {
        showConfirm('Bronni bekor qilishni tasdiqlaysizmi?', (confirmed) => {
          if (confirmed) {
            cancelBookingMutation.mutate(room.current_booking.id);
          }
        });
      } else {
        // Fallback для браузера
        const confirmed = window.confirm('Bronni bekor qilishni tasdiqlaysizmi?');
        if (confirmed) {
          cancelBookingMutation.mutate(room.current_booking.id);
        }
      }
    }
  };

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h3 className="text-lg font-semibold text-gray-900">
                №{room.room_number}
              </h3>
              <RoomStatusBadge
                isAvailable={room.is_available}
                booking={room.current_booking}
              />
            </div>

            <p className="text-sm text-gray-600 mb-3">
              {room.room_type}
            </p>

            {room.current_booking?.guest_name && (
              <p className="text-xs text-gray-500">
                Mehmon: {room.current_booking.guest_name}
              </p>
            )}
          </div>

          <div className="flex gap-2">
            {room.current_booking && (
              <Button
                variant="danger"
                size="sm"
                onClick={handleCancelBooking}
                title="Bronni bekor qilish"
                loading={cancelBookingMutation.isLoading}
              >
                <XMarkIcon className="h-4 w-4" />
              </Button>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onViewCalendar(room)}
              title="Kalendar"
            >
              <CalendarDaysIcon className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onEdit(room)}
              title="Tahrirlash"
            >
              <PencilIcon className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}