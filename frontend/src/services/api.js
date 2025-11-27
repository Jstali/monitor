import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3232/api';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear token and redirect to login if unauthorized
      localStorage.removeItem('token');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  register: (data) => api.post('/auth/register', data),
  getCurrentUser: () => api.get('/auth/me'),
};

// Organization API
export const organizationAPI = {
  getAll: () => api.get('/organizations'),
  getById: (id) => api.get(`/organizations/${id}`),
  update: (id, data) => api.put(`/organizations/${id}`, data),
  getEmployees: (id) => api.get(`/organizations/${id}/employees`),
};

// Employee API
export const employeeAPI = {
  getProfile: () => api.get('/employees/me'),
  updateProfile: (data) => api.put('/employees/me', data),
  getById: (id) => api.get(`/employees/${id}`),
  update: (id, data) => api.put(`/employees/${id}`, data),
  assignManager: (employeeId, managerId) => api.put(`/employees/${employeeId}/assign-manager`, { manager_id: managerId }),
};

// Monitoring API
export const monitoringAPI = {
  startSession: (credentials) => api.post('/monitoring/sessions/start', credentials || {}),
  stopSession: () => api.post('/monitoring/sessions/stop'),
  getCurrentSession: () => api.get('/monitoring/sessions/current'),
  getSessions: (params) => api.get('/monitoring/sessions', { params }),
  logActivity: (data) => api.post('/monitoring/activities', data),
  getActivities: (sessionId) => api.get('/monitoring/activities', { params: { session_id: sessionId } }),
  getAgentCredentials: () => api.get('/monitoring/agent/credentials'),
  updateAgentCredentials: (credentials) => api.put('/monitoring/agent/credentials', credentials),
  getCredentialsStatus: () => api.get('/monitoring/agent/credentials/status'),
};

// Screenshot API
export const screenshotAPI = {
  upload: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/screenshots/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  getById: (id) => api.get(`/screenshots/${id}`),
  getFile: (id) => api.get(`/screenshots/${id}/file`, { responseType: 'blob' }),
  extractData: (id) => api.post(`/screenshots/${id}/extract`),
  extractBatch: (screenshot_ids) => api.post('/screenshots/extract/batch', { screenshot_ids }),
  getSessionScreenshots: (sessionId) => api.get(`/screenshots/session/${sessionId}`),
};

// Workflow API
export const workflowAPI = {
  getSessionDiagram: (sessionId, format = 'json') => 
    api.get(`/workflow/session/${sessionId}/diagram`, { 
      params: { format },
      responseType: format === 'json' ? 'json' : 'blob' 
    }),
  getEmployeeDiagram: (employeeId, format = 'json') => 
    api.get(`/workflow/employee/${employeeId}/diagram`, { 
      params: { format },
      responseType: format === 'json' ? 'json' : 'blob' 
    }),
};

export default api;
