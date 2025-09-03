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
        console.error('Bookings fetch error:', error);
        toast.error('Bronlarni yuklashda xatolik');
      }
    }
  );

  const deleteMutation = useMutation(
    (bookingId) => {
      console.log('[BookingsList] Deleting booking with ID:', bookingId);
      return bookingService.deleteBooking(bookingId);
    },
    {
      onSuccess: (data, bookingId) => {
        console.log('[BookingsList] Successfully deleted booking:', bookingId);
        queryClient.invalidateQueries('bookings');
        queryClient.invalidateQueries('rooms');
        toast.success('Bron muvaffaqiyatli o\'chirildi');
      },
      onError: (error, bookingId) => {
        console.error('[BookingsList] Delete error for booking', bookingId, ':', error);
        console.error('Error response:', error.response);

        if (error.response?.status === 404) {
          toast.error(`Bron #${bookingId} topilmadi`);
        } else if (error.response?.status === 405) {
          toast.error('Server xatosi: Method Not Allowed');
        } else {
          toast.error(error.response?.data?.detail || 'Bronni o\'chirishda xatolik');
        }
      }
    }
  );

  const handleDelete = (booking) => {
    console.log('[BookingsList] handleDelete called with booking:', booking);

    // Проверяем что у нас есть правильный ID
    const bookingId = booking.id;

    if (!bookingId) {
      console.error('[BookingsList] No booking ID provided');
      toast.error('Bron ID topilmadi');
      return;
    }

    console.log('[BookingsList] Confirming deletion for booking ID:', bookingId);

    if (window.confirm(`Bron #${bookingId} ni o'chirishni tasdiqlaysizmi?`)) {
      console.log('[BookingsList] User confirmed deletion');
      deleteMutation.mutate(bookingId);
    } else {
      console.log('[BookingsList] User cancelled deletion');
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
                      <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                        ID: {booking.id}
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
                    onClick={() => handleDelete(booking)}
                    loading={deleteMutation.isLoading}
                    title={`Bron #${booking.id} ni bekor qilish`}
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