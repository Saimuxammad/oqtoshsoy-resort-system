import api from './api';

export const bookingService = {
  // Get all bookings
  getBookings: async (filters = {}) => {
    try {
      const params = new URLSearchParams();
      if (filters.roomId) params.append('room_id', filters.roomId);
      if (filters.startDate) params.append('start_date', filters.startDate);
      if (filters.endDate) params.append('end_date', filters.endDate);

      const response = await api.get(`/bookings?${params}`);
      console.log('Bookings loaded:', response.data);
      return response.data;
    } catch (error) {
      console.error('getBookings error:', error);
      throw error;
    }
  },

  // Get single booking
  getBooking: async (bookingId) => {
    try {
      const response = await api.get(`/bookings/${bookingId}`);
      return response.data;
    } catch (error) {
      console.error('getBooking error:', error);
      throw error;
    }
  },

  // Create booking
  createBooking: async (booking) => {
    try {
      console.log('Creating booking:', booking);
      const response = await api.post('/bookings', booking);
      console.log('Booking created:', response.data);
      return response.data;
    } catch (error) {
      console.error('createBooking error:', error);
      throw error;
    }
  },

  // Update booking - используем PUT вместо PATCH
  updateBooking: async (bookingId, data) => {
    try {
      console.log('[BookingService] Updating booking:', bookingId, data);

      // Получаем токен
      const token = localStorage.getItem('auth_token') ||
                    sessionStorage.getItem('auth_token') ||
                    'dev_token';

      // Базовый URL
      const baseUrl = 'https://oqtoshsoy-resort-system-production.up.railway.app/api';
      const url = `${baseUrl}/bookings/${bookingId}`;

      console.log('[BookingService] UPDATE URL:', url);
      console.log('[BookingService] Update data:', data);

      // Пробуем сначала PATCH
      let response = await fetch(url, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json'
        },
        body: JSON.stringify(data)
      });

      // Если PATCH не поддерживается, пробуем PUT
      if (response.status === 405) {
        console.log('[BookingService] PATCH not allowed, trying PUT...');
        response = await fetch(url, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/json'
          },
          body: JSON.stringify(data)
        });
      }

      console.log('[BookingService] Update response:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('[BookingService] Update error:', errorText);

        let errorData;
        try {
          errorData = JSON.parse(errorText);
        } catch (e) {
          errorData = { detail: errorText || `HTTP ${response.status}` };
        }

        const error = new Error(errorData.detail || 'Update failed');
        error.response = {
          status: response.status,
          data: errorData
        };
        throw error;
      }

      const result = await response.json();
      console.log('[BookingService] Booking updated:', result);
      return result;

    } catch (error) {
      console.error('[BookingService] updateBooking error:', error);
      throw error;
    }
  },

  // Delete booking - улучшенная версия с детальным логированием
  deleteBooking: async (bookingId) => {
    try {
      console.log('[BookingService] Starting delete for booking:', bookingId);

      // Получаем токен
      const token = localStorage.getItem('auth_token') ||
                    sessionStorage.getItem('auth_token') ||
                    'dev_token';

      // Базовый URL без trailing slash
      const baseUrl = 'https://oqtoshsoy-resort-system-production.up.railway.app/api';
      const url = `${baseUrl}/bookings/${bookingId}`;

      console.log('[BookingService] DELETE URL:', url);
      console.log('[BookingService] Token:', token ? `${token.substring(0, 20)}...` : 'none');
      console.log('[BookingService] Current location:', window.location.href);

      const response = await fetch(url, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json',
          'Origin': window.location.origin
        },
        mode: 'cors',
        credentials: 'include'
      });

      console.log('[BookingService] Response received:');
      console.log('  Status:', response.status);
      console.log('  Status Text:', response.statusText);
      console.log('  OK:', response.ok);
      console.log('  Headers:', Object.fromEntries(response.headers.entries()));

      // Читаем тело ответа
      const responseText = await response.text();
      console.log('[BookingService] Response body:', responseText);

      if (!response.ok) {
        // Пробуем парсить как JSON
        let errorData;
        try {
          errorData = JSON.parse(responseText);
          console.error('[BookingService] Error data:', errorData);
        } catch (e) {
          errorData = { detail: responseText || `HTTP ${response.status}: ${response.statusText}` };
        }

        // Создаем ошибку в формате, который ожидают компоненты
        const error = new Error(errorData.detail || 'Delete failed');
        error.response = {
          status: response.status,
          statusText: response.statusText,
          data: errorData
        };
        throw error;
      }

      // Парсим успешный ответ
      let data;
      if (responseText) {
        try {
          data = JSON.parse(responseText);
        } catch (e) {
          // Если не JSON, возвращаем как есть
          data = { message: responseText || 'Deleted successfully' };
        }
      } else {
        data = { message: 'Deleted successfully' };
      }

      console.log('[BookingService] Delete successful:', data);
      return data;

    } catch (error) {
      console.error('[BookingService] Delete error:', error);
      console.error('[BookingService] Error stack:', error.stack);

      // Если error.response уже есть, просто пробрасываем
      if (error.response) {
        throw error;
      }

      // Иначе создаем структуру ошибки
      const wrappedError = new Error(error.message);
      wrappedError.response = {
        status: 0,
        statusText: 'Network Error',
        data: {
          detail: error.message || 'Network error occurred'
        }
      };
      throw wrappedError;
    }
  },

  // Проверка доступности номера для бронирования
  checkAvailability: async (roomId, startDate, endDate, excludeBookingId = null) => {
    try {
      const params = new URLSearchParams({
        room_id: roomId,
        start_date: startDate,
        end_date: endDate
      });

      if (excludeBookingId) {
        params.append('exclude_booking_id', excludeBookingId);
      }

      const response = await api.get(`/bookings/check-availability?${params}`);
      return response.data;
    } catch (error) {
      console.error('checkAvailability error:', error);
      throw error;
    }
  }
};