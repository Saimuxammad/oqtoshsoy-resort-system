import api from './api';

export const roomService = {
  // Get all rooms - Используем raw эндпоинт для обхода проблем с моделями
  getRooms: async (filters = {}) => {
    try {
      // Сначала пробуем raw эндпоинт
      const response = await api.get('/rooms-raw');
      console.log('Rooms loaded from raw endpoint:', response.data);

      // Преобразуем ENUM значения в читаемые (обновленный маппинг)
      const roomTypeMap = {
        'STANDARD_2': "2 o'rinli standart",
        'STANDARD_4': "4 o'rinli standart",
        'LUX_2': "2 o'rinli lyuks",
        'VIP_SMALL_4': "4 o'rinli kichik VIP",
        'VIP_BIG_4': "4 o'rinli katta VIP",
        'APARTMENT_4': "4 o'rinli apartament",
        'COTTAGE_6': "Kottedj (6 kishi uchun)",
        'PRESIDENT_8': "Prezident apartamenti (8 kishi uchun)"
      };

      // Обновляем capacity на основе типа комнаты
      const capacityMap = {
        'STANDARD_2': 2,
        'STANDARD_4': 4,
        'LUX_2': 2,
        'VIP_SMALL_4': 4,
        'VIP_BIG_4': 4,
        'APARTMENT_4': 4,
        'COTTAGE_6': 6,
        'PRESIDENT_8': 8
      };

      // Обновляем цены на основе типа комнаты
      const priceMap = {
        'STANDARD_2': 500000,
        'STANDARD_4': 700000,
        'LUX_2': 800000,
        'VIP_SMALL_4': 1000000,
        'VIP_BIG_4': 1200000,
        'APARTMENT_4': 1500000,
        'COTTAGE_6': 2000000,
        'PRESIDENT_8': 3000000
      };

      if (Array.isArray(response.data)) {
        return response.data.map(room => ({
          ...room,
          room_type: roomTypeMap[room.room_type] || room.room_type,
          capacity: capacityMap[room.room_type] || room.capacity,
          price_per_night: priceMap[room.room_type] || room.price_per_night
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