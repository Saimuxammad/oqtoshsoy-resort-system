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
});

// Функция для добавления слеша в конец URL
const ensureTrailingSlash = (url) => {
  // Не добавляем слеш, если URL заканчивается на файл или уже имеет слеш
  if (url.match(/\.[a-zA-Z0-9]+$/) || url.endsWith('/')) {
    return url;
  }
  // Если URL содержит query параметры
  if (url.includes('?')) {
    const [path, query] = url.split('?');
    return `${path}/?${query}`;
  }
  return `${url}/`;
};

// Add auth token to requests and fix URLs
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }

  // Автоматически добавляем слеш в конец URL
  config.url = ensureTrailingSlash(config.url);

  console.log('API Request:', config.method?.toUpperCase(), config.url);
  return config;
});

// Handle responses and errors
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.config.url, response.status);
    return response;
  },
  (error) => {
    console.error('API Error:', {
      url: error.config?.url,
      status: error.response?.status,
      data: error.response?.data,
      message: error.message
    });

    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
    }

    return Promise.reject(error);
  }
);

export default api;