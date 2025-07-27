// roomService.js
import api from './api';

export const roomService = {
  getRooms: async (filters = {}) => {
    try {
      console.log('🔄 Запрос комнат с фильтрами:', filters);
      const params = new URLSearchParams();

      // Добавляем параметры фильтрации, если они есть
      if (filters.roomType) params.append('roomType', filters.roomType);
      if (filters.status) params.append('status', filters.status);

      // Запрос к API
      const response = await api.get(`/rooms?${params.toString()}`);
      console.log('✅ Ответ от сервера:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Ошибка при получении комнат:', error);
      throw error;
    }
  }
};
