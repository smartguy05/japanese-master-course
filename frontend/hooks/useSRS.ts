/**
 * Spaced Repetition System (SRS) Hook
 * 
 * Implements SM-2 algorithm for optimal review scheduling
 * Based on SuperMemo 2 algorithm
 */

import { useState, useCallback } from 'react';

export interface SRSCard {
  id: string;
  easeFactor: number;
  interval: number;
  repetitions: number;
  nextReview: Date;
}

export interface ReviewResult {
  nextReview: Date;
  interval: number;
  easeFactor: number;
  repetitions: number;
}

/**
 * Calculate next review date based on SM-2 algorithm
 * @param card - Current card state
 * @param quality - Answer quality (0-5, where 3+ is correct)
 * @returns Updated card state
 */
export function calculateNextReview(
  card: SRSCard,
  quality: number
): ReviewResult {
  let { easeFactor, interval, repetitions } = card;

  if (quality >= 3) {
    // Correct answer
    if (repetitions === 0) {
      interval = 1;
    } else if (repetitions === 1) {
      interval = 6;
    } else {
      interval = Math.round(interval * easeFactor);
    }
    repetitions += 1;
  } else {
    // Incorrect answer
    repetitions = 0;
    interval = 1;
  }

  // Update ease factor
  easeFactor = easeFactor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02));
  easeFactor = Math.max(1.3, easeFactor); // Minimum ease factor

  const nextReview = new Date();
  nextReview.setDate(nextReview.getDate() + interval);

  return {
    nextReview,
    interval,
    easeFactor,
    repetitions,
  };
}

export function useSRS() {
  const [cards, setCards] = useState<Map<string, SRSCard>>(new Map());

  const recordAnswer = useCallback((cardId: string, quality: number) => {
    setCards((prevCards) => {
      const newCards = new Map(prevCards);
      const card = newCards.get(cardId);
      
      if (!card) {
        console.warn(`Card ${cardId} not found`);
        return prevCards;
      }

      const result = calculateNextReview(card, quality);
      
      newCards.set(cardId, {
        ...card,
        ...result,
      });

      return newCards;
    });
  }, []);

  const getDueCards = useCallback(() => {
    const now = new Date();
    return Array.from(cards.values()).filter(
      (card) => card.nextReview <= now
    );
  }, [cards]);

  return {
    cards,
    recordAnswer,
    getDueCards,
  };
}
