import axios from 'axios';
// import { API_BASE_URL } from '../utils/constants';

// Хардкодим URL напрямую
const API_BASE_URL = 'https://oqtoshsoy-resort-system-production.up.railway.app/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

// Handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);

    if (error.response?.status === 401) {
      // Токен истек, очищаем
      localStorage.removeItem('auth_token');
      // Не перезагружаем страницу в development
      // window.location.reload();
    }

    return Promise.reject(error);
  }
);

export default api;