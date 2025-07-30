import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { bookingService } from '../../services/bookingService';
import { Loading } from '../UI/Loading';
import { Button } from '../UI/Button';
import { Card, CardContent } from '../UI/Card';
import { format } from 'date-fns';
import { uz } from 'date-fns/locale';
import { ArrowPathIcon, TrashIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

export function BookingsList() {
  const [filters, setFilters] = useState({});
  const queryClient = useQueryClient();

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
        toast.success('Bron bekor qilindi');
      },
      onError: (error) => {
        console.error('Delete error:', error);
        toast.error(error.response?.data?.detail || 'Xatolik yuz berdi');
      }
    }
  );

  const handleDelete = async (bookingId) => {
    const confirmed = await window.Telegram?.WebApp?.showConfirm?.(
      'Bronni bekor qilishni tasdiqlaysizmi?'
    ) ?? window.confirm('Bronni bekor qilishni tasdiqlaysizmi?');

    if (confirmed) {
      deleteMutation.mutate(bookingId);
    }
  };

  const handleRefresh = () => {
    refetch();
    toast.success('Yangilandi');
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
          {bookings.map((booking) => (
            <Card key={booking.id}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        Xona №{booking.room?.room_number || booking.room_id}
                      </h3>
                      <span className="text-sm text-gray-600">
                        {booking.room?.room_type}
                      </span>
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
                    loading={deleteMutation.isLoading && deleteMutation.variables === booking.id}
                    title="Bronni bekor qilish"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}