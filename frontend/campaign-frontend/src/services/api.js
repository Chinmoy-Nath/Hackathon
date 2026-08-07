import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: (email, password) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    return api.post('/auth/login', formData, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } });
  },
  getMe: () => api.get('/auth/me'),
};

export const campaignAPI = {
  list: (params) => api.get('/campaigns', { params }),
  get: (id) => api.get(`/campaigns/${id}`),
  create: (data) => api.post('/campaigns', data),
  execute: (id) => api.post(`/campaigns/${id}/execute`),
  getAnalytics: (id) => api.get(`/campaigns/${id}/analytics`),
  getContent: (id) => api.get(`/campaigns/${id}/content`),
  updateStatus: (id, status) => api.patch(`/campaigns/${id}/status`, { status }),
  parseRequest: (userInput) => api.post('/campaigns/parse-request', { user_input: userInput }),
};

export const customerAPI = {
  list: (params) => api.get('/customers', { params }),
  getProfile: (id) => api.get(`/customers/${id}/profile`),
  getRecommendation: (id) => api.get(`/customers/${id}/recommendation`),
  getSegmentSummary: () => api.get('/customers/segments/summary'),
};

export const analyticsAPI = {
  getCampaignManagerDashboard: () => api.get('/analytics/dashboard/campaign-manager'),
  getRetailManagerDashboard: () => api.get('/analytics/dashboard/retail-manager'),
  getFunnel: (campaignId) => api.get(`/analytics/campaigns/${campaignId}/funnel`),
  getROI: (campaignId) => api.get(`/analytics/campaigns/${campaignId}/roi`),
  getDealerPerformance: () => api.get('/analytics/dealer-performance'),
  getVehicleSegments: () => api.get('/analytics/vehicle-segments'),
};

export const vehicleAPI = {
  list: (params) => api.get('/vehicles', { params }),
  get: (id) => api.get(`/vehicles/${id}`),
};

export default api;
