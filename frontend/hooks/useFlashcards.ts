/**
 * useFlashcards Hook
 *
 * Handles flashcard review sessions and SRS operations
 */

'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { flashcardsAPI } from '@/services/api';
import type { FlashCard, ReviewRating } from '@/lib/types';
import toast from 'react-hot-toast';

export function useFlashcards(jlptLevel?: string) {
  const queryClient = useQueryClient();

  // Fetch due cards
  const {
    data: dueCards,
    isLoading: isDueCardsLoading,
    error: dueCardsError,
  } = useQuery({
    queryKey: ['flashcards', 'due'],
    queryFn: flashcardsAPI.getDueCards,
  });

  // Fetch all cards (optionally filtered by JLPT level)
  const {
    data: allCards,
    isLoading: isAllCardsLoading,
  } = useQuery({
    queryKey: ['flashcards', 'all', jlptLevel],
    queryFn: () => flashcardsAPI.getAllCards(jlptLevel),
    enabled: !!jlptLevel,
  });

  // Submit review mutation
  const reviewMutation = useMutation({
    mutationFn: (rating: ReviewRating) => flashcardsAPI.submitReview(rating),
    onSuccess: (nextReview, variables) => {
      // Update cache optimistically
      queryClient.setQueryData<FlashCard[]>(['flashcards', 'due'], (old) => {
        if (!old) return old;
        return old.filter((card) => card.id !== variables.card_id);
      });

      queryClient.invalidateQueries({ queryKey: ['flashcards'] });
      queryClient.invalidateQueries({ queryKey: ['progress'] });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to submit review');
    },
  });

  // Reset card mutation
  const resetMutation = useMutation({
    mutationFn: (cardId: string) => flashcardsAPI.resetCard(cardId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['flashcards'] });
      toast.success('Card reset successfully');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to reset card');
    },
  });

  return {
    dueCards: dueCards || [],
    dueCardsCount: dueCards?.length || 0,
    isDueCardsLoading,
    dueCardsError,
    allCards: allCards || [],
    isAllCardsLoading,
    submitReview: reviewMutation.mutate,
    isSubmittingReview: reviewMutation.isPending,
    resetCard: resetMutation.mutate,
    isResettingCard: resetMutation.isPending,
  };
}
