"""
Spaced Repetition System (SRS) Service using SM-2 Algorithm.

This implementation follows the SuperMemo SM-2 algorithm for optimal
spacing of flashcard reviews to maximize long-term retention.

Algorithm Reference: https://www.supermemo.com/en/archives1990-2015/english/ol/sm2
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class NextReview:
    """Result of SM-2 calculation containing next review parameters."""

    interval_days: int
    ease_factor: float
    repetitions: int
    next_review_date: datetime


class SRSService:
    """
    Service for managing Spaced Repetition System operations.

    Implements the SM-2 algorithm for calculating optimal review intervals.
    """

    # SM-2 Algorithm Constants
    MIN_EASE_FACTOR = 1.3
    DEFAULT_EASE_FACTOR = 2.5
    FIRST_INTERVAL = 1
    SECOND_INTERVAL = 6

    def calculate_next_review(
        self,
        ease_factor: float,
        interval_days: int,
        repetitions: int,
        quality: int,
        review_time: Optional[datetime] = None
    ) -> NextReview:
        """
        Calculate next review parameters using SM-2 algorithm.

        The SM-2 algorithm adjusts the review interval based on the quality
        of recall, with the goal of reviewing items just before they would
        be forgotten.

        Args:
            ease_factor: Current ease factor (difficulty multiplier)
            interval_days: Current interval in days
            repetitions: Number of consecutive successful repetitions
            quality: Quality of recall (0-5)
                0: Complete blackout
                1: Incorrect response with some recall
                2: Incorrect response but easy to recall correct answer
                3: Correct with serious difficulty
                4: Correct with hesitation
                5: Perfect response
            review_time: Time of review (defaults to now)

        Returns:
            NextReview: Object containing new interval, ease factor, and next review date

        Raises:
            ValueError: If quality is not in range 0-5

        Example:
            >>> srs = SRSService()
            >>> result = srs.calculate_next_review(
            ...     ease_factor=2.5,
            ...     interval_days=1,
            ...     repetitions=1,
            ...     quality=5
            ... )
            >>> result.interval_days
            6
        """
        # Validate quality
        if not 0 <= quality <= 5:
            raise ValueError("Quality must be between 0 and 5")

        if review_time is None:
            review_time = datetime.utcnow()

        # Calculate new ease factor using SM-2 formula
        # EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        new_ease_factor = ease_factor + (
            0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
        )

        # Clamp ease factor to minimum only (SM-2 has no upper limit)
        new_ease_factor = max(self.MIN_EASE_FACTOR, new_ease_factor)

        # Determine new interval and repetitions based on quality
        if quality < 3:
            # Incorrect answer - reset to beginning
            new_interval = self.FIRST_INTERVAL
            new_repetitions = 0
        else:
            # Correct answer - increase interval
            new_repetitions = repetitions + 1

            if repetitions == 0:
                # First successful review
                new_interval = self.FIRST_INTERVAL
            elif repetitions == 1:
                # Second successful review
                new_interval = self.SECOND_INTERVAL
            else:
                # Subsequent reviews: scale by OLD ease factor
                # (interval is calculated before EF update in SM-2)
                new_interval = int(interval_days * ease_factor)

        # Calculate next review date
        next_review_date = review_time + timedelta(days=new_interval)

        return NextReview(
            interval_days=new_interval,
            ease_factor=new_ease_factor,
            repetitions=new_repetitions,
            next_review_date=next_review_date
        )

    async def get_due_cards(
        self,
        db: AsyncSession,
        user_id: UUID,
        limit: int = 20,
        current_time: Optional[datetime] = None
    ) -> list[dict]:
        """
        Get flashcards due for review.

        Args:
            db: Database session
            user_id: User ID
            limit: Maximum number of cards to return
            current_time: Current time (defaults to now)

        Returns:
            List of flashcard dictionaries with content joined

        Example:
            >>> cards = await srs_service.get_due_cards(db, user_id, limit=10)
            >>> len(cards)
            10
        """
        from app.models.flashcard import Flashcard

        if current_time is None:
            current_time = datetime.utcnow()

        # Query flashcards due for review
        query = (
            select(Flashcard)
            .where(
                and_(
                    Flashcard.user_id == user_id,
                    Flashcard.next_review <= current_time
                )
            )
            .order_by(Flashcard.next_review)
            .limit(limit)
        )

        result = await db.execute(query)
        flashcards = result.scalars().all()

        return [self._flashcard_to_dict(card) for card in flashcards]

    async def record_review(
        self,
        db: AsyncSession,
        flashcard_id: UUID,
        user_id: UUID,
        quality: int,
        time_spent: int = 0,
        review_time: Optional[datetime] = None
    ) -> NextReview:
        """
        Record a flashcard review and update SRS parameters.

        Args:
            db: Database session
            flashcard_id: Flashcard ID
            user_id: User ID
            quality: Quality of recall (0-5)
            time_spent: Time spent reviewing in seconds
            review_time: Time of review (defaults to now)

        Returns:
            NextReview: New review parameters

        Raises:
            ValueError: If flashcard not found or doesn't belong to user

        Example:
            >>> result = await srs_service.record_review(
            ...     db, flashcard_id, user_id, quality=4, time_spent=15
            ... )
            >>> result.interval_days
            25
        """
        from app.models.flashcard import Flashcard
        from app.models.review import ReviewHistory

        if review_time is None:
            review_time = datetime.utcnow()

        # Get flashcard
        query = select(Flashcard).where(
            and_(
                Flashcard.id == flashcard_id,
                Flashcard.user_id == user_id
            )
        )
        result = await db.execute(query)
        flashcard = result.scalar_one_or_none()

        if not flashcard:
            raise ValueError("Flashcard not found or does not belong to user")

        # Calculate next review using SM-2
        next_review = self.calculate_next_review(
            ease_factor=flashcard.ease_factor,
            interval_days=flashcard.interval_days,
            repetitions=flashcard.repetitions,
            quality=quality,
            review_time=review_time
        )

        # Update flashcard
        flashcard.ease_factor = next_review.ease_factor
        flashcard.interval_days = next_review.interval_days
        flashcard.repetitions = next_review.repetitions
        flashcard.last_reviewed = review_time
        flashcard.next_review = next_review.next_review_date

        # Update counters
        if quality >= 3:
            flashcard.correct_count += 1
        else:
            flashcard.incorrect_count += 1

        # Create review history entry
        review_history = ReviewHistory(
            flashcard_id=flashcard_id,
            user_id=user_id,
            quality=quality,
            time_spent=time_spent,
            reviewed_at=review_time
        )
        db.add(review_history)

        await db.commit()
        await db.refresh(flashcard)

        return next_review

    async def get_review_stats(
        self,
        db: AsyncSession,
        user_id: UUID,
        period_days: int = 30
    ) -> dict:
        """
        Get user review statistics for a period.

        Args:
            db: Database session
            user_id: User ID
            period_days: Number of days to analyze

        Returns:
            Dictionary with stats:
                - total_reviews: Total reviews in period
                - accuracy: Percentage of correct reviews (quality >= 3)
                - avg_quality: Average quality score
                - cards_due_today: Number of cards due today
                - total_cards: Total flashcards

        Example:
            >>> stats = await srs_service.get_review_stats(db, user_id)
            >>> stats['accuracy']
            0.85
        """
        from app.models.flashcard import Flashcard
        from app.models.review import ReviewHistory

        current_time = datetime.utcnow()
        period_start = current_time - timedelta(days=period_days)

        # Total reviews in period
        query = select(func.count(ReviewHistory.id)).where(
            and_(
                ReviewHistory.user_id == user_id,
                ReviewHistory.reviewed_at >= period_start
            )
        )
        result = await db.execute(query)
        total_reviews = result.scalar_one() or 0

        # Correct reviews (quality >= 3)
        query = select(func.count(ReviewHistory.id)).where(
            and_(
                ReviewHistory.user_id == user_id,
                ReviewHistory.reviewed_at >= period_start,
                ReviewHistory.quality >= 3
            )
        )
        result = await db.execute(query)
        correct_reviews = result.scalar_one() or 0

        # Average quality
        query = select(func.avg(ReviewHistory.quality)).where(
            and_(
                ReviewHistory.user_id == user_id,
                ReviewHistory.reviewed_at >= period_start
            )
        )
        result = await db.execute(query)
        avg_quality = result.scalar_one() or 0.0

        # Cards due today
        query = select(func.count(Flashcard.id)).where(
            and_(
                Flashcard.user_id == user_id,
                Flashcard.next_review <= current_time
            )
        )
        result = await db.execute(query)
        cards_due_today = result.scalar_one() or 0

        # Total cards
        query = select(func.count(Flashcard.id)).where(
            Flashcard.user_id == user_id
        )
        result = await db.execute(query)
        total_cards = result.scalar_one() or 0

        # Calculate accuracy
        accuracy = (correct_reviews / total_reviews) if total_reviews > 0 else 0.0

        return {
            "total_reviews": total_reviews,
            "correct_reviews": correct_reviews,
            "accuracy": round(accuracy, 3),
            "avg_quality": round(float(avg_quality), 2),
            "cards_due_today": cards_due_today,
            "total_cards": total_cards,
            "period_days": period_days
        }

    def _flashcard_to_dict(self, flashcard) -> dict:
        """Convert flashcard model to dictionary."""
        return {
            "id": str(flashcard.id),
            "content_type": flashcard.content_type,
            "content_id": str(flashcard.content_id),
            "ease_factor": flashcard.ease_factor,
            "interval_days": flashcard.interval_days,
            "repetitions": flashcard.repetitions,
            "last_reviewed": flashcard.last_reviewed,
            "next_review": flashcard.next_review,
            "correct_count": flashcard.correct_count,
            "incorrect_count": flashcard.incorrect_count,
            "created_at": flashcard.created_at
        }
