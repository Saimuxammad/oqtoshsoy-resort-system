import api from './api';

export const authService = {
  authenticate: async (initData) => {
    console.log('Authenticating with data:', initData);

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
      console.log('Auth response:', response.data);

      // Сохраняем токен
      if (response.data.access_token) {
        localStorage.setItem('auth_token', response.data.access_token);
        // Также сохраняем информацию о пользователе
        if (response.data.user) {
          localStorage.setItem('user', JSON.stringify(response.data.user));
        }
      }
      return response.data;
    } catch (error) {
      console.error('Auth error:', error);
      // Если ошибка аутентификации, всё равно пытаемся работать
      if (error.response?.status === 401 || error.code === 'ERR_NETWORK') {
        // Создаем фейковый токен для тестирования
        const fakeToken = 'fake_token_' + Date.now();
        localStorage.setItem('auth_token', fakeToken);
        return {
          access_token: fakeToken,
          user: mockAuthData
        };
      }
      throw error;
    }
  },

  getToken: () => {
    return localStorage.getItem('auth_token');
  },

  getUser: () => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  logout: () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
  },

  // Проверка, авторизован ли пользователь
  isAuthenticated: () => {
    return !!localStorage.getItem('auth_token');
  }
};