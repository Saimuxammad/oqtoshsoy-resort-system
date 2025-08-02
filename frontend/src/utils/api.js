import axios from 'axios';

// Определяем базовый URL для API
const getBaseURL = () => {
  // Проверяем переменную окружения
  const envApiUrl = import.meta.env.VITE_API_URL;

  // Для Telegram WebApp
  if (window.Telegram?.WebApp) {
    // В Telegram используем прямой URL к backend
    return 'https://oqtoshsoy-resort-system-production.up.railway.app/api';
  }

  // Для production на Railway
  if (window.location.hostname.includes('railway.app')) {
    // Используем переменную окружения или fallback
    return envApiUrl ? `${envApiUrl}/api` : 'https://oqtoshsoy-resort-system-production.up.railway.app/api';
  }

  // Для локальной разработки
  if (window.location.hostname === 'localhost') {
    return 'http://localhost:8000/api';
  }

  // Fallback - используем прямой URL к backend
  return 'https://oqtoshsoy-resort-system-production.up.railway.app/api';
};

const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor для добавления токена
api.interceptors.request.use(
  (config) => {
    // Получаем токен из localStorage или из Telegram WebApp
    const token = localStorage.getItem('auth_token') ||
                  sessionStorage.getItem('auth_token') ||
                  'dev_token'; // Временный токен для разработки

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Логируем запросы для отладки
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`, {
      baseURL: config.baseURL,
      headers: config.headers,
      data: config.data
    });

    return config;
  },
  (error) => {
    console.error('[API] Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor для обработки ошибок
api.interceptors.response.use(
  (response) => {
    console.log(`[API] Response ${response.config.url}:`, response.data);
    return response;
  },
  (error) => {
    console.error('[API] Response error:', error);

    if (error.response) {
      // Сервер ответил с ошибкой
      console.error('[API] Error response:', {
        status: error.response.status,
        data: error.response.data,
        headers: error.response.headers
      });

      // Обработка специфических ошибок
      switch (error.response.status) {
        case 401:
          // Не авторизован
          console.warn('[API] Unauthorized - redirecting to auth...');
          // Здесь можно добавить редирект на страницу авторизации
          break;
        case 403:
          console.warn('[API] Forbidden - insufficient permissions');
          break;
        case 404:
          console.warn('[API] Not found');
          break;
        case 500:
          console.error('[API] Internal server error');
          break;
      }
    } else if (error.request) {
      // Запрос был отправлен, но ответ не получен
      console.error('[API] No response received:', error.request);

      // Проверяем, является ли это CORS ошибкой
      if (error.message === 'Network Error') {
        console.error('[API] Possible CORS issue or server is down');
      }
    } else {
      // Что-то произошло при настройке запроса
      console.error('[API] Request setup error:', error.message);
    }

    return Promise.reject(error);
  }
);

// Функция для обновления токена
export const setAuthToken = (token) => {
  if (token) {
    localStorage.setItem('auth_token', token);
    sessionStorage.setItem('auth_token', token);
  } else {
    localStorage.removeItem('auth_token');
    sessionStorage.removeItem('auth_token');
  }
};

// Экспортируем настроенный экземпляр axios
export default api;