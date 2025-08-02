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

      // Получаем токен
      const token = localStorage.getItem('auth_token') ||
                    sessionStorage.getItem('auth_token') ||
                    'dev_token';

      // Используем прямой fetch как временное решение
      const url = `https://oqtoshsoy-resort-system-production.up.railway.app/api/bookings/${bookingId}`;
      console.log('Direct fetch to:', url);

      const response = await fetch(url, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json'
        }
      });

      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Error response:', errorText);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      console.log('Booking deleted:', data);
      return data;

    } catch (error) {
      console.error('deleteBooking error:', error);
      throw error;
    }
  }
};