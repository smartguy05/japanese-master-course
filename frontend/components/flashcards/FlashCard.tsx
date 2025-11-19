/**
 * FlashCard Component
 *
 * Displays a flashcard with flip animation for SRS review
 */

'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/card';
import type { FlashCard as FlashCardType } from '@/lib/types';
import { cn } from '@/lib/utils';

interface FlashCardProps {
  card: FlashCardType;
  onFlip?: () => void;
  className?: string;
}

export function FlashCard({ card, onFlip, className }: FlashCardProps) {
  const [isFlipped, setIsFlipped] = useState(false);

  const handleFlip = () => {
    setIsFlipped(!isFlipped);
    onFlip?.();
  };

  return (
    <div
      className={cn('perspective-1000 w-full max-w-2xl mx-auto', className)}
      data-testid="flashcard"
    >
      <motion.div
        className="relative w-full h-96 cursor-pointer"
        onClick={handleFlip}
        animate={{ rotateY: isFlipped ? 180 : 0 }}
        transition={{ duration: 0.6, type: 'spring' }}
        style={{ transformStyle: 'preserve-3d' }}
      >
        {/* Front of card */}
        <Card
          className={cn(
            'absolute inset-0 flex flex-col items-center justify-center p-8 backface-hidden',
            'bg-gradient-to-br from-primary/10 to-primary/5'
          )}
          style={{ backfaceVisibility: 'hidden' }}
        >
          <div className="text-center">
            <div className="text-8xl font-bold mb-4 select-none">{card.front}</div>
            {card.reading && (
              <div className="text-2xl text-muted-foreground mb-2">{card.reading}</div>
            )}
            <div className="text-sm text-muted-foreground mt-8">
              Click to reveal answer
            </div>
          </div>
        </Card>

        {/* Back of card */}
        <Card
          className={cn(
            'absolute inset-0 flex flex-col items-center justify-center p-8 backface-hidden',
            'bg-gradient-to-br from-secondary/10 to-secondary/5'
          )}
          style={{
            backfaceVisibility: 'hidden',
            transform: 'rotateY(180deg)',
          }}
        >
          <div className="text-center">
            <div className="text-6xl font-bold mb-4">{card.back}</div>
            {card.meaning && (
              <div className="text-3xl text-muted-foreground mb-4">{card.meaning}</div>
            )}
            {card.reading && (
              <div className="text-xl text-muted-foreground mt-2">({card.reading})</div>
            )}
            <div className="mt-8 space-y-2">
              <div className="text-sm text-muted-foreground">
                Type: {card.type} • Level: {card.jlpt_level}
              </div>
              <div className="text-xs text-muted-foreground">
                Interval: {card.interval_days} days • Reviews: {card.repetitions}
              </div>
            </div>
          </div>
        </Card>
      </motion.div>
    </div>
  );
}
