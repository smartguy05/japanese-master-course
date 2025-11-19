/**
 * useAuth Hook
 *
 * Handles authentication state and operations
 */

'use client';

import { useEffect } from 'react';
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { useRouter } from 'next/navigation';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { authAPI } from '@/services/api';
import type { User, LoginCredentials, RegisterData, AuthResponse } from '@/lib/types';
import toast from 'react-hot-toast';

interface AuthStore {
  user: User | null;
  isAuthenticated: boolean;
  setUser: (user: User | null) => void;
  clearUser: () => void;
}

// Zustand store for auth state
export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      clearUser: () => set({ user: null, isAuthenticated: false }),
    }),
    {
      name: 'auth-storage',
    }
  )
);

export function useAuth() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user, isAuthenticated, setUser, clearUser } = useAuthStore();

  // Fetch current user
  const { data: fetchedUser, isLoading: isLoadingUser } = useQuery({
    queryKey: ['currentUser'],
    queryFn: authAPI.getCurrentUser,
    enabled: !!authAPI && !user,
    retry: false,
  });

  // Set user when fetched
  useEffect(() => {
    if (fetchedUser) {
      setUser(fetchedUser);
    }
  }, [fetchedUser, setUser]);

  // Login mutation
  const loginMutation = useMutation({
    mutationFn: (credentials: LoginCredentials) => authAPI.login(credentials),
    onSuccess: (data: AuthResponse) => {
      setUser(data.user);
      queryClient.setQueryData(['currentUser'], data.user);
      toast.success(`Welcome back, ${data.user.full_name}!`);
      router.push('/dashboard');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Login failed. Please check your credentials.');
    },
  });

  // Register mutation
  const registerMutation = useMutation({
    mutationFn: (data: RegisterData) => authAPI.register(data),
    onSuccess: (data: AuthResponse) => {
      setUser(data.user);
      queryClient.setQueryData(['currentUser'], data.user);
      toast.success(`Welcome, ${data.user.full_name}! Let's start learning Japanese!`);
      router.push('/dashboard');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Registration failed. Please try again.');
    },
  });

  // Logout function
  const logout = () => {
    authAPI.logout();
    clearUser();
    queryClient.clear();
    toast.success('Logged out successfully');
    router.push('/');
  };

  return {
    user,
    isAuthenticated,
    isLoading: isLoadingUser,
    login: loginMutation.mutate,
    isLoggingIn: loginMutation.isPending,
    register: registerMutation.mutate,
    isRegistering: registerMutation.isPending,
    logout,
  };
}
