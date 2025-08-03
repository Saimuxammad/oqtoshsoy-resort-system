import api from './api';

export const analyticsService = {
  getOccupancyStats: async (startDate, endDate) => {
    const params = new URLSearchParams({
      start_date: startDate.toISOString().split('T')[0],
      end_date: endDate.toISOString().split('T')[0]
    });
    const response = await api.get(`/api/analytics/occupancy?${params}`);
    return response.data;
  },

  getRoomTypeStats: async (startDate, endDate) => {
    const params = new URLSearchParams({
      start_date: startDate.toISOString().split('T')[0],
      end_date: endDate.toISOString().split('T')[0]
    });
    const response = await api.get(`/api/analytics/room-types?${params}`);
    return response.data;
  },

  getBookingTrends: async (months = 6) => {
    const response = await api.get(`/api/analytics/trends?months=${months}`);
    return response.data;
  },

  getUserActivity: async () => {
    const response = await api.get('/api/analytics/users');
    return response.data;
  },

  getRevenueForecast: async (daysAhead = 30) => {
    const response = await api.get(`/api/analytics/revenue-forecast?days_ahead=${daysAhead}`);
    return response.data;
  },

  exportAnalytics: async (startDate, endDate) => {
    const params = new URLSearchParams({
      start_date: startDate.toISOString().split('T')[0],
      end_date: endDate.toISOString().split('T')[0]
    });
    const response = await api.get(`/api/export/analytics?${params}`, {
      responseType: 'arraybuffer'
    });
    return response.data;
  }
};