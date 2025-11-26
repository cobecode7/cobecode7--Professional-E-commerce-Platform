/**
 * Authentication Context Provider
 * Manages authentication state across the application
 */

'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { useCurrentUser, useLogin, useRegister, useLogout } from '../hooks/useAuth';
import { User, LoginRequest, RegisterRequest } from '../types/api';
import { authUtils } from '../lib/api';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  checkAuth: () => void;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isInitialized, setIsInitialized] = useState(false);
  
  // Use the React Query hooks for user data
  const { 
    data: user, 
    isLoading: userLoading, 
    refetch: refetchUser 
  } = useCurrentUser();

  // Use the authentication mutations
  const loginMutation = useLogin();
  const registerMutation = useRegister();
  const logoutMutation = useLogout();

  const isAuthenticated = authUtils.isAuthenticated() && !!user;
  const isLoading = userLoading || !isInitialized || loginMutation.isPending || registerMutation.isPending || logoutMutation.isPending;

  useEffect(() => {
    // Initialize auth state on mount
    setIsInitialized(true);
  }, []);

  const checkAuth = () => {
    refetchUser();
  };

  const login = async (email: string, password: string) => {
    const credentials: LoginRequest = { email, password };
    await loginMutation.mutateAsync(credentials);
  };

  const register = async (userData: RegisterRequest) => {
    await registerMutation.mutateAsync(userData);
  };

  const logout = async () => {
    await logoutMutation.mutateAsync();
  };

  const value = {
    user: user || null,
    isAuthenticated,
    isLoading,
    checkAuth,
    login,
    register,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuthContext() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuthContext must be used within an AuthProvider');
  }
  return context;
}
