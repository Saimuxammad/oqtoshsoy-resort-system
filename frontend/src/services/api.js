import axios from 'axios';

// Получаем базовый URL в зависимости от окружения
const getBaseURL = () => {
  // Определяем backend URL
  const BACKEND_URL = 'https://oqtoshsoy-resort-system-production.up.railway.app';

  // Проверяем, локальная ли это разработка
  const isLocal = ['localhost', '127.0.0.1'].includes(window.location.hostname);

  // Для production используем прямой URL с /api
  const finalBaseURL = isLocal
    ? 'http://localhost:8000/api/'  // Добавляем слеш в конце
    : `${BACKEND_URL}/api/`;         // Добавляем слеш в конце

  console.log('[API] Environment:', isLocal ? 'local' : 'production');
  console.log('[API] Backend URL:', finalBaseURL);

  return finalBaseURL;
};

// Инициализация axios с параметрами
const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  withCredentials: false, // Отключаем credentials для CORS
});

// Интерцептор запросов — авторизация + логирование
api.interceptors.request.use(
  config => {
    // Получаем токен из localStorage или sessionStorage
    const token = localStorage.getItem('auth_token') ||
                  sessionStorage.getItem('auth_token');

    // В dev режиме используем dev_token если нет реального
    if (!token && window.location.hostname === 'localhost') {
      config.headers.Authorization = 'Bearer dev_token';
    } else if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Логируем полный URL
    const fullURL = config.baseURL + (config.url || '');
    console.log(`[API] ${config.method?.toUpperCase()} ${fullURL}`, {
      headers: config.headers,
      params: config.params,
      data: config.data
    });

    return config;
  },
  error => {
    console.error('[API] Request error:', error);
    return Promise.reject(error);
  }
);

// Интерцептор ответа — диагностика ошибок
api.interceptors.response.use(
  response => {
    console.log(`[API] Response from ${response.config.url}:`, {
      status: response.status,
      data: response.data
    });
    return response;
  },
  error => {
    console.error('[API] Response error:', error);

    if (error.response) {
      const { status, data, config } = error.response;
      console.error(`[API] Error ${status} from ${config.url}:`, {
        data,
        fullURL: config.baseURL + config.url
      });

      // Специальная обработка различных кодов ошибок
      switch (status) {
        case 401:
          console.warn('[API] Unauthorized - token might be invalid');
          break;
        case 403:
          console.warn('[API] Forbidden - no access rights');
          break;
        case 404:
          console.warn('[API] Endpoint not found:', config.baseURL + config.url);
          break;
        case 500:
          console.error('[API] Server error');
          break;
      }
    } else if (error.request) {
      console.error('[API] No response received. Network error or server is down');
      console.error('[API] Request:', error.request);
    } else {
      console.error('[API] Setup error:', error.message);
    }

    return Promise.reject(error);
  }
);

// Функция для установки токена
export const setAuthToken = (token) => {
  if (token) {
    localStorage.setItem('auth_token', token);
    sessionStorage.setItem('auth_token', token);
  } else {
    localStorage.removeItem('auth_token');
    sessionStorage.removeItem('auth_token');
  }
};

// Функция для проверки доступности API
export const checkAPIHealth = async () => {
  try {
    const response = await api.get('/test');
    console.log('[API] Health check passed:', response.data);
    return true;
  } catch (error) {
    console.error('[API] Health check failed:', error);
    return false;
  }
};

// Экспорт API
export default api;