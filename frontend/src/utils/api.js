import axios from 'axios';

// 🌐 Получаем базовый URL в зависимости от окружения
const getBaseURL = () => {
  const BACKEND_URL = import.meta.env.VITE_API_URL || 'https://oqtoshsoy-resort-system-production.up.railway.app';

  const isLocal = ['localhost', '127.0.0.1'].includes(window.location.hostname);

  const finalBaseURL = isLocal
    ? 'http://localhost:8000/api'
    : `${BACKEND_URL}/api`;

  console.log('[API] Mode:', import.meta.env.MODE);
  console.log('[API] Final baseURL:', finalBaseURL);

  return finalBaseURL;
};

// 📦 Инициализация axios с параметрами
const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  paramsSerializer: params =>
    new URLSearchParams(params).toString()
});

// 🔒 Интерцептор запросов — авторизация + логирование
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('auth_token') ||
                  sessionStorage.getItem('auth_token') ||
                  'dev_token';

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    console.log(`[API] Request: ${config.method?.toUpperCase()} ${config.url}`, {
      baseURL: config.baseURL,
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

// ⚠️ Интерцептор ответа — диагностика ошибок
api.interceptors.response.use(
  response => {
    console.log(`[API] Response from ${response.config.url}:`, response.data);
    return response;
  },
  error => {
    console.error('[API] Response error:', error);

    if (error.response) {
      const { status, data, headers } = error.response;
      console.warn(`[API] Status ${status}`, { data, headers });

      switch (status) {
        case 401:
          console.warn('[API] Unauthorized — maybe redirect to login');
          break;
        case 403:
          console.warn('[API] Forbidden — no access rights');
          break;
        case 404:
          console.warn('[API] Endpoint not found');
          break;
        case 500:
          console.error('[API] Server error');
          break;
      }
    } else if (error.request) {
      console.error('[API] No response received. Is server reachable?');
    } else {
      console.error('[API] Setup error:', error.message);
    }

    return Promise.reject(error);
  }
);

// 🔄 Функция для установки токена
export const setAuthToken = (token) => {
  const storage = [localStorage, sessionStorage];
  storage.forEach(store => {
    if (token) store.setItem('auth_token', token);
    else store.removeItem('auth_token');
  });
};

// 📤 Экспорт API
export default api;