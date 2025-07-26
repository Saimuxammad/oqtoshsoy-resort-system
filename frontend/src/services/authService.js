import api from './api';

export const authService = {
  authenticate: async (initData) => {
    // Для разработки
    if (!initData || initData === '') {
      const mockAuthData = {
        id: 123456789,
        first_name: 'Test',
        last_name: 'User',
        username: 'testuser',
        auth_date: Math.floor(Date.now() / 1000),
        hash: 'development'
      };

      try {
        const response = await api.post('/auth/telegram', mockAuthData);
        // Сохраняем токен
        if (response.data.access_token) {
          localStorage.setItem('auth_token', response.data.access_token);
        }
        return response.data;
      } catch (error) {
        console.error('Auth error:', error);
        throw error;
      }
    }

    // Production код...
  },

  getToken: () => {
    return localStorage.getItem('auth_token');
  },

  logout: () => {
    localStorage.removeItem('auth_token');
  }
};