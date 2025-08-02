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
      console.log('Bookings loaded:', response.data);
      return response.data;
    } catch (error) {
      console.error('getBookings error:', error);
      throw error;
    }
  },

  // Get single booking
  getBooking: async (bookingId) => {
    try {
      const response = await api.get(`/bookings/${bookingId}`);
      return response.data;
    } catch (error) {
      console.error('getBooking error:', error);
      throw error;
    }
  },

  // Create booking
  createBooking: async (booking) => {
    try {
      console.log('Creating booking:', booking);
      const response = await api.post('/bookings', booking);
      console.log('Booking created:', response.data);
      return response.data;
    } catch (error) {
      console.error('createBooking error:', error);
      throw error;
    }
  },

  // Update booking
  updateBooking: async (bookingId, data) => {
    try {
      console.log('Updating booking:', bookingId, data);
      const response = await api.patch(`/bookings/${bookingId}`, data);
      console.log('Booking updated:', response.data);
      return response.data;
    } catch (error) {
      console.error('updateBooking error:', error);
      throw error;
    }
  },

  // Delete booking
  deleteBooking: async (bookingId) => {
    try {
      console.log('Deleting booking:', bookingId);
      console.log('API base URL:', api.defaults.baseURL);
      console.log('Full URL:', `${api.defaults.baseURL}/bookings/${bookingId}`);

      const response = await api.delete(`/bookings/${bookingId}`);
      console.log('Booking deleted:', response.data);
      return response.data;
    } catch (error) {
      console.error('deleteBooking error:', error);
      console.error('Error response:', error.response);
      console.error('Error config:', error.config);

      // Показываем более детальную информацию об ошибке
      if (error.response) {
        console.error('Response status:', error.response.status);
        console.error('Response data:', error.response.data);
        console.error('Response headers:', error.response.headers);
      }

      throw error;
    }
  }
};