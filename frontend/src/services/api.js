import axios from 'axios';

// ⛳ Устанавливаем HTTPS базовый URL, если в продакшене
const API_BASE_URL = import.meta.env.MODE === 'production'
  ? 'https://oqtoshsoy-resort-system-production.up.railway.app/api'
  : (import.meta.env.VITE_API_URL || 'http://localhost:8000/api');

console.log('🌍 Среда:', import.meta.env.MODE);
console.log('🔗 Базовый URL:', API_BASE_URL);

// ⚙️ Создаём экземпляр axios
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 🔐 Авторизация: добавляем токен к каждому запросу
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  console.log('📡 Запрос:', config.method?.toUpperCase(), config.url);
  return config;
});

// 📥 Обработка ответов и ошибок
api.interceptors.response.use(
  (response) => {
    console.log('✅ Ответ:', response.config.url, response.status);
    return response;
  },
  (error) => {
    console.error('❌ Ошибка API:', {
      url: error.config?.url,
      status: error.response?.status,
      data: error.response?.data,
      message: error.message
    });

    // 🔁 Обработка 401: сброс токена и перезагрузка
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      if (import.meta.env.MODE === 'production') {
        window.location.reload();
      }
    }

    return Promise.reject(error);
  }
);

export default api;
