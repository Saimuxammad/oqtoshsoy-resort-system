import api from '../utils/api';

export const roomService = {
  // Получить список комнат с фильтрами
  getRooms: async (filters = {}) => {
    try {
      const params = {};

      if (filters.type) params.type = filters.type;
      if (filters.available !== undefined) params.available = filters.available;

      const response = await api.get('/rooms/list', {
        params
      });

      console.log('[RoomService] Rooms loaded:', response.data);
      return response.data;
    } catch (error) {
      console.error('[RoomService] getRooms error:', error);
      throw error;
    }
  },

  // Получить одну комнату по ID
  getRoom: async (roomId) => {
    try {
      const response = await api.get(`/rooms/${roomId}`);
      console.log('[RoomService] Room loaded:', response.data);
      return response.data;
    } catch (error) {
      console.error('[RoomService] getRoom error:', error);
      throw error;
    }
  },

  // Обновить данные комнаты
  updateRoom: async (roomId, data) => {
    try {
      const response = await api.patch(`/rooms/${roomId}`, data);
      console.log('[RoomService] Room updated:', response.data);
      return response.data;
    } catch (error) {
      console.error('[RoomService] updateRoom error:', error);
      throw error;
    }
  }
};
