/**
 * useLessons Hook
 *
 * Handles lesson fetching and progress tracking
 */

'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { lessonsAPI } from '@/services/api';
import type { Lesson, LessonProgress } from '@/lib/types';
import toast from 'react-hot-toast';

interface UseLessonsParams {
  level?: string;
  type?: string;
  page?: number;
  perPage?: number;
}

export function useLessons(params?: UseLessonsParams) {
  const queryClient = useQueryClient();

  // Fetch all lessons
  const {
    data: lessonsData,
    isLoading: isLessonsLoading,
    error: lessonsError,
  } = useQuery({
    queryKey: ['lessons', params],
    queryFn: () => lessonsAPI.getAll(params),
  });

  return {
    lessons: lessonsData?.data || [],
    totalLessons: lessonsData?.total || 0,
    currentPage: lessonsData?.page || 1,
    totalPages: lessonsData?.total_pages || 1,
    isLessonsLoading,
    lessonsError,
  };
}

export function useLesson(lessonId: string) {
  const queryClient = useQueryClient();

  // Fetch single lesson
  const {
    data: lesson,
    isLoading: isLessonLoading,
    error: lessonError,
  } = useQuery({
    queryKey: ['lessons', lessonId],
    queryFn: () => lessonsAPI.getById(lessonId),
    enabled: !!lessonId,
  });

  // Fetch lesson progress
  const {
    data: progress,
    isLoading: isProgressLoading,
  } = useQuery({
    queryKey: ['lessons', lessonId, 'progress'],
    queryFn: () => lessonsAPI.getProgress(lessonId),
    enabled: !!lessonId,
  });

  // Submit exercise answer
  const submitExerciseMutation = useMutation({
    mutationFn: ({
      exerciseId,
      answer,
    }: {
      exerciseId: string;
      answer: string | string[];
    }) => lessonsAPI.submitExercise(lessonId, exerciseId, answer),
    onSuccess: (result) => {
      if (result.correct) {
        toast.success('Correct! ' + result.explanation);
      } else {
        toast.error('Incorrect. ' + result.explanation);
      }
      queryClient.invalidateQueries({ queryKey: ['lessons', lessonId, 'progress'] });
      queryClient.invalidateQueries({ queryKey: ['progress'] });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to submit answer');
    },
  });

  // Complete lesson
  const completeLessonMutation = useMutation({
    mutationFn: () => lessonsAPI.completeLesson(lessonId),
    onSuccess: () => {
      toast.success('Lesson completed! Great job!');
      queryClient.invalidateQueries({ queryKey: ['lessons'] });
      queryClient.invalidateQueries({ queryKey: ['progress'] });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to complete lesson');
    },
  });

  return {
    lesson,
    isLessonLoading,
    lessonError,
    progress,
    isProgressLoading,
    submitExercise: submitExerciseMutation.mutate,
    isSubmittingExercise: submitExerciseMutation.isPending,
    completeLesson: completeLessonMutation.mutate,
    isCompletingLesson: completeLessonMutation.isPending,
  };
}
