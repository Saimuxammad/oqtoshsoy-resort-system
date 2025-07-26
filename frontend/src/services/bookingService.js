import api from './api';

export const bookingService = {
  // Get all bookings
  getBookings: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.roomId) params.append('room_id', filters.roomId);
    if (filters.startDate) params.append('start_date', filters.startDate);
    if (filters.endDate) params.append('end_date', filters.endDate);

    const response = await api.get(`/bookings?${params}`);
    return response.data;
  },

  // Create booking
  createBooking: async (booking) => {
    const response = await api.post('/bookings', booking);
    return response.data;
  },

  // Update booking
  updateBooking: async (bookingId, data) => {
    const response = await api.patch(`/bookings/${bookingId}`, data);
    return response.data;
  },

  // Delete booking
  deleteBooking: async (bookingId) => {
    const response = await api.delete(`/bookings/${bookingId}`);
    return response.data;
  }
};