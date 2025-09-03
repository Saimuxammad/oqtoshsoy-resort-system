import api from './api';

export const bookingService = {
  // Get all bookings
  getBookings: async (filters = {}) => {
    try {
      const params = new URLSearchParams();
      if (filters.roomId) params.append('room_id', filters.roomId);
      if (filters.startDate) params.append('start_date', filters.startDate);
      if (filters.endDate) params.append('end_date', filters.endDate);

      const response = await api.get(`/bookings${params.toString() ? '?' + params.toString() : ''}`);
      console.log('[BookingService] Bookings loaded:', response.data);
      return response.data;
    } catch (error) {
      console.error('[BookingService] getBookings error:', error);
      throw error;
    }
  },

  // Get single booking
  getBooking: async (bookingId) => {
    try {
      const response = await api.get(`/bookings/${bookingId}`);
      return response.data;
    } catch (error) {
      console.error('[BookingService] getBooking error:', error);
      throw error;
    }
  },

  // Create booking - используем v2 эндпоинт с новой логикой
  createBooking: async (booking) => {
    try {
      console.log('[BookingService] Creating booking:', booking);

      const bookingData = {
        ...booking,
        start_date: booking.start_date,
        end_date: booking.end_date,
        room_id: parseInt(booking.room_id),
        guest_name: booking.guest_name || '',
        notes: booking.notes || ''
      };

      // Используем новый эндпоинт /bookings/v2
      const response = await api.post('/bookings/v2', bookingData);
      console.log('[BookingService] Booking created:', response.data);
      return response.data;
    } catch (error) {
      console.error('[BookingService] createBooking error:', error);

      // Если v2 не работает, пробуем обычный эндпоинт
      if (error.response?.status === 404) {
        console.log('[BookingService] v2 endpoint not found, trying regular endpoint');
        const response = await api.post('/bookings', booking);
        return response.data;
      }

      throw error;
    }
  },

  // Update booking
  updateBooking: async (bookingId, data) => {
    try {
      console.log('[BookingService] Updating booking:', bookingId, data);

      // Сначала пробуем PATCH
      try {
        const response = await api.patch(`/bookings/${bookingId}`, data);
        console.log('[BookingService] Booking updated with PATCH:', response.data);
        return response.data;
      } catch (patchError) {
        // Если PATCH не поддерживается, пробуем PUT
        if (patchError.response?.status === 405) {
          console.log('[BookingService] PATCH not allowed, trying PUT...');
          const response = await api.put(`/bookings/${bookingId}`, data);
          console.log('[BookingService] Booking updated with PUT:', response.data);
          return response.data;
        }
        throw patchError;
      }
    } catch (error) {
      console.error('[BookingService] updateBooking error:', error);
      throw error;
    }
  },

  // Delete booking - ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ
  deleteBooking: async (bookingId) => {
    try {
      console.log('[BookingService] Deleting booking ID:', bookingId);

      // Формируем правильный URL
      const url = `bookings/${bookingId}`;
      console.log('[BookingService] DELETE URL:', url);

      // Отправляем запрос
      const response = await api.delete(url);

      console.log('[BookingService] Delete response:', response.data);
      return response.data;
    } catch (error) {
      console.error('[BookingService] Delete error:', error);
      console.error('[BookingService] Error response:', error.response);

      if (error.response?.status === 404) {
        // Более информативное сообщение об ошибке
        const message = `Bron #${bookingId} topilmadi yoki allaqachon o'chirilgan`;
        console.error('[BookingService]', message);
        throw new Error(message);
      } else if (error.response?.status === 405) {
        throw new Error('Server does not support DELETE method');
      }

      throw error;
    }
  },

  // Check availability - упрощенная версия
  checkAvailability: async (roomId, startDate, endDate, excludeBookingId = null) => {
    try {
      console.log('[BookingService] Checking availability:', {
        roomId, startDate, endDate, excludeBookingId
      });

      // Пока эндпоинт не работает, возвращаем true
      // Сервер сам проверит при создании
      return { available: true };

    } catch (error) {
      console.error('[BookingService] checkAvailability error:', error);
      // При ошибке разрешаем создание
      return { available: true };
    }
  }
};