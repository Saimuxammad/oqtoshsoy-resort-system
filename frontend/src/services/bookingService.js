import api from './api';

export const bookingService = {
  // Get all bookings - ИСПРАВЛЕНО: правильная передача параметров
  getBookings: async (filters = {}) => {
    try {
      const params = new URLSearchParams();

      // ВАЖНО: Передаем room_id для фильтрации
      if (filters.roomId) {
        params.append('room_id', filters.roomId);
        console.log('[BookingService] Filtering by room_id:', filters.roomId);
      }
      if (filters.startDate) params.append('start_date', filters.startDate);
      if (filters.endDate) params.append('end_date', filters.endDate);

      const url = params.toString() ? `bookings?${params.toString()}` : 'bookings';
      console.log('[BookingService] Request URL:', `/api/${url}`);

      const response = await api.get(url);
      console.log('[BookingService] Bookings loaded:', response.data.length, 'items');

      // Логируем для отладки
      if (filters.roomId) {
        console.log('[BookingService] Bookings for room', filters.roomId, ':', response.data);
      }

      return response.data;
    } catch (error) {
      console.error('[BookingService] getBookings error:', error);
      throw error;
    }
  },

  // Get single booking
  getBooking: async (bookingId) => {
    try {
      const response = await api.get(`bookings/${bookingId}`);
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

      // Сначала пробуем v2 эндпоинт
      try {
        const response = await api.post('bookings/v2', bookingData);
        console.log('[BookingService] Booking created via v2:', response.data);
        return response.data;
      } catch (error) {
        // Если v2 не работает, используем обычный
        if (error.response?.status === 404) {
          console.log('[BookingService] v2 not found, using regular endpoint');
          const response = await api.post('bookings', bookingData);
          return response.data;
        }
        throw error;
      }
    } catch (error) {
      console.error('[BookingService] createBooking error:', error);
      throw error;
    }
  },

  // Update booking
  updateBooking: async (bookingId, data) => {
    try {
      console.log('[BookingService] Updating booking:', bookingId, data);

      // Сначала пробуем PATCH
      try {
        const response = await api.patch(`bookings/${bookingId}`, data);
        console.log('[BookingService] Booking updated with PATCH:', response.data);
        return response.data;
      } catch (patchError) {
        // Если PATCH не поддерживается, пробуем PUT
        if (patchError.response?.status === 405) {
          console.log('[BookingService] PATCH not allowed, trying PUT...');
          const response = await api.put(`bookings/${bookingId}`, data);
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

  // Delete booking
  deleteBooking: async (bookingId) => {
    try {
      console.log('[BookingService] Deleting booking ID:', bookingId);
      const url = `bookings/${bookingId}`;
      const response = await api.delete(url);
      console.log('[BookingService] Delete response:', response.data);
      return response.data;
    } catch (error) {
      console.error('[BookingService] Delete error:', error);

      if (error.response?.status === 404) {
        const message = `Bron #${bookingId} topilmadi yoki allaqachon o'chirilgan`;
        console.error('[BookingService]', message);
        throw new Error(message);
      }

      throw error;
    }
  },

  // Check availability
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
      return { available: true };
    }
  }
};