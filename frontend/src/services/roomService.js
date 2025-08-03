export const roomService = {
  import api from '../utils/api';

export const roomService = {
  getRooms: async (filters = {}) => {
    try {
      const response = await api.get('/rooms/list', {
        params: filters
      });
      return response.data;
    } catch (error) {
      console.error('[RoomService] getRooms error:', error);
      throw error;
    }
  },

  // 🔜 Дополнительные методы можно добавить ниже
  // getRoom: async (roomId) => { ... }
  // updateRoom: async (roomId, data) => { ... }
};


  // Get all rooms
  getRooms: async (filters = {}) => {
    try {
      const params = new URLSearchParams();
      if (filters.type) params.append('type', filters.type);
      if (filters.available !== undefined) params.append('available', filters.available);

      // Получаем токен
      const token = localStorage.getItem('auth_token') ||
                    sessionStorage.getItem('auth_token') ||
                    'dev_token';

      // Прямой URL без дублирования
      const url = `https://oqtoshsoy-resort-system-production.up.railway.app/api/rooms/list?${params}`;
      console.log('[RoomService] Fetching rooms from:', url);

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json'
        }
      });

      console.log('[RoomService] Response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('[RoomService] Error response:', errorText);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      console.log('[RoomService] Rooms loaded:', data);
      return data;

    } catch (error) {
      console.error('[RoomService] getRooms error:', error);
      throw error;
    }
  },

  // Get single room
  getRoom: async (roomId) => {
    try {
      const token = localStorage.getItem('auth_token') ||
                    sessionStorage.getItem('auth_token') ||
                    'dev_token';

      const url = `https://oqtoshsoy-resort-system-production.up.railway.app/api/rooms/${roomId}`;

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('[RoomService] getRoom error:', error);
      throw error;
    }
  },

  // Update room
  updateRoom: async (roomId, data) => {
    try {
      const token = localStorage.getItem('auth_token') ||
                    sessionStorage.getItem('auth_token') ||
                    'dev_token';

      const url = `https://oqtoshsoy-resort-system-production.up.railway.app/api/rooms/${roomId}`;

      const response = await fetch(url, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json'
        },
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('[RoomService] updateRoom error:', error);
      throw error;
    }
  }
};