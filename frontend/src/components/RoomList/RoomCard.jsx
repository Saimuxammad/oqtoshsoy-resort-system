import React from 'react';
import { Card, CardContent } from '../UI/Card';
import { Button } from '../UI/Button';
import { RoomStatusBadge } from './RoomStatusBadge';
import { CalendarDaysIcon, PencilIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { useMutation, useQueryClient } from 'react-query';
import { bookingService } from '../../services/bookingService';
import { useTelegram } from '../../hooks/useTelegram';
import toast from 'react-hot-toast';

export function RoomCard({ room, onEdit, onViewCalendar }) {
  const queryClient = useQueryClient();
  const { user } = useTelegram();

  const cancelBookingMutation = useMutation(
    (bookingId) => bookingService.deleteBooking(bookingId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('rooms');
        queryClient.invalidateQueries('bookings');
        toast.success('Bron bekor qilindi');
      },
      onError: (error) => {
        console.error('Cancel booking error:', error);
        if (error.response?.status === 403) {
          toast.error('Bronni bekor qilish uchun admin huquqi kerak');
        } else if (error.response?.status === 404) {
          toast.error('Bron topilmadi');
        } else {
          toast.error(error.response?.data?.detail || 'Xatolik yuz berdi');
        }
      }
    }
  );

  const handleCancelBooking = () => {
    if (room.current_booking?.id) {
      if (window.confirm('Bronni bekor qilishni tasdiqlaysizmi?')) {
        cancelBookingMutation.mutate(room.current_booking.id);
      }
    }
  };

  // Admin yoki o'zi yaratgan bronni bekor qilish mumkin
  const canCancelBooking = room.current_booking && user;

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
            {canCancelBooking && (
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