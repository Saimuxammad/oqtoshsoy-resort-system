import axios from 'axios';

// ВРЕМЕННОЕ РЕШЕНИЕ - используем только HTTPS URL
const API_BASE_URL = 'https://oqtoshsoy-resort-system-production.up.railway.app/api';

console.log('API_BASE_URL:', API_BASE_URL);

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
  console.log('API Request:', config.method?.toUpperCase(), config.url);
  return config;
});

// Handle responses and errors
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.config.url, response.status);
    console.log('Response data:', response.data);
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