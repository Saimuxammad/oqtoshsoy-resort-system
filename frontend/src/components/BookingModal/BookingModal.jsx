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
      toast.success('Bron muvaffaqiyatli yaratildi');
      onClose();
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Xatolik yuz berdi');
    }
  });

  const updateMutation = useMutation(
    ({ id, ...data }) => bookingService.updateBooking(id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('rooms');
        toast.success('Bron muvaffaqiyatli yangilandi');
        onClose();
      },
      onError: (error) => {
        toast.error(error.response?.data?.detail || 'Xatolik yuz berdi');
      }
    }
  );

  const handleSubmit = (data) => {
    if (booking) {
      updateMutation.mutate({ id: booking.id, ...data });
    } else {
      createMutation.mutate(data);
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
      />
    </Modal>
  );
}