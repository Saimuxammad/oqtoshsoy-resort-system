import axios from 'axios';

// Правильная конфигурация URL
const API_BASE_URL = import.meta.env.VITE_API_URL ||
  (import.meta.env.PROD
    ? 'https://oqtoshsoy-resort-system-production.up.railway.app/api'
    : 'http://localhost:8000/api');

console.log('API Configuration:', {
  VITE_API_URL: import.meta.env.VITE_API_URL,
  MODE: import.meta.env.MODE,
  PROD: import.meta.env.PROD,
  API_BASE_URL: API_BASE_URL
});

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  console.log('API Request:', {
    method: config.method?.toUpperCase(),
    url: config.url,
    baseURL: config.baseURL,
    fullURL: config.baseURL + config.url
  });
  return config;
});

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', {
      url: response.config.url,
      status: response.status,
      data: response.data
    });
    return response;
  },
  (error) => {
    console.error('API Error:', {
      message: error.message,
      code: error.code,
      response: {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
      },
      config: {
        url: error.config?.url,
        method: error.config?.method,
        baseURL: error.config?.baseURL,
      }
    });

    // Специальная обработка для Network Error
    if (error.code === 'ERR_NETWORK') {
      console.error('Network Error Details:', {
        message: 'Возможные причины:',
        reasons: [
          '1. CORS заблокирован',
          '2. Сервер недоступен',
          '3. Неправильный URL API',
          '4. Mixed content (HTTPS->HTTP)'
        ],
        currentURL: API_BASE_URL
      });
    }

    return Promise.reject(error);
  }
);

export default api;