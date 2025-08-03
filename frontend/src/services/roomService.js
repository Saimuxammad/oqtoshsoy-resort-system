import api from './api';

export const roomService = {
  // Get all rooms - ИСПРАВЛЕНО: убран /list
  getRooms: async (filters = {}) => {
    try {
      const params = new URLSearchParams();
      if (filters.type) params.append('room_type', filters.type);
      if (filters.status) params.append('status', filters.status);

      const response = await api.get(`/rooms?${params}`);
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
      const response = await api.get(`/rooms/${roomId}`);
      return response.data;
    } catch (error) {
      console.error('getRoom error:', error);
      throw error;
    }
  },

  // Update room
  updateRoom: async (roomId, data) => {
    try {
      console.log('Updating room:', roomId, data);
      const response = await api.patch(`/rooms/${roomId}`, data);
      console.log('Room updated:', response.data);
      return response.data;
    } catch (error) {
      console.error('updateRoom error:', error);
      throw error;
    }
  },

  // Get room availability
  checkAvailability: async (roomId, startDate, endDate) => {
    try {
      const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate
      });
      const response = await api.get(`/rooms/${roomId}/availability?${params}`);
      return response.data;
    } catch (error) {
      console.error('checkAvailability error:', error);
      throw error;
    }
  }
};