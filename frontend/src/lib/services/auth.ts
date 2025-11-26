/**
 * Authentication API Services
 */

import { api } from '../api';
import {
  User,
  UserProfile,
  Address,
  LoginRequest,
  RegisterRequest,
  AuthResponse,
} from '../../types/api';

export const authService = {
  // Authentication
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    return api.post('/accounts/login/', credentials);
  },

  register: async (userData: RegisterRequest): Promise<AuthResponse> => {
    return api.post('/accounts/register/', userData);
  },

  logout: async (): Promise<{ message: string }> => {
    return api.post('/accounts/logout/');
  },

  // User profile
  getCurrentUser: async (): Promise<User> => {
    return api.get('/accounts/current-user/');
  },

  getUserProfile: async (): Promise<User> => {
    return api.get('/accounts/profile/');
  },

  updateUserProfile: async (data: Partial<User>): Promise<User> => {
    return api.patch('/accounts/profile/', data);
  },

  // Extended profile
  getProfileDetails: async (): Promise<UserProfile> => {
    return api.get('/accounts/profile/details/');
  },

  updateProfileDetails: async (data: Partial<UserProfile>): Promise<UserProfile> => {
    return api.patch('/accounts/profile/details/', data);
  },

  // Password management
  changePassword: async (data: {
    old_password: string;
    new_password: string;
    new_password_confirm: string;
  }): Promise<{ message: string }> => {
    return api.post('/accounts/password/change/', data);
  },

  // Address management
  getAddresses: async (): Promise<Address[]> => {
    return api.get('/accounts/addresses/');
  },

  createAddress: async (data: Omit<Address, 'id' | 'full_address' | 'created_at' | 'updated_at'>): Promise<Address> => {
    return api.post('/accounts/addresses/', data);
  },

  getAddress: async (id: number): Promise<Address> => {
    return api.get(`/accounts/addresses/${id}/`);
  },

  updateAddress: async (id: number, data: Partial<Address>): Promise<Address> => {
    return api.patch(`/accounts/addresses/${id}/`, data);
  },

  deleteAddress: async (id: number): Promise<void> => {
    return api.delete(`/accounts/addresses/${id}/`);
  },

  // Email verification
  sendEmailVerification: async (): Promise<{ message: string }> => {
    return api.post('/accounts/verify-email/send/');
  },

  verifyEmail: async (token: string): Promise<{ message: string }> => {
    return api.get(`/accounts/verify-email/?token=${token}`);
  },
};
