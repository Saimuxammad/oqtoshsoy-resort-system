import axios from 'axios';

// ВАЖНО: Используем HTTPS для production!
const API_BASE_URL = import.meta.env.PROD
  ? 'https://oqtoshsoy-resort-system-production.up.railway.app/api'
  : 'http://localhost:8000/api';

console.log('API_BASE_URL:', API_BASE_URL);
console.log('Environment:', import.meta.env.MODE);

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  // Добавляем timeout
  timeout: 30000,
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  console.log('API Request:', config.method?.toUpperCase(), config.url);
  console.log('Request headers:', config.headers);
  return config;
});

// Handle responses and errors
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.config.url, response.status);
    return response;
  },
  (error) => {
    console.error('API Error Details:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      message: error.message,
      code: error.code
    });

    // Специальная обработка для Network Error
    if (error.code === 'ERR_NETWORK') {
      console.error('Network Error - возможно проблема с CORS или недоступен сервер');
    }

    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      // Не перезагружаем в dev режиме
      if (import.meta.env.PROD && window.location.pathname !== '/login') {
        // window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

export default api;