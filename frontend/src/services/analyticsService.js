import api from './api';

export const analyticsService = {
  getOccupancyStats: async (startDate, endDate) => {
    const params = new URLSearchParams({
      start_date: startDate.toISOString().split('T')[0],
      end_date: endDate.toISOString().split('T')[0]
    });
    const response = await api.get(`/analytics/occupancy?${params}`);
    return response.data;
  },

  getRoomTypeStats: async (startDate, endDate) => {
    const params = new URLSearchParams({
      start_date: startDate.toISOString().split('T')[0],
      end_date: endDate.toISOString().split('T')[0]
    });
    const response = await api.get(`/analytics/room-types?${params}`);
    return response.data;
  },

  getBookingTrends: async (months = 6) => {
    const response = await api.get(`/analytics/trends?months=${months}`);
    return response.data;
  },

  getUserActivity: async () => {
    const response = await api.get('/analytics/users');
    return response.data;
  },

  getRevenueForecast: async (daysAhead = 30) => {
    const response = await api.get(`/analytics/revenue-forecast?days_ahead=${daysAhead}`);
    return response.data;
  },

  exportAnalytics: async (startDate, endDate) => {
    const params = new URLSearchParams({
      start_date: startDate.toISOString().split('T')[0],
      end_date: endDate.toISOString().split('T')[0]
    });
    const response = await api.get(`/export/analytics?${params}`, {
      responseType: 'arraybuffer'
    });
    return response.data;
  }
};