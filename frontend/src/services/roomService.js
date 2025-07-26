import api from './api';

export const roomService = {
  // Get all rooms
  getRooms: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.roomType) params.append('room_type', filters.roomType);
    if (filters.isAvailable !== undefined) params.append('is_available', filters.isAvailable);

    const response = await api.get(`/rooms?${params}`);
    return response.data;
  },

  // Get single room
  getRoom: async (roomId) => {
    const response = await api.get(`/rooms/${roomId}`);
    return response.data;
  },

  // Check room availability
  checkAvailability: async (roomId, startDate, endDate) => {
    const params = new URLSearchParams({
      start_date: startDate,
      end_date: endDate
    });
    const response = await api.get(`/rooms/${roomId}/availability?${params}`);
    return response.data;
  },

  // Update room
  updateRoom: async (roomId, data) => {
    const response = await api.patch(`/rooms/${roomId}`, data);
    return response.data;
  }
};