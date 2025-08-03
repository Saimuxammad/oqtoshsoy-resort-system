import api, { setAuthToken } from '../utils/api';

export const authService = {
  authenticate: async (initData) => {
    try {
      console.log('Authenticating with initData:', initData);

      // Для Telegram WebApp
      if (initData) {
        const response = await api.post('/api/auth/telegram', { initData });
        const { token, user } = response.data;

        // Сохраняем токен
        setAuthToken(token);

        return { token, user };
      }

      // Для dev режима
      console.log('Dev mode - using mock auth');
      const mockToken = 'dev_token_' + Date.now();
      setAuthToken(mockToken);

      return {
        token: mockToken,
        user: {
          id: 1,
          first_name: 'Dev',
          last_name: 'User',
          is_admin: true
        }
      };
    } catch (error) {
      console.error('Authentication error:', error);

      // В случае ошибки все равно позволяем работать в dev режиме
      const fallbackToken = 'fallback_token_' + Date.now();
      setAuthToken(fallbackToken);

      return {
        token: fallbackToken,
        user: {
          id: 1,
          first_name: 'Guest',
          last_name: 'User',
          is_admin: false
        }
      };
    }
  },

  logout: () => {
    setAuthToken(null);
    localStorage.clear();
    sessionStorage.clear();
  },

  getCurrentUser: () => {
    // Получаем сохраненного пользователя
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