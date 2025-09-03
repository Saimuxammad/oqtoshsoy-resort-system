import api from './api';

export const roomService = {
  getRooms: async (filters = {}) => {
    try {
      console.log('[RoomService] Getting rooms with filters:', filters);

      // Формируем параметры запроса
      const params = new URLSearchParams();
      if (filters.type) params.append('room_type', filters.type);
      if (filters.status) params.append('status', filters.status);

      const url = params.toString() ? `rooms?${params}` : 'rooms';
      const response = await api.get(url);

      console.log('[RoomService] API Response:', response.data);
      console.log('[RoomService] Response type:', typeof response.data);
      console.log('[RoomService] Is array:', Array.isArray(response.data));

      // Проверяем что получили массив
      if (!Array.isArray(response.data)) {
        console.error('[RoomService] Response is not an array:', response.data);
        return [];
      }

      // Маппинг типов комнат для отображения
      const roomTypeMap = {
        "2 o'rinli standart": "2 o'rinli standart",
        "4 o'rinli standart": "4 o'rinli standart",
        "2 o'rinli lyuks": "2 o'rinli lyuks",
        "4 o'rinli kichik VIP": "4 o'rinli kichik VIP",
        "4 o'rinli katta VIP": "4 o'rinli katta VIP",
        "4 o'rinli apartament": "4 o'rinli apartament",
        "Kottedj (6 kishi uchun)": "Kottedj (6 kishi uchun)",
        "Prezident apartamenti (8 kishi uchun)": "Prezident apartamenti (8 kishi uchun)",
        // Альтернативные названия на случай если backend вернет другие
        'STANDARD_DOUBLE': "2 o'rinli standart",
        'STANDARD_QUAD': "4 o'rinli standart",
        'LUX_DOUBLE': "2 o'rinli lyuks",
        'VIP_SMALL': "4 o'rinli kichik VIP",
        'VIP_LARGE': "4 o'rinli katta VIP",
        'APARTMENT': "4 o'rinli apartament",
        'COTTAGE': "Kottedj (6 kishi uchun)",
        'PRESIDENT': "Prezident apartamenti (8 kishi uchun)"
      };

      // Преобразуем данные
      const rooms = response.data.map(room => ({
        ...room,
        room_type: roomTypeMap[room.room_type] || room.room_type,
        // Убеждаемся что все поля есть
        capacity: room.capacity || 2,
        price_per_night: room.price_per_night || 500000,
        description: room.description || '',
        amenities: room.amenities || '',
        is_available: room.is_available !== undefined ? room.is_available : true,
        current_booking: room.current_booking || null
      }));

      console.log('[RoomService] Processed rooms count:', rooms.length);
      console.log('[RoomService] First 3 rooms:', rooms.slice(0, 3));

      return rooms;
    } catch (error) {
      console.error('[RoomService] getRooms error:', error);
      console.error('[RoomService] Error response:', error.response);

      // Возвращаем пустой массив при ошибке
      return [];
    }
  },

  getRoom: async (roomId) => {
    try {
      console.log('[RoomService] Getting room:', roomId);
      const response = await api.get(`rooms/${roomId}`);
      console.log('[RoomService] Room data:', response.data);
      return response.data;
    } catch (error) {
      console.error('[RoomService] getRoom error:', error);
      throw error;
    }
  },

  updateRoom: async (roomId, data) => {
    try {
      console.log('[RoomService] Updating room:', roomId, data);
      const response = await api.patch(`rooms/${roomId}`, data);
      console.log('[RoomService] Room updated:', response.data);
      return response.data;
    } catch (error) {
      console.error('[RoomService] updateRoom error:', error);
      throw error;
    }
  },

  checkAvailability: async (roomId, startDate, endDate) => {
    try {
      const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate
      });
      const response = await api.get(`rooms/${roomId}/availability?${params}`);
      console.log('[RoomService] Availability:', response.data);
      return response.data;
    } catch (error) {
      console.error('[RoomService] checkAvailability error:', error);
      throw error;
    }
  }
};