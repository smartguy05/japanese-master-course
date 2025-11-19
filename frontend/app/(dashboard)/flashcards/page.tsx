/**
 * Flashcards Page
 *
 * SRS flashcard review session
 */

'use client';

import { useState, useEffect } from 'react';
import { FlashCard } from '@/components/flashcards/FlashCard';
import { ReviewControls } from '@/components/flashcards/ReviewControls';
import { ProgressRing } from '@/components/progress/ProgressRing';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useFlashcards } from '@/hooks/useFlashcards';
import { ArrowLeft, CheckCircle2, Timer } from 'lucide-react';
import Link from 'next/link';
import { motion } from 'framer-motion';

export default function FlashcardsPage() {
  const { dueCards, submitReview, isSubmittingReview } = useFlashcards();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [reviewedCount, setReviewedCount] = useState(0);
  const [correctCount, setCorrectCount] = useState(0);
  const [isRevealed, setIsRevealed] = useState(false);
  const [startTime, setStartTime] = useState(Date.now());
  const [sessionTime, setSessionTime] = useState(0);

  const currentCard = dueCards[currentIndex];
  const isComplete = currentIndex >= dueCards.length;
  const progress = dueCards.length > 0 ? ((reviewedCount / dueCards.length) * 100) : 0;

  // Timer
  useEffect(() => {
    const interval = setInterval(() => {
      setSessionTime(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);

    return () => clearInterval(interval);
  }, [startTime]);

  const handleRate = (quality: 1 | 2 | 3 | 4 | 5) => {
    if (!currentCard || isSubmittingReview) return;

    const timeSpent = Math.floor((Date.now() - startTime) / 1000);

    submitReview(
      {
        card_id: currentCard.id,
        quality,
        time_spent_seconds: timeSpent,
      },
      {
        onSuccess: () => {
          setReviewedCount(reviewedCount + 1);
          if (quality >= 3) {
            setCorrectCount(correctCount + 1);
          }
          setCurrentIndex(currentIndex + 1);
          setIsRevealed(false);
          setStartTime(Date.now());
        },
      }
    );
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (dueCards.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <CheckCircle2 className="w-16 h-16 text-green-500 mb-4" />
        <h2 className="text-2xl font-bold mb-2">All caught up!</h2>
        <p className="text-muted-foreground mb-8">
          No flashcards due for review right now. Great work!
        </p>
        <Button asChild>
          <Link href="/dashboard">Return to Dashboard</Link>
        </Button>
      </div>
    );
  }

  if (isComplete) {
    const accuracy = (correctCount / reviewedCount) * 100;

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="flex flex-col items-center justify-center min-h-[60vh]"
      >
        <div className="text-center mb-8">
          <CheckCircle2 className="w-20 h-20 text-green-500 mx-auto mb-4" />
          <h2 className="text-3xl font-bold mb-2">Session Complete!</h2>
          <p className="text-muted-foreground">Excellent work on your review session!</p>
        </div>

        <Card className="w-full max-w-md mb-8">
          <CardContent className="pt-6">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground">Cards Reviewed</span>
                <span className="text-2xl font-bold">{reviewedCount}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground">Accuracy</span>
                <span className="text-2xl font-bold text-green-500">
                  {accuracy.toFixed(0)}%
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground">Time Spent</span>
                <span className="text-2xl font-bold">{formatTime(sessionTime)}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="flex gap-4">
          <Button variant="outline" asChild>
            <Link href="/dashboard">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Dashboard
            </Link>
          </Button>
          <Button onClick={() => window.location.reload()}>Review Again</Button>
        </div>
      </motion.div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Flashcard Review</h1>
          <p className="text-muted-foreground mt-1">
            Card {currentIndex + 1} of {dueCards.length}
          </p>
        </div>
        <Button variant="ghost" asChild>
          <Link href="/dashboard">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Exit
          </Link>
        </Button>
      </div>

      {/* Progress Stats */}
      <div className="grid grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6 text-center">
            <ProgressRing progress={progress} size={80} strokeWidth={6} />
            <p className="text-sm text-muted-foreground mt-2">Progress</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 text-center">
            <div className="text-3xl font-bold">{correctCount}/{reviewedCount}</div>
            <p className="text-sm text-muted-foreground mt-2">Correct</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 text-center">
            <div className="flex items-center justify-center gap-2">
              <Timer className="w-5 h-5" />
              <span className="text-3xl font-bold">{formatTime(sessionTime)}</span>
            </div>
            <p className="text-sm text-muted-foreground mt-2">Time</p>
          </CardContent>
        </Card>
      </div>

      {/* Flashcard */}
      <div className="py-8">
        {currentCard && (
          <FlashCard
            card={currentCard}
            onFlip={() => setIsRevealed(true)}
          />
        )}
      </div>

      {/* Review Controls */}
      {isRevealed && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <ReviewControls
            onRate={handleRate}
            disabled={isSubmittingReview}
          />
        </motion.div>
      )}

      {!isRevealed && (
        <div className="text-center text-muted-foreground">
          Click the card to reveal the answer
        </div>
      )}
    </div>
  );
}
