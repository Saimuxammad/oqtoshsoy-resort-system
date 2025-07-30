import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { bookingService } from '../../services/bookingService';
import { roomService } from '../../services/roomService';
import { Loading } from '../UI/Loading';
import { Button } from '../UI/Button';
import { Card, CardContent } from '../UI/Card';
import { format } from 'date-fns';
import { uz } from 'date-fns/locale';
import { ArrowPathIcon, TrashIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

export function BookingsList() {
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState({});

  // Загружаем все комнаты для сопоставления ID с номерами
  const { data: rooms } = useQuery('allRooms', () => roomService.getRooms());

  const { data: bookings, isLoading, refetch } = useQuery(
    ['bookings', filters],
    () => bookingService.getBookings(filters),
    {
      onError: (error) => {
        toast.error('Bronlarni yuklashda xatolik');
      }
    }
  );

  const deleteMutation = useMutation(
    (bookingId) => bookingService.deleteBooking(bookingId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('bookings');
        queryClient.invalidateQueries('rooms');
        toast.success('Bron o\'chirildi');
      },
      onError: (error) => {
        if (error.response?.status === 403) {
          toast.error('Bronni o\'chirish uchun admin huquqi kerak');
        } else {
          toast.error('Xatolik yuz berdi');
        }
      }
    }
  );

  const handleRefresh = () => {
    refetch();
    toast.success('Yangilandi');
  };

  const handleDelete = (bookingId) => {
    if (window.confirm('Bronni o\'chirishni tasdiqlaysizmi?')) {
      deleteMutation.mutate(bookingId);
    }
  };

  // Функция для получения информации о комнате по ID
  const getRoomInfo = (roomId) => {
    const room = rooms?.find(r => r.id === roomId);
    return room || null;
  };

  if (isLoading) return <Loading />;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-900">
          Barcha bronlar {bookings && `(${bookings.length})`}
        </h2>
        <Button
          variant="secondary"
          size="sm"
          onClick={handleRefresh}
        >
          <ArrowPathIcon className="h-4 w-4 mr-2" />
          Qayta yuklash
        </Button>
      </div>

      {!bookings || bookings.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12 text-gray-500">
            <p>Hozircha bronlar yo'q</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {bookings.map((booking) => {
            const roomInfo = getRoomInfo(booking.room_id);
            return (
              <Card key={booking.id}>
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          Xona №{roomInfo?.room_number || booking.room_id}
                        </h3>
                        {roomInfo && (
                          <span className="text-sm text-gray-600">
                            {roomInfo.room_type}
                          </span>
                        )}
                      </div>

                      <p className="text-sm text-gray-600 mb-1">
                        <span className="font-medium">Sanalar:</span>{' '}
                        {format(new Date(booking.start_date), 'dd MMMM yyyy', { locale: uz })} - {' '}
                        {format(new Date(booking.end_date), 'dd MMMM yyyy', { locale: uz })}
                      </p>

                      {booking.guest_name && (
                        <p className="text-sm text-gray-600 mb-1">
                          <span className="font-medium">Mehmon:</span> {booking.guest_name}
                        </p>
                      )}

                      {booking.notes && (
                        <p className="text-sm text-gray-600">
                          <span className="font-medium">Izoh:</span> {booking.notes}
                        </p>
                      )}
                    </div>

                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => handleDelete(booking.id)}
                      loading={deleteMutation.isLoading}
                      title="O'chirish"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}