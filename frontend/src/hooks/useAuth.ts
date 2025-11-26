/**
 * Authentication React Query Hooks
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { authService } from '../lib/services/auth';
import { authUtils } from '../lib/api';
import {
  User,
  UserProfile,
  Address,
  LoginRequest,
  RegisterRequest,
  AuthResponse,
} from '../types/api';

// Query Keys
export const AUTH_KEYS = {
  currentUser: ['auth', 'currentUser'] as const,
  profile: ['auth', 'profile'] as const,
  profileDetails: ['auth', 'profileDetails'] as const,
  addresses: ['auth', 'addresses'] as const,
  address: (id: number) => ['auth', 'address', id] as const,
};

// Authentication Hooks
export const useLogin = () => {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: (credentials: LoginRequest) => authService.login(credentials),
    onSuccess: (data: AuthResponse) => {
      // Store auth token
      authUtils.setToken(data.token);
      
      // Cache user data
      queryClient.setQueryData(AUTH_KEYS.currentUser, data.user);
      
      // Redirect to dashboard or intended page
      router.push('/dashboard');
    },
  });
};

export const useRegister = () => {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: (userData: RegisterRequest) => authService.register(userData),
    onSuccess: (data: AuthResponse) => {
      // Store auth token
      authUtils.setToken(data.token);
      
      // Cache user data
      queryClient.setQueryData(AUTH_KEYS.currentUser, data.user);
      
      // Redirect to onboarding or dashboard
      router.push('/dashboard');
    },
  });
};

export const useLogout = () => {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: () => authService.logout(),
    onSuccess: () => {
      // Clear auth token
      authUtils.removeToken();
      
      // Clear all cached data
      queryClient.clear();
      
      // Redirect to login
      router.push('/auth/login');
    },
  });
};

// User Profile Hooks
export const useCurrentUser = () => {
  return useQuery({
    queryKey: AUTH_KEYS.currentUser,
    queryFn: authService.getCurrentUser,
    enabled: authUtils.isAuthenticated(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useUserProfile = () => {
  return useQuery({
    queryKey: AUTH_KEYS.profile,
    queryFn: authService.getUserProfile,
    enabled: authUtils.isAuthenticated(),
  });
};

export const useUpdateProfile = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Partial<User>) => authService.updateUserProfile(data),
    onSuccess: (updatedUser) => {
      // Update cached user data
      queryClient.setQueryData(AUTH_KEYS.currentUser, updatedUser);
      queryClient.setQueryData(AUTH_KEYS.profile, updatedUser);
    },
  });
};

export const useProfileDetails = () => {
  return useQuery({
    queryKey: AUTH_KEYS.profileDetails,
    queryFn: authService.getProfileDetails,
    enabled: authUtils.isAuthenticated(),
  });
};

export const useUpdateProfileDetails = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Partial<UserProfile>) => authService.updateProfileDetails(data),
    onSuccess: (updatedProfile) => {
      queryClient.setQueryData(AUTH_KEYS.profileDetails, updatedProfile);
    },
  });
};

export const useChangePassword = () => {
  return useMutation({
    mutationFn: (data: {
      old_password: string;
      new_password: string;
      new_password_confirm: string;
    }) => authService.changePassword(data),
  });
};

// Address Hooks
export const useAddresses = () => {
  return useQuery({
    queryKey: AUTH_KEYS.addresses,
    queryFn: authService.getAddresses,
    enabled: authUtils.isAuthenticated(),
  });
};

export const useAddress = (id: number) => {
  return useQuery({
    queryKey: AUTH_KEYS.address(id),
    queryFn: () => authService.getAddress(id),
    enabled: authUtils.isAuthenticated() && !!id,
  });
};

export const useCreateAddress = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Omit<Address, 'id' | 'full_address' | 'created_at' | 'updated_at'>) => 
      authService.createAddress(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: AUTH_KEYS.addresses });
    },
  });
};

export const useUpdateAddress = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Address> }) => 
      authService.updateAddress(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: AUTH_KEYS.addresses });
      queryClient.invalidateQueries({ queryKey: AUTH_KEYS.address(id) });
    },
  });
};

export const useDeleteAddress = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => authService.deleteAddress(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: AUTH_KEYS.addresses });
    },
  });
};

// Utility Hook
export const useIsAuthenticated = () => {
  const { data: user, isLoading } = useCurrentUser();
  return {
    isAuthenticated: !!user,
    user,
    isLoading,
  };
};
