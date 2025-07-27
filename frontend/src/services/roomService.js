import api from './api';

export const roomService = {
  // Get all rooms
  getRooms: async (filters = {}) => {
    console.log('Fetching rooms from:', api.defaults.baseURL);
    const params = new URLSearchParams();
    if (filters.roomType) params.append('room_type', filters.roomType);
    if (filters.isAvailable !== undefined) params.append('is_available', filters.isAvailable);

    try {
      const response = await api.get(`/rooms?${params}`);
      console.log('Rooms response:', response.data);
      return response.data;
    } catch (error) {
      console.error('getRooms error:', error);
      throw error;
    }
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
  },

  // Create room (admin only)
  createRoom: async (data) => {
    const response = await api.post('/rooms', data);
    return response.data;
  }
};