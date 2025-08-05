import api from './api';

export const roomService = {
  getRooms: async (filters = {}) => {
    try {
      const response = await api.get('rooms');
      console.log('Raw API response:', response);

      let rooms = [];

      // Обрабатываем разные возможные структуры ответа
      if (Array.isArray(response.data)) {
        // Если это массив
        if (response.data.length > 0) {
          // Проверяем, является ли первый элемент комнатой или контейнером
          const firstItem = response.data[0];

          if (firstItem.room_number && firstItem.room_type) {
            // Это массив комнат
            rooms = response.data;
          } else if (Array.isArray(firstItem)) {
            // Это массив массивов
            rooms = firstItem;
          } else if (typeof firstItem === 'object') {
            // Это массив с одним объектом-контейнером
            // Пробуем найти массив комнат внутри
            const possibleKeys = ['rooms', 'data', 'items', 'results'];
            for (const key of possibleKeys) {
              if (Array.isArray(firstItem[key])) {
                rooms = firstItem[key];
                break;
              }
            }

            // Если не нашли, берем все значения, которые являются массивами
            if (rooms.length === 0) {
              for (const value of Object.values(firstItem)) {
                if (Array.isArray(value) && value.length > 0 && value[0].room_number) {
                  rooms = value;
                  break;
                }
              }
            }
          }
        }
      } else if (response.data && typeof response.data === 'object') {
        // Если это объект, ищем массив комнат внутри
        if (Array.isArray(response.data.rooms)) {
          rooms = response.data.rooms;
        } else if (Array.isArray(response.data.data)) {
          rooms = response.data.data;
        }
      }

      console.log('Extracted rooms:', rooms.length);

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

      const transformedRooms = rooms.map((room, index) => {
        const transformed = {
          ...room,
          room_type: roomTypeMap[room.room_type] || room.room_type
        };
        if (index < 3) {
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