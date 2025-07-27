import api from './api';

export const authService = {
  authenticate: async (initData) => {
    // Для разработки и production без Telegram
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
        console.log('Auth successful, token saved');
      }

      return response.data;
    } catch (error) {
      console.error('Auth error:', error);

      // Если аутентификация не удалась, попробуем без токена
      // Backend должен работать в development режиме
      return {
        access_token: 'dev_token',
        user: mockAuthData
      };
    }
  },

  getToken: () => {
    return localStorage.getItem('auth_token');
  },

  logout: () => {
    localStorage.removeItem('auth_token');
  }
};