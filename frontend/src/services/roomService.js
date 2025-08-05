import api from './api';

export const roomService = {
  getRooms: async (filters = {}) => {
    try {
      const response = await api.get('rooms');
      console.log('Raw API response:', response);
      console.log('Response data:', response.data);
      console.log('Is response.data array?', Array.isArray(response.data));
      console.log('Response data length:', response.data?.length);

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

      // Убедимся, что у нас есть массив
      const rooms = Array.isArray(response.data) ? response.data : [];
      console.log('Rooms to transform:', rooms.length);

      const transformedRooms = rooms.map((room, index) => {
        const transformed = {
          ...room,
          room_type: roomTypeMap[room.room_type] || room.room_type
        };
        if (index < 3) { // Логируем только первые 3 для отладки
          console.log(`Room ${index}:`, room, '->', transformed);
        }
        return transformed;
      });

      console.log('Total transformed rooms:', transformedRooms.length);
      console.log('Unique room types:', [...new Set(transformedRooms.map(r => r.room_type))]);

      return transformedRooms;
    } catch (error) {
      console.error('getRooms error:', error);
      console.error('Error details:', error.response);
      return [];
    }
  },

  getRoom: async (roomId) => {
    try {
      const response = await api.get(`rooms/${roomId}`);
      return response.data;
    } catch (error) {
      console.error('getRoom error:', error);
      throw error;
    }
  },

  updateRoom: async (roomId, data) => {
    try {
      console.log('Updating room:', roomId, data);
      const response = await api.patch(`rooms/${roomId}`, data);
      console.log('Room updated:', response.data);
      return response.data;
    } catch (error) {
      console.error('updateRoom error:', error);
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
      return response.data;
    } catch (error) {
      console.error('checkAvailability error:', error);
      throw error;
    }
  }
};