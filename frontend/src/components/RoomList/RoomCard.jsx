import React from 'react';
import { Card, CardContent } from '../UI/Card';
import { Button } from '../UI/Button';
import { RoomStatusBadge } from './RoomStatusBadge';
import { CalendarDaysIcon, PencilIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { useMutation, useQueryClient } from 'react-query';
import { bookingService } from '../../services/bookingService';
import toast from 'react-hot-toast';
import { format } from 'date-fns';
import { uz } from 'date-fns/locale';

export function RoomCard({ room, onEdit, onViewCalendar }) {
  const queryClient = useQueryClient();

  // Отмена бронирования
  const cancelBookingMutation = useMutation(
    (bookingId) => bookingService.deleteBooking(bookingId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('rooms');
        toast.success('Bron bekor qilindi');
      },
      onError: (error) => {
        toast.error('Xatolik yuz berdi');
      }
    }
  );

  const handleCancelBooking = (e) => {
    e.stopPropagation();
    if (window.confirm('Bronni bekor qilmoqchimisiz?')) {
      cancelBookingMutation.mutate(room.current_booking.id);
    }
  };

  const formatDate = (date) => {
    return format(new Date(date), 'dd MMM', { locale: uz });
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

            {/* Информация о текущем бронировании */}
            {room.current_booking && (
              <div className="bg-red-50 p-2 rounded-md mb-2">
                <p className="text-sm font-medium text-red-900">
                  {room.current_booking.guest_name || 'Mehmon nomi ko\'rsatilmagan'}
                </p>
                <p className="text-xs text-red-700">
                  {formatDate(room.current_booking.start_date)} - {formatDate(room.current_booking.end_date)}
                </p>
                {room.current_booking.notes && (
                  <p className="text-xs text-red-600 mt-1">
                    {room.current_booking.notes}
                  </p>
                )}
              </div>
            )}

            {/* Будущие бронирования */}
            {room.upcoming_bookings && room.upcoming_bookings.length > 0 && (
              <div className="mt-2">
                <p className="text-xs text-gray-500 mb-1">Keyingi bronlar:</p>
                <div className="space-y-1">
                  {room.upcoming_bookings.slice(0, 2).map((booking, idx) => (
                    <div key={idx} className="text-xs text-gray-600 bg-gray-50 p-1 rounded">
                      {formatDate(booking.start_date)} - {booking.guest_name || 'Mehmon'}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="flex gap-1">
            {/* Кнопка отмены брони */}
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
              title={room.is_available ? "Bron qilish" : "Tahrirlash"}
            >
              <PencilIcon className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}