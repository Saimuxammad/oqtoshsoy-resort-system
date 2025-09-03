import api from './api';

export const bookingService = {
  // Get all bookings
  getBookings: async (filters = {}) => {
    try {
      const params = new URLSearchParams();
      if (filters.roomId) params.append('room_id', filters.roomId);
      if (filters.startDate) params.append('start_date', filters.startDate);
      if (filters.endDate) params.append('end_date', filters.endDate);

      const response = await api.get(`/bookings?${params}`);
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

  // Create booking
  createBooking: async (booking) => {
    try {
      console.log('[BookingService] Creating booking:', booking);

      // Убеждаемся что даты в правильном формате
      const bookingData = {
        ...booking,
        start_date: booking.start_date,
        end_date: booking.end_date,
        room_id: parseInt(booking.room_id),
        guest_name: booking.guest_name || '',
        notes: booking.notes || ''
      };

      const response = await api.post('/bookings', bookingData);
      console.log('[BookingService] Booking created:', response.data);
      return response.data;
    } catch (error) {
      console.error('[BookingService] createBooking error:', error);
      console.error('[BookingService] Error response:', error.response);
      throw error;
    }
  },

  // Update booking - используем PATCH, с fallback на PUT
  updateBooking: async (bookingId, data) => {
    try {
      console.log('[BookingService] Updating booking:', bookingId, data);

      // Сначала пробуем PATCH
      try {
        const response = await api.patch(`/bookings/${bookingId}`, data);
        console.log('[BookingService] Booking updated with PATCH:', response.data);
        return response.data;
      } catch (patchError) {
        // Если PATCH не поддерживается (405), пробуем PUT
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

  // Delete booking - упрощенная версия
  deleteBooking: async (bookingId) => {
    try {
      console.log('[BookingService] Deleting booking:', bookingId);

      const response = await api.delete(`/bookings/${bookingId}`);

      console.log('[BookingService] Delete response:', response.data);
      return response.data;
    } catch (error) {
      console.error('[BookingService] Delete error:', error);
      console.error('[BookingService] Error response:', error.response);

      // Специальная обработка для 405 Method Not Allowed
      if (error.response?.status === 405) {
        const errorMsg = 'Server does not support DELETE method. Please check backend configuration.';
        console.error('[BookingService]', errorMsg);
        throw new Error(errorMsg);
      }

      throw error;
    }
  },

  // Проверка доступности номера для бронирования
  checkAvailability: async (roomId, startDate, endDate, excludeBookingId = null) => {
    try {
      const params = new URLSearchParams({
        room_id: roomId,
        start_date: startDate,
        end_date: endDate
      });

      if (excludeBookingId) {
        params.append('exclude_booking_id', excludeBookingId);
      }

      const response = await api.get(`/bookings/check-availability?${params}`);
      return response.data;
    } catch (error) {
      console.error('[BookingService] checkAvailability error:', error);
      throw error;
    }
  }
};