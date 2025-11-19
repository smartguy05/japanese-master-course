/**
 * useSettings Hook
 *
 * Handles user settings and preferences
 */

'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { settingsAPI } from '@/services/api';
import type { UserSettings } from '@/lib/types';
import toast from 'react-hot-toast';

export function useSettings() {
  const queryClient = useQueryClient();

  // Fetch settings
  const {
    data: settings,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['settings'],
    queryFn: settingsAPI.get,
  });

  // Update settings mutation
  const updateMutation = useMutation({
    mutationFn: (updates: Partial<UserSettings>) => settingsAPI.update(updates),
    onSuccess: (updatedSettings) => {
      queryClient.setQueryData(['settings'], updatedSettings);
      toast.success('Settings updated successfully');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to update settings');
    },
  });

  // Update password mutation
  const updatePasswordMutation = useMutation({
    mutationFn: ({
      currentPassword,
      newPassword,
    }: {
      currentPassword: string;
      newPassword: string;
    }) => settingsAPI.updatePassword(currentPassword, newPassword),
    onSuccess: () => {
      toast.success('Password updated successfully');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to update password');
    },
  });

  // Delete account mutation
  const deleteAccountMutation = useMutation({
    mutationFn: settingsAPI.deleteAccount,
    onSuccess: () => {
      toast.success('Account deleted successfully');
      queryClient.clear();
      // Redirect handled by logout
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to delete account');
    },
  });

  return {
    settings,
    isLoading,
    error,
    updateSettings: updateMutation.mutate,
    isUpdatingSettings: updateMutation.isPending,
    updatePassword: updatePasswordMutation.mutate,
    isUpdatingPassword: updatePasswordMutation.isPending,
    deleteAccount: deleteAccountMutation.mutate,
    isDeletingAccount: deleteAccountMutation.isPending,
  };
}
