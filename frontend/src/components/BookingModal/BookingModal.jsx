import React from 'react';
import { Modal } from '../UI/Modal';
import { BookingForm } from './BookingForm';
import { useMutation, useQueryClient } from 'react-query';
import { bookingService } from '../../services/bookingService';
import toast from 'react-hot-toast';

export function BookingModal({ isOpen, onClose, room, booking = null }) {
  const queryClient = useQueryClient();

  const createMutation = useMutation(bookingService.createBooking, {
    onSuccess: () => {
      queryClient.invalidateQueries('rooms');
      queryClient.invalidateQueries('bookings');
      toast.success('Bron muvaffaqiyatli yaratildi');
      onClose();
    },
    onError: (error) => {
      console.error('Create booking error:', error.response?.data);
      toast.error(error.response?.data?.detail || 'Xatolik yuz berdi');
    }
  });

  const updateMutation = useMutation(
    ({ id, ...data }) => bookingService.updateBooking(id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('rooms');
        queryClient.invalidateQueries('bookings');
                toast.success('Bron muvaffaqiyatli yangilandi');
        onClose();
      },
      onError: (error) => {
        console.error('Update booking error:', error.response?.data);
        toast.error(error.response?.data?.detail || 'Xatolik yuz berdi');
      }
    }
  );

  const deleteMutation = useMutation(
    (bookingId) => bookingService.deleteBooking(bookingId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('rooms');
        queryClient.invalidateQueries('bookings');
        toast.success('Bron bekor qilindi');
        onClose();
      },
      onError: (error) => {
        console.error('Delete booking error:', error.response?.data);
        toast.error(error.response?.data?.detail || 'Xatolik yuz berdi');
      }
    }
  );

  const handleSubmit = (data, isExtending = false) => {
    console.log('BookingModal handleSubmit:', { booking, data, isExtending });

    // При продлении всегда создаем новое бронирование
    if (isExtending) {
      createMutation.mutate(data);
    } else if (booking) {
      // Обновляем существующее бронирование
      updateMutation.mutate({ id: booking.id, ...data });
    } else {
      // Создаем новое бронирование
      createMutation.mutate(data);
    }
  };

  const handleDelete = () => {
    if (booking && window.confirm('Bronni o\'chirishni tasdiqlaysizmi?')) {
      deleteMutation.mutate(booking.id);
    }
  };

  const handleExtend = () => {
    if (booking) {
      // Создаем новое бронирование сразу после текущего
      const nextDay = new Date(booking.end_date);
      nextDay.setDate(nextDay.getDate() + 1);

      const extendedBooking = {
        room_id: room.id,
        start_date: nextDay.toISOString().split('T')[0],
        end_date: null, // Пользователь выберет
        guest_name: booking.guest_name,
        notes: booking.notes ? `${booking.notes} (davomi)` : 'Davomi'
      };

      // Открываем форму с предзаполненными данными для продления
      // Это потребует передачи данных в BookingForm
      console.log('Extend booking with:', extendedBooking);
      toast.info('Davom etish uchun yangi sanani tanlang');
    }
  };

  if (!room) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={booking ? 'Bronni tahrirlash' : 'Yangi bron'}
    >
      <BookingForm
        room={room}
        booking={booking}
        onSubmit={handleSubmit}
        onCancel={onClose}
        onDelete={booking ? handleDelete : undefined}
        onExtend={booking ? handleExtend : undefined}
        isLoading={createMutation.isLoading || updateMutation.isLoading || deleteMutation.isLoading}
      />
    </Modal>
  );
}