import axios, { AxiosInstance, AxiosError } from 'axios';

// API Base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    // Only access localStorage on client side
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      // Token expired, try to refresh
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          
          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);
          
          // Retry original request
          if (error.config) {
            error.config.headers.Authorization = `Bearer ${access_token}`;
            return axios(error.config);
          }
        }
      } catch (refreshError) {
        // Refresh failed, logout user
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// API Methods
export const authAPI = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  
  register: (email: string, password: string, full_name: string) =>
    api.post('/auth/register', { email, password, full_name }),
  
  refresh: (refreshToken: string) =>
    api.post('/auth/refresh', { refresh_token: refreshToken }),
};

export const modelsAPI = {
  getAll: () => api.get('/models/'),
  
  getById: (id: string) => api.get(`/models/${id}`),
  
  getMetrics: (id: string) => api.get(`/models/${id}/metrics`),
  
  getLeaderboard: () => api.get('/models/leaderboard/performance'),
  
  getComparison: (modelIds: string[]) =>
    api.get('/models/leaderboard/comparison', { params: { model_ids: modelIds } }),
  
  train: (data: {
    name: string;
    model_type: string;
    dataset_id: string;
    optimize?: boolean;
    hyperparameters?: Record<string, any>;
  }) => api.post('/models/train', data),
};

export const datasetsAPI = {
  getAll: () => api.get('/datasets/'),
  
  getById: (id: string) => api.get(`/datasets/${id}`),
  
  downloadIEEE: () => api.post('/datasets/download-ieee-cis'),
  
  preprocess: (id: string, applySampling: boolean = true) =>
    api.post(`/datasets/${id}/preprocess`, { apply_sampling: applySampling }),
  
  getStatistics: (id: string) => api.get(`/datasets/${id}/statistics`),
};

export const explanationsAPI = {
  generate: (model_id: string, method: string = 'shap', config: Record<string, any> = {}) => 
    api.post('/explanations/generate', null, { 
      params: { model_id, method, config: JSON.stringify(config) } 
    }),
  
  generateLocal: (data: { model_id: string; sample_index: number; method?: string }) =>
    api.post('/explanations/local', data),
  
  getById: (id: string) => api.get(`/explanations/${id}`),
  
  getByModel: (modelId: string) => api.get(`/explanations/model/${modelId}`),
  
  compare: (modelId: string) => api.get(`/explanations/compare/${modelId}`),
  
  evaluateQuality: (explanationId: string) => 
    api.post(`/explanations/evaluate-quality/${explanationId}`),
  
  getQuality: (evalId: string) => api.get(`/explanations/quality/${evalId}`),
};

export const benchmarksAPI = {
  getAll: () => api.get('/benchmarks/'),
  
  compare: (params?: { dataset_ids?: string; model_types?: string; metric?: string }) =>
    api.get('/benchmarks/compare', { params }),
  
  getLeaderboard: (metric: string = 'auc_roc', limit: number = 10) =>
    api.get('/benchmarks/leaderboard', { params: { metric, limit } }),
};

export default api;
