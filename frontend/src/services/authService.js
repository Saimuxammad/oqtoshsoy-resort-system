import { setAuthToken } from '../utils/api';

export const authService = {
  authenticate: async (initData) => {
    try {
      console.log('Authenticating with initData:', initData);

      // Для Telegram WebApp
      if (initData) {
        const url = 'https://oqtoshsoy-resort-system-production.up.railway.app/api/auth/telegram';

        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify({ initData })
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw { response: { status: response.status, data: errorData } };
        }

        const { token, user } = await response.json();

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

      // Пробрасываем ошибку 403
      if (error.response?.status === 403) {
        throw error;
      }

      // В случае других ошибок все равно позволяем работать в dev режиме
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