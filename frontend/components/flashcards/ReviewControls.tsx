/**
 * ReviewControls Component
 *
 * Rating buttons for flashcard review (1-5 quality scale)
 */

'use client';

import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface ReviewControlsProps {
  onRate: (quality: 1 | 2 | 3 | 4 | 5) => void;
  disabled?: boolean;
}

const ratings = [
  { quality: 1 as const, label: 'Again', color: 'bg-red-500 hover:bg-red-600', key: '1' },
  { quality: 2 as const, label: 'Hard', color: 'bg-orange-500 hover:bg-orange-600', key: '2' },
  { quality: 3 as const, label: 'Good', color: 'bg-yellow-500 hover:bg-yellow-600', key: '3' },
  { quality: 4 as const, label: 'Easy', color: 'bg-green-500 hover:bg-green-600', key: '4' },
  { quality: 5 as const, label: 'Perfect', color: 'bg-blue-500 hover:bg-blue-600', key: '5' },
];

export function ReviewControls({ onRate, disabled }: ReviewControlsProps) {
  // Handle keyboard shortcuts
  const handleKeyDown = (e: KeyboardEvent) => {
    if (disabled) return;
    const key = e.key;
    const rating = ratings.find((r) => r.key === key);
    if (rating) {
      onRate(rating.quality);
    }
  };

  // Add keyboard event listener
  if (typeof window !== 'undefined') {
    window.addEventListener('keydown', handleKeyDown);
  }

  return (
    <div className="flex flex-col gap-4 w-full max-w-2xl mx-auto" data-testid="review-controls">
      <div className="flex gap-2 justify-center">
        {ratings.map((rating) => (
          <Button
            key={rating.quality}
            onClick={() => onRate(rating.quality)}
            disabled={disabled}
            className={cn(
              'flex-1 text-white font-semibold py-6',
              rating.color
            )}
            data-testid={`rate-${rating.quality}`}
          >
            <div className="flex flex-col items-center">
              <span className="text-lg">{rating.label}</span>
              <span className="text-xs opacity-75">({rating.key})</span>
            </div>
          </Button>
        ))}
      </div>
      <p className="text-xs text-center text-muted-foreground">
        Use keyboard shortcuts (1-5) for faster reviews
      </p>
    </div>
  );
}
