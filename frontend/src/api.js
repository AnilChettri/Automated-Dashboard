import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
});

export const analyticsApi = {
  getKpis: (period = '30d') => api.get(`/analytics/kpi?period=${period}`),
  getRevenueTrend: (period = '30d') => api.get(`/analytics/revenue-trend?period=${period}`),
  getSegments: () => api.get('/analytics/segments'),
  getTopProducts: (limit = 5) => api.get(`/analytics/top-products?limit=${limit}`),
};

export const forecastApi = {
  getRevenueForecast: (horizon = 30) => api.get(`/forecast/revenue?horizon=${horizon}`),
  getStatus: () => api.get('/forecast/status'),
};

export const insightApi = {
  getLatest: () => api.get('/insights/latest'),
  rateInsight: (id, rating) => api.post(`/insights/${id}/rate?rating=${rating}`),
};

export const chatApi = {
  ask: (query) => api.post('/chat/ask', { query }),
};

export const mlApi = {
  train: () => api.post('/ml/train'),
  getStatus: () => api.get('/ml/status'),
};

export const recommendationApi = {
  getProducts: () => api.get('/recommendations/products'),
  getActions: () => api.get('/recommendations/actions'),
};

export const customerApi = {
  getList: (params = {}) => api.get('/customers', { params }),
  getDetail: (id) => api.get(`/customers/${id}`),
};

export const productApi = {
  getList: () => api.get('/products'),
};

export default api;
