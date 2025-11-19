/**
 * useProgress Hook
 *
 * Handles user progress and statistics
 */

'use client';

import { useQuery } from '@tanstack/react-query';
import { progressAPI } from '@/services/api';
import { subDays, format } from 'date-fns';

export function useProgress() {
  const {
    data: progress,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['progress'],
    queryFn: progressAPI.get,
  });

  return {
    progress,
    isLoading,
    error,
    xp: progress?.total_xp || 0,
    level: progress?.level || 1,
    currentStreak: progress?.current_streak_days || 0,
    longestStreak: progress?.longest_streak_days || 0,
    totalStudyTime: progress?.total_study_time_minutes || 0,
    lessonsCompleted: progress?.lessons_completed || 0,
    flashcardsReviewed: progress?.flashcards_reviewed || 0,
    conversationsCompleted: progress?.conversations_completed || 0,
    achievements: progress?.achievements || [],
    jlptProgress: progress?.jlpt_progress,
  };
}

export function useDailyStats(days: number = 30) {
  const endDate = new Date();
  const startDate = subDays(endDate, days);

  const {
    data: stats,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['progress', 'daily', days],
    queryFn: () =>
      progressAPI.getDailyStats(
        format(startDate, 'yyyy-MM-dd'),
        format(endDate, 'yyyy-MM-dd')
      ),
  });

  return {
    stats: stats || [],
    isLoading,
    error,
  };
}

export function useStreakData() {
  const {
    data: streakData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['progress', 'streak'],
    queryFn: progressAPI.getStreakData,
  });

  return {
    currentStreak: streakData?.current_streak || 0,
    longestStreak: streakData?.longest_streak || 0,
    streakDates: streakData?.streak_dates || [],
    isLoading,
    error,
  };
}
