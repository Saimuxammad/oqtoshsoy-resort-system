import api from './api';

export const roomService = {
  // Get all rooms - Используем raw эндпоинт для обхода проблем с моделями
  getRooms: async (filters = {}) => {
    try {
      // Сначала пробуем raw эндпоинт
      const response = await api.get('/rooms-raw');
      console.log('Rooms loaded from raw endpoint:', response.data);

      // Преобразуем ENUM значения в читаемые
      const roomTypeMap = {
        'STANDARD_DOUBLE': "2 o'rinli standart",
        'STANDARD_QUAD': "4 o'rinli standart",
        'LUX_DOUBLE': "2 o'rinli lyuks",
        'VIP_SMALL': "4 o'rinli kichik VIP",
        'VIP_LARGE': "4 o'rinli katta VIP",
        'APARTMENT': "4 o'rinli apartament",
        'COTTAGE': "Kottedj (6 kishi uchun)",
        'PRESIDENT': "Prezident apartamenti (8 kishi uchun)"
      };

      if (Array.isArray(response.data)) {
        return response.data.map(room => ({
          ...room,
          room_type: roomTypeMap[room.room_type] || room.room_type
        }));
      }

      return response.data;
    } catch (error) {
      console.error('getRooms error:', error);
      // Возвращаем пустой массив при ошибке
      return [];
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