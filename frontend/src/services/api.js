// frontend/src/services/api.js или frontend/src/utils/api.js
import axios from 'axios';

const API_URL = 'https://oqtoshsoy-resort-system-production-ef7c.up.railway.app/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Добавляем токен к каждому запросу
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Обработка ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Если токен недействителен, очищаем локальное хранилище
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');

      // Можно добавить перенаправление на страницу входа
      // window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Функция для установки токена
export const setAuthToken = (token) => {
  if (token) {
    localStorage.setItem('auth_token', token);
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    localStorage.removeItem('auth_token');
    delete api.defaults.headers.common['Authorization'];
  }
};

// Проверка авторизации при загрузке
const savedToken = localStorage.getItem('auth_token');
if (savedToken) {
  setAuthToken(savedToken);
}

export default api;