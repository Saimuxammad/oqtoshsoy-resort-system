import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { bookingService } from '../../services/bookingService';
import { Card, CardHeader, CardContent } from '../UI/Card';
import { Button } from '../UI/Button';
import { Loading } from '../UI/Loading';
import { format } from 'date-fns';
import { uz } from 'date-fns/locale';
import { TrashIcon, PencilIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

export function BookingsList() {
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState({});

  const { data: bookings, isLoading } = useQuery(
    ['bookings', filters],
    () => bookingService.getBookings(filters)
  );

  const deleteMutation = useMutation(
    (bookingId) => bookingService.deleteBooking(bookingId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('bookings');
        queryClient.invalidateQueries('rooms');
        toast.success('Bron o\'chirildi');
      }
    }
  );

  const handleDelete = (bookingId) => {
    if (window.confirm('Bronni o\'chirmoqchimisiz?')) {
      deleteMutation.mutate(bookingId);
    }
  };

  if (isLoading) return <Loading />;

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Barcha bronlar</h2>

      {bookings && bookings.length > 0 ? (
        <div className="grid gap-4">
          {bookings.map((booking) => (
            <Card key={booking.id}>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">
                      Xona №{booking.room?.room_number || booking.room_id}
                    </p>
                    <p className="text-sm text-gray-600">
                      {booking.guest_name || 'Mehmon nomi ko\'rsatilmagan'}
                    </p>
                    <p className="text-sm text-gray-500">
                      {format(new Date(booking.start_date), 'dd.MM.yyyy')} -
                      {format(new Date(booking.end_date), 'dd.MM.yyyy')}
                    </p>
                    {booking.notes && (
                      <p className="text-sm text-gray-500 mt-1">{booking.notes}</p>
                    )}
                  </div>

                  <div className="flex gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => console.log('Edit booking', booking.id)}
                    >
                      <PencilIcon className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => handleDelete(booking.id)}
                      loading={deleteMutation.isLoading}
                    >
                      <TrashIcon className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <p className="text-center text-gray-500 py-8">Bronlar topilmadi</p>
      )}
    </div>
  );
}