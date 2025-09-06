import { setAuthToken } from '../utils/api';

export const authService = {
  authenticate: async (initData) => {
    try {
      console.log('Authenticating with initData:', initData);

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

        // Если доступ запрещен - НЕ ДАЕМ ОБХОД
        if (response.status === 403) {
          console.error('Access denied:', errorData);
          throw {
            response: {
              status: 403,
              data: errorData
            }
          };
        }

        throw new Error(errorData.detail || 'Authentication failed');
      }

      const { token, user } = await response.json();

      // Сохраняем токен
      setAuthToken(token);
      localStorage.setItem('current_user', JSON.stringify(user));

      return { token, user };

    } catch (error) {
      console.error('Authentication error:', error);

      // НЕ СОЗДАЕМ ФЕЙКОВЫЙ ТОКЕН!
      // Пробрасываем ошибку дальше
      throw error;
    }
  },

  logout: () => {
    setAuthToken(null);
    localStorage.clear();
    sessionStorage.clear();
  }
};