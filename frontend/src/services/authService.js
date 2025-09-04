import api from './api';

export const authService = {
  authenticate: async (initData) => {
    try {
      console.log('Authenticating with initData:', initData);

      // Для Telegram WebApp
      if (initData) {
        const response = await api.post('/auth/telegram', { initData });
        const { token, user } = response.data;

        // Сохраняем токен
        if (token) {
          localStorage.setItem('auth_token', token);
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        }

        return { token, user };
      }

      // Для dev режима (без Telegram)
      console.log('Dev mode - using mock auth');
      const mockUser = {
        id: 1,
        telegram_id: 5488749868,
        first_name: 'Dev',
        last_name: 'User',
        is_admin: true,
        can_modify: true
      };

      return {
        token: 'dev_token',
        user: mockUser
      };
    } catch (error) {
      console.error('Authentication error:', error);

      // Возвращаем тестового пользователя при ошибке
      const fallbackUser = {
        id: 1,
        telegram_id: 5488749868,
        first_name: 'Guest',
        last_name: 'User',
        is_admin: false,
        can_modify: false
      };

      return {
        token: 'fallback_token',
        user: fallbackUser
      };
    }
  },

  logout: () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('current_user');
    sessionStorage.clear();
  },

  getCurrentUser: () => {
    const savedUser = localStorage.getItem('current_user');
    if (savedUser) {
      try {
        return JSON.parse(savedUser);
      } catch (e) {
        console.error('Error parsing saved user:', e);
      }
    }
    return null;
  }
};