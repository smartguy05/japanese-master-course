import { calculateNextReview } from '@/hooks/useSRS';

describe('SRS Algorithm', () => {
  const mockCard = {
    id: 'test-1',
    easeFactor: 2.5,
    interval: 1,
    repetitions: 0,
    nextReview: new Date(),
  };

  describe('calculateNextReview', () => {
    it('should increase interval on correct answer after first repetition', () => {
      const cardWithProgress = {
        ...mockCard,
        repetitions: 2,
        interval: 6,
      };

      const result = calculateNextReview(cardWithProgress, 4);

      expect(result.interval).toBeGreaterThan(cardWithProgress.interval);
      expect(result.repetitions).toBe(3);
    });

    it('should reset interval on incorrect answer (quality < 3)', () => {
      const cardWithProgress = {
        ...mockCard,
        repetitions: 5,
        interval: 30,
      };
      
      const result = calculateNextReview(cardWithProgress, 2);
      
      expect(result.interval).toBe(1);
      expect(result.repetitions).toBe(0);
    });

    it('should maintain ease factor above minimum (1.3)', () => {
      const result = calculateNextReview(mockCard, 0);
      
      expect(result.easeFactor).toBeGreaterThanOrEqual(1.3);
    });

    it('should set interval to 1 day for first repetition', () => {
      const result = calculateNextReview(mockCard, 4);
      
      expect(result.interval).toBe(1);
      expect(result.repetitions).toBe(1);
    });

    it('should set interval to 6 days for second repetition', () => {
      const cardSecondRep = {
        ...mockCard,
        repetitions: 1,
        interval: 1,
      };
      
      const result = calculateNextReview(cardSecondRep, 4);
      
      expect(result.interval).toBe(6);
      expect(result.repetitions).toBe(2);
    });

    it('should calculate next review date correctly', () => {
      const result = calculateNextReview(mockCard, 4);
      const now = new Date();
      const expectedDate = new Date(now);
      expectedDate.setDate(expectedDate.getDate() + result.interval);
      
      expect(result.nextReview.getDate()).toBe(expectedDate.getDate());
    });

    it('should adjust ease factor based on answer quality', () => {
      // Quality 5 (perfect) should increase ease factor
      const perfectResult = calculateNextReview(mockCard, 5);
      expect(perfectResult.easeFactor).toBeGreaterThan(mockCard.easeFactor);
      
      // Quality 3 (barely correct) should decrease ease factor
      const barelyResult = calculateNextReview(mockCard, 3);
      expect(barelyResult.easeFactor).toBeLessThan(mockCard.easeFactor);
    });
  });
});
