/**
 * API Client Configuration
 * Centralized API communication with authentication and error handling
 */

import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import Cookies from 'js-cookie';

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
const TOKEN_KEY = 'auth_token';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token management
export const authUtils = {
  getToken: (): string | null => {
    if (typeof window === 'undefined') return null;
    return Cookies.get(TOKEN_KEY) || localStorage.getItem(TOKEN_KEY);
  },
  
  setToken: (token: string): void => {
    Cookies.set(TOKEN_KEY, token, { expires: 7, secure: process.env.NODE_ENV === 'production' });
    localStorage.setItem(TOKEN_KEY, token);
  },
  
  removeToken: (): void => {
    Cookies.remove(TOKEN_KEY);
    localStorage.removeItem(TOKEN_KEY);
  },
  
  isAuthenticated: (): boolean => {
    return !!authUtils.getToken();
  }
};

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = authUtils.getToken();
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      authUtils.removeToken();
      if (typeof window !== 'undefined') {
        window.location.href = '/auth/login';
      }
    }
    return Promise.reject(error);
  }
);

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: number;
}

export interface PaginatedResponse<T> {
  results: T[];
  count: number;
  next?: string;
  previous?: string;
  page?: number;
  page_size?: number;
  total_pages?: number;
}

export interface ApiError {
  message: string;
  errors?: Record<string, string[]>;
  status?: number;
}

// Generic API methods
export const api = {
  get: <T>(url: string, params?: any): Promise<T> =>
    apiClient.get(url, { params }).then(response => response.data),
  
  post: <T>(url: string, data?: any): Promise<T> =>
    apiClient.post(url, data).then(response => response.data),
  
  put: <T>(url: string, data?: any): Promise<T> =>
    apiClient.put(url, data).then(response => response.data),
  
  patch: <T>(url: string, data?: any): Promise<T> =>
    apiClient.patch(url, data).then(response => response.data),
  
  delete: <T>(url: string): Promise<T> =>
    apiClient.delete(url).then(response => response.data),
};

export default apiClient;
