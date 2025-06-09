import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds for file uploads
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API functions
export const authAPI = {
  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },
  
  register: async (username: string, email: string, password: string, role: string = 'user') => {
    const response = await api.post('/auth/register', { username, email, password, role });
    return response.data;
  },
};

export const contractsAPI = {
  upload: async (file: File, userId?: number) => {
    const formData = new FormData();
    formData.append('file', file);
    if (userId) formData.append('user_id', userId.toString());
    
    const response = await api.post('/contracts/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  getAll: async (userId?: number) => {
    const response = await api.get('/contracts', {
      params: userId ? { user_id: userId } : {},
    });
    return response.data;
  },
  
  getById: async (contractId: number) => {
    const response = await api.get(`/contracts/${contractId}`);
    return response.data;
  },
  
  delete: async (contractId: number) => {
    const response = await api.delete(`/contracts/${contractId}`);
    return response.data;
  },
};

export const summariesAPI = {
  generate: async (contractId: number, type: 'brief' | 'standard' | 'detailed' = 'standard') => {
    const response = await api.post(`/summaries/generate/${contractId}`, { type });
    return response.data;
  },
  
  getById: async (summaryId: number) => {
    const response = await api.get(`/summaries/${summaryId}`);
    return response.data;
  },
  
  getByContract: async (contractId: number) => {
    const response = await api.get(`/summaries/contract/${contractId}`);
    return response.data;
  },
  
  approve: async (summaryId: number) => {
    const response = await api.put(`/summaries/${summaryId}/approve`);
    return response.data;
  },
  
  submitFeedback: async (summaryId: number, feedback: string, rating: number) => {
    const response = await api.post(`/summaries/${summaryId}/feedback`, { feedback, rating });
    return response.data;
  },
};

export default api;
