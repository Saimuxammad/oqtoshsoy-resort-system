import api from '../utils/api';

export const roomService = {
  // Get all rooms
  getRooms: async (filters = {}) => {
    try {
      const params = new URLSearchParams();
      if (filters.type) params.append('type', filters.type);
      if (filters.available !== undefined) params.append('available', filters.available);

      const response = await api.get(`/api/rooms?${params}`);
      console.log('Rooms loaded:', response.data);
      return response.data;
    } catch (error) {
      console.error('getRooms error:', error);
      throw error;
    }
  },

  // Get single room
  getRoom: async (roomId) => {
    try {
      const response = await api.get(`/api/rooms/${roomId}`);
      return response.data;
    } catch (error) {
      console.error('getRoom error:', error);
      throw error;
    }
  },

  // Update room
  updateRoom: async (roomId, data) => {
    try {
      const response = await api.patch(`/api/rooms/${roomId}`, data);
      return response.data;
    } catch (error) {
      console.error('updateRoom error:', error);
      throw error;
    }
  }
};