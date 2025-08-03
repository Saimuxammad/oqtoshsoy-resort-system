import api from './api';

export const historyService = {
  getEntityHistory: async (entityType, entityId, limit = 50) => {
    const response = await api.get(`/api/history/entity/${entityType}/${entityId}?limit=${limit}`);
    return response.data;
  },

  getUserHistory: async (userId, limit = 50) => {
    const response = await api.get(`/api/history/user/${userId}?limit=${limit}`);
    return response.data;
  },

  getRecentHistory: async (hours = 24, limit = 100) => {
    const response = await api.get(`/api/history/recent?hours=${hours}&limit=${limit}`);
    return response.data;
  }
};