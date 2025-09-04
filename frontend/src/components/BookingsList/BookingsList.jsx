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

export function BookingsList({ currentUser }) {  // ← ДОБАВИЛИ currentUser
  const [filters, setFilters] = useState({});
  const queryClient = useQueryClient();

  // Проверяем права доступа
  const canDelete = currentUser?.is_admin || currentUser?.can_modify;

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
    (bookingId) => bookingService.deleteBooking(bookingId),
    {
      onSuccess: (data, bookingId) => {
        queryClient.invalidateQueries('bookings');
        queryClient.invalidateQueries('rooms');
        toast.success("Bron muvaffaqiyatli o'chirildi");
      },
      onError: (error, bookingId) => {
        if (error.response?.status === 404) {
          toast.error(`Bron #${bookingId} topilmadi`);
        } else {
          toast.error(error.response?.data?.detail || "Bronni o'chirishda xatolik");
        }
      }
    }
  );

  const handleDelete = (booking) => {
    if (!canDelete) {
      toast.error("Sizda o'chirish huquqi yo'q");
      return;
    }

    const bookingId = booking.id;
    if (!bookingId) {
      toast.error('Bron ID topilmadi');
      return;
    }

    if (window.confirm(`Bron #${bookingId} ni o'chirishni tasdiqlaysizmi?`)) {
      deleteMutation.mutate(bookingId);
    }
  };

  const handleRefresh = () => {
    refetch();
    toast.success('Yangilandi');
  };

  if (isLoading) return <Loading text="Bronlar yuklanmoqda..." />;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-900">
          Barcha bronlar {bookings && `(${bookings.length} ta)`}
        </h2>
        <Button
          variant="secondary"
          size="sm"
          onClick={handleRefresh}
        >
          <ArrowPathIcon className="h-4 w-4 mr-2" />
          Yangilash
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

                  {/* ВОТ ЗДЕСЬ ГЛАВНОЕ ИЗМЕНЕНИЕ - КНОПКА ПОКАЗЫВАЕТСЯ ТОЛЬКО АДМИНАМ */}
                  {canDelete && (
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => handleDelete(booking)}
                      loading={deleteMutation.isLoading}
                      title={`Bron #${booking.id} ni bekor qilish`}
                    >
                      <TrashIcon className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {!canDelete && (
        <div className="mt-4 p-3 bg-gray-50 border border-gray-200 rounded-lg">
          <p className="text-sm text-gray-600">
            💡 Eslatma: Sizda faqat ko'rish huquqi mavjud. Bronlarni o'chirish uchun administrator bilan bog'laning.
          </p>
        </div>
      )}
    </div>
  );
}